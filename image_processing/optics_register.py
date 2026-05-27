"""
optics_register.py  –  Phase 2: Multi-image registration
                        Aligns a set of optics-table photos to a common
                        reference frame and fuses their detections.

Usage:
    python optics_register.py <image1> <image2> [<image3> ...] [--debug] [--out-dir DIR]

Pipeline:
    1. Load all images, detect breadboard holes + grid in each
    2. Score each image for "flatness" (how rectilinear its grid looks)
       → pick the flattest as the reference frame
    3. SIFT feature matching between every image and the reference
       → RANSAC homography  (H: other → reference)
    4. Optionally refine H using matched grid hole positions
    5. Warp all images into reference space, fuse into a composite
    6. Run OCR on the composite (better angles averaged in)
    7. Output fused JSON map + SVG + composite image

Outputs (in --out-dir, default ./optics_output):
    fused_composite.jpg   – warped frames blended together
    fused_map.json        – component grid map
    fused_map.svg         – annotated SVG
    registration.json     – per-image homographies + scores
    *_warped.jpg          – individual warped frames (with --debug)
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

# Re-use Phase 1 helpers
sys.path.insert(0, str(Path(__file__).parent))
from optics_mapper import (
    detect_breadboard_holes,
    read_labels,
    cluster_labels_into_components,
    build_svg,
    save_debug_image,
    pixel_to_grid,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. IMAGE LOADING & PER-FRAME ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

MAX_DIM = 1600  # Working resolution – large enough for SIFT, small enough to be fast


def load_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Cannot read image: {path}")
    h, w = img.shape[:2]
    scale = min(1.0, MAX_DIM / max(h, w))
    if scale < 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_AREA)
    return img


def analyse_frame(img_bgr: np.ndarray, name: str) -> dict:
    """
    Detect grid, compute flatness score, extract SIFT keypoints.
    Returns a frame-info dict.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    holes, grid_info = detect_breadboard_holes(gray)

    flatness = _flatness_score(holes, grid_info) if holes is not None else 0.0

    # SIFT keypoints & descriptors (on contrast-enhanced gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    sift = cv2.SIFT_create(nfeatures=4000)
    kps, descs = sift.detectAndCompute(eq, None)

    return {
        "name": name,
        "img": img_bgr,
        "gray": gray,
        "holes": holes,
        "grid_info": grid_info,
        "flatness": flatness,
        "keypoints": kps,
        "descriptors": descs,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. FLATNESS SCORING
#    A perfectly top-down photo of a square grid has:
#      • NN distances all equal  (low variance)
#      • NN angle distribution bimodal at 0° and 90°
#    Perspective distortion breaks both properties.
# ─────────────────────────────────────────────────────────────────────────────

def _flatness_score(holes: np.ndarray, grid_info: dict) -> float:
    """
    Returns a score in [0, 1]: 1.0 = perfectly top-down, 0.0 = heavily tilted.
    Uses two criteria:
      A) Uniformity of nearest-neighbour distances (low CoV → flat)
      B) Orthogonality of dominant grid directions (close to 90° → flat)
    """
    if holes is None or len(holes) < 16:
        return 0.0

    from scipy.spatial import KDTree
    tree = KDTree(holes)
    dists, idxs = tree.query(holes, k=5)

    # ── A: Distance uniformity ──
    nn = dists[:, 1]
    cov = np.std(nn) / (np.mean(nn) + 1e-6)          # coefficient of variation
    score_dist = float(np.exp(-3.0 * cov))            # 1.0 when cov=0

    # ── B: Orthogonality of dominant axes ──
    vectors = []
    for i in range(len(holes)):
        for j in range(1, 5):
            v = holes[idxs[i, j]] - holes[i]
            if np.linalg.norm(v) > 0:
                vectors.append(v)
    vectors = np.array(vectors)
    angles = np.degrees(np.arctan2(vectors[:, 1], vectors[:, 0])) % 180.0

    # Find two dominant angles
    hist, edges = np.histogram(angles, bins=180, range=(0, 180))
    # Smooth histogram
    hist = np.convolve(hist, np.ones(5) / 5, mode='same')
    peaks = _find_two_peaks(hist)
    if peaks is not None:
        a1, a2 = edges[peaks[0]], edges[peaks[1]]
        delta = abs(abs(a1 - a2) - 90.0)             # deviation from 90°
        score_ortho = float(np.exp(-0.05 * delta))    # 1.0 when delta=0
    else:
        score_ortho = 0.3

    score = 0.5 * score_dist + 0.5 * score_ortho
    return round(float(score), 4)


def _find_two_peaks(hist: np.ndarray):
    """Return indices of the two highest non-adjacent peaks in a histogram."""
    order = np.argsort(hist)[::-1]
    peaks = []
    for idx in order:
        if all(abs(idx - p) > 10 for p in peaks):
            peaks.append(idx)
        if len(peaks) == 2:
            return peaks
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 3. PAIRWISE HOMOGRAPHY ESTIMATION
# ─────────────────────────────────────────────────────────────────────────────

MIN_MATCHES = 20  # Minimum good SIFT matches to attempt homography


def estimate_homography(src_frame: dict, dst_frame: dict,
                        debug: bool = False) -> Optional[np.ndarray]:
    """
    Estimate homography H such that:   dst_pts ≈ H @ src_pts
    (i.e. warping src into dst's coordinate space)

    Uses SIFT + FLANN matching + RANSAC.
    Returns H (3×3 float64) or None if estimation failed.
    """
    descs_src = src_frame["descriptors"]
    descs_dst = dst_frame["descriptors"]

    if descs_src is None or descs_dst is None:
        return None
    if len(descs_src) < MIN_MATCHES or len(descs_dst) < MIN_MATCHES:
        return None

    # FLANN matcher
    index_params = dict(algorithm=1, trees=5)   # FLANN_INDEX_KDTREE
    search_params = dict(checks=100)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    try:
        matches = flann.knnMatch(descs_src, descs_dst, k=2)
    except cv2.error:
        return None

    # Lowe's ratio test
    good = [m for m, n in matches if m.distance < 0.72 * n.distance]

    if len(good) < MIN_MATCHES:
        print(f"    ✗ Only {len(good)} good matches between "
              f"'{src_frame['name']}' → '{dst_frame['name']}' (need {MIN_MATCHES})")
        return None

    kps_src = src_frame["keypoints"]
    kps_dst = dst_frame["keypoints"]

    src_pts = np.float32([kps_src[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kps_dst[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,
                                 ransacReprojThreshold=4.0,
                                 confidence=0.995,
                                 maxIters=5000)

    if H is None:
        return None

    inliers = int(mask.sum())
    inlier_ratio = inliers / len(good)
    print(f"    ✓ {inliers}/{len(good)} inliers ({inlier_ratio:.0%})  "
          f"'{src_frame['name']}' → '{dst_frame['name']}'")

    if inlier_ratio < 0.25 or inliers < MIN_MATCHES:
        print(f"    ✗ Homography rejected (low inlier ratio)")
        return None

    # Sanity check: H should not be degenerate
    if not _homography_is_sane(H, src_frame["img"].shape):
        print(f"    ✗ Homography rejected (degenerate transform)")
        return None

    return H


def _homography_is_sane(H: np.ndarray, shape: tuple) -> bool:
    """
    Reject degenerate homographies by checking that the four image corners
    map to a convex quadrilateral with reasonable area.
    """
    h, w = shape[:2]
    corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    warped = cv2.perspectiveTransform(corners, H).reshape(-1, 2)

    # Must be convex
    hull = cv2.convexHull(warped.astype(np.float32))
    if len(hull) < 4:
        return False

    # Area should be between 0.1× and 10× of original
    orig_area = w * h
    warped_area = float(cv2.contourArea(hull))
    ratio = warped_area / (orig_area + 1e-6)
    return 0.1 < ratio < 10.0


# ─────────────────────────────────────────────────────────────────────────────
# 4. GRID-GUIDED HOMOGRAPHY REFINEMENT
#    If both frames have detected holes, use matched hole pairs to refine H.
#    Grid holes are more reliable anchors than arbitrary SIFT features.
# ─────────────────────────────────────────────────────────────────────────────

def refine_with_grid(H_init: np.ndarray,
                     src_frame: dict, dst_frame: dict) -> np.ndarray:
    """
    Attempt to refine H using matched breadboard hole positions.
    Falls back to H_init if not enough holes are matched.
    """
    src_holes = src_frame.get("holes")
    dst_holes = dst_frame.get("holes")

    if src_holes is None or dst_holes is None:
        return H_init
    if len(src_holes) < 9 or len(dst_holes) < 9:
        return H_init

    # Project src holes through H_init into dst space
    src_pts = src_holes.reshape(-1, 1, 2).astype(np.float32)
    projected = cv2.perspectiveTransform(src_pts, H_init).reshape(-1, 2)

    # For each projected point, find nearest actual hole in dst
    from scipy.spatial import KDTree
    dst_pitch = dst_frame["grid_info"].get("pitch_px", 40)
    tree = KDTree(dst_holes)
    dists, idxs = tree.query(projected, k=1)

    # Keep pairs within half a pitch (genuine correspondences)
    threshold = dst_pitch * 0.5
    mask = dists < threshold
    if mask.sum() < 8:
        return H_init  # not enough matched holes

    matched_src = src_holes[mask].astype(np.float32)
    matched_dst = dst_holes[idxs[mask]].astype(np.float32)

    H_refined, inlier_mask = cv2.findHomography(
        matched_src.reshape(-1, 1, 2),
        matched_dst.reshape(-1, 1, 2),
        cv2.RANSAC,
        ransacReprojThreshold=dst_pitch * 0.3,
    )

    if H_refined is None or not _homography_is_sane(H_refined, src_frame["img"].shape):
        return H_init

    n_inliers = int(inlier_mask.sum())
    print(f"    ↳ Grid refinement: {n_inliers}/{mask.sum()} hole pairs used")
    return H_refined


# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPOSITE FUSION
#    Warp all registered frames into reference space and blend.
# ─────────────────────────────────────────────────────────────────────────────

def fuse_frames(ref_frame: dict,
                other_frames: list,
                homographies: dict,
                out_dir: Path,
                debug: bool = False) -> np.ndarray:
    """
    Warp all frames into the reference frame's coordinate space.
    Uses a weighted blend: pixels from frames with lower viewing angle
    (higher flatness score) get more weight in the final composite.

    Returns the fused composite as a BGR ndarray.
    """
    ref_img = ref_frame["img"]
    h_ref, w_ref = ref_img.shape[:2]

    # Accumulate weighted sum
    acc = np.zeros((h_ref, w_ref, 3), dtype=np.float64)
    weight_acc = np.zeros((h_ref, w_ref, 1), dtype=np.float64)

    # Reference frame contributes with its flatness score as weight
    ref_weight = max(ref_frame["flatness"], 0.5)
    acc += ref_img.astype(np.float64) * ref_weight
    weight_acc += ref_weight

    for frame in other_frames:
        name = frame["name"]
        H = homographies.get(name)
        if H is None:
            print(f"  ⚠ Skipping '{name}' – no valid homography")
            continue

        warped = cv2.warpPerspective(
            frame["img"], H, (w_ref, h_ref),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )

        # Mask: only blend pixels that were actually filled
        warp_mask = cv2.warpPerspective(
            np.ones(frame["img"].shape[:2], dtype=np.float32),
            H, (w_ref, h_ref),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )[:, :, np.newaxis]

        w = max(frame["flatness"], 0.1)
        acc += warped.astype(np.float64) * warp_mask * w
        weight_acc += warp_mask * w

        if debug:
            dbg_path = out_dir / f"{name}_warped.jpg"
            cv2.imwrite(str(dbg_path), warped)
            print(f"    Warped frame saved → {dbg_path}")

    # Normalise
    safe_weight = np.where(weight_acc > 0, weight_acc, 1.0)
    composite = (acc / safe_weight).clip(0, 255).astype(np.uint8)
    return composite


# ─────────────────────────────────────────────────────────────────────────────
# 6. CROSS-FRAME DETECTION MERGING
#    Run OCR on the composite + optionally on individual warped frames,
#    then merge component detections using grid coordinates.
# ─────────────────────────────────────────────────────────────────────────────

def merge_detections(composite: np.ndarray,
                     ref_grid_info: dict,
                     ref_frame: dict,
                     other_frames: list,
                     homographies: dict) -> list:
    """
    Strategy:
      1. Run OCR on the composite image (benefits from multi-view averaging)
      2. For each other frame, warp its detected labels into reference space
         and add them to the candidate pool
      3. Cluster all candidates by grid position, pick best text per cluster
    """
    print("\n  Running OCR on fused composite…")
    composite_labels = read_labels(composite)
    print(f"  → {len(composite_labels)} text regions in composite")

    all_labels = list(composite_labels)

    # Also gather labels from individual frames (warped into ref space)
    for frame in other_frames:
        H = homographies.get(frame["name"])
        if H is None:
            continue
        frame_labels = read_labels(frame["img"])
        # Transform label centroids into reference space
        if frame_labels:
            pts = np.float32([[l["cx"], l["cy"]] for l in frame_labels]
                             ).reshape(-1, 1, 2)
            warped_pts = cv2.perspectiveTransform(pts, H).reshape(-1, 2)
            for lbl, (wx, wy) in zip(frame_labels, warped_pts):
                lbl = dict(lbl)
                lbl["cx"] = float(wx)
                lbl["cy"] = float(wy)
                all_labels.append(lbl)

    # Also include ref frame labels
    ref_labels = read_labels(ref_frame["img"])
    all_labels.extend(ref_labels)

    print(f"  → {len(all_labels)} total text regions across all frames")

    # Cluster into components
    components = cluster_labels_into_components(all_labels, ref_grid_info)
    return components, all_labels


# ─────────────────────────────────────────────────────────────────────────────
# 7. MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def run_registration(image_paths: list, out_dir: Path, debug: bool = False):

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Optics Mapper – Phase 2: Multi-Image Registration ===")
    print(f"Images : {[p.name for p in image_paths]}")
    print(f"Output : {out_dir}\n")

    # ── Step 1: Load & analyse all frames ──
    print("[1/6] Loading and analysing frames…")
    frames = []
    for path in image_paths:
        print(f"  Loading '{path.name}'…")
        img = load_image(path)
        frame = analyse_frame(img, path.stem)
        grid_ok = "✓" if frame["holes"] is not None else "✗"
        print(f"  {grid_ok} '{path.name}'  "
              f"size={img.shape[1]}×{img.shape[0]}  "
              f"flatness={frame['flatness']:.3f}  "
              f"keypoints={len(frame['keypoints'])}  "
              f"holes={frame['grid_info'].get('n_holes', 0)}")
        frames.append(frame)

    if len(frames) < 2:
        print("ERROR: need at least 2 images")
        sys.exit(1)

    # ── Step 2: Pick reference frame ──
    print("\n[2/6] Selecting reference frame (flattest view)…")
    ref_idx = int(np.argmax([f["flatness"] for f in frames]))
    ref_frame = frames[ref_idx]
    other_frames = [f for i, f in enumerate(frames) if i != ref_idx]
    print(f"  Reference: '{ref_frame['name']}'  "
          f"flatness={ref_frame['flatness']:.3f}")

    # ── Step 3: Estimate homographies ──
    print("\n[3/6] Estimating homographies (other → reference)…")
    homographies = {}
    for frame in other_frames:
        print(f"  Registering '{frame['name']}'…")
        H = estimate_homography(frame, ref_frame, debug=debug)
        if H is not None:
            H = refine_with_grid(H, frame, ref_frame)
            homographies[frame["name"]] = H
        else:
            print(f"  ✗ Could not register '{frame['name']}'")

    n_registered = len(homographies)
    print(f"\n  {n_registered}/{len(other_frames)} frames successfully registered")

    # ── Step 4: Save registration results ──
    print("\n[4/6] Saving registration metadata…")
    reg_data = {
        "reference_frame": ref_frame["name"],
        "frames": [
            {
                "name": f["name"],
                "flatness": f["flatness"],
                "n_holes": f["grid_info"].get("n_holes", 0),
                "n_keypoints": len(f["keypoints"]),
                "registered": f["name"] in homographies,
                "homography": homographies[f["name"]].tolist()
                              if f["name"] in homographies else None,
            }
            for f in frames
        ],
    }
    reg_path = out_dir / "registration.json"
    reg_path.write_text(json.dumps(reg_data, indent=2))
    print(f"  → {reg_path}")

    # ── Step 5: Fuse frames into composite ──
    print("\n[5/6] Fusing frames into composite…")
    composite = fuse_frames(ref_frame, other_frames, homographies,
                            out_dir, debug=debug)
    comp_path = out_dir / "fused_composite.jpg"
    cv2.imwrite(str(comp_path), composite,
                [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"  → {comp_path}")

    # ── Step 6: Merge detections & output map ──
    print("\n[6/6] Merging detections across frames…")
    ref_grid = ref_frame["grid_info"]
    if not ref_grid:
        print("  ⚠ Reference frame has no grid – using fallback pitch")
        ref_grid = {"pitch_px": 50, "angle_deg": 0,
                    "origin_px": [0, 0], "n_holes": 0}

    components, all_labels = merge_detections(
        composite, ref_grid, ref_frame, other_frames, homographies
    )
    print(f"  → {len(components)} components identified")
    for c in components[:15]:
        print(f"     ({c['grid_col']:3d},{c['grid_row']:3d})  {c['label']}")

    # JSON output
    result = {
        "reference_frame": ref_frame["name"],
        "n_frames_fused": 1 + n_registered,
        "grid": ref_grid,
        "components": components,
    }
    json_path = out_dir / "fused_map.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"\n  JSON → {json_path}")

    # SVG output
    svg_path = out_dir / "fused_map.svg"
    holes = ref_frame["holes"]
    build_svg(composite, holes, ref_grid, all_labels, components, svg_path)

    if debug:
        dbg_path = out_dir / "fused_debug.jpg"
        save_debug_image(composite, holes, all_labels, components, dbg_path)

    print("\n=== Done ===\n")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Optics table mapper – Phase 2: multi-image registration"
    )
    parser.add_argument("images", nargs="+", help="Input image paths")
    parser.add_argument("--debug", action="store_true",
                        help="Save per-frame warped images and debug overlays")
    parser.add_argument("--out-dir", default="optics_output",
                        help="Output directory (default: ./optics_output)")
    args = parser.parse_args()

    paths = [Path(p) for p in args.images]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"ERROR: files not found: {missing}")
        sys.exit(1)

    run_registration(paths, Path(args.out_dir), debug=args.debug)
