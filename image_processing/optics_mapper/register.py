"""
register.py  –  Phase 2: Multi-image registration + fusion

Usage (module):
    from optics_mapper.register import run_registration
    run_registration([Path("a.jpg"), Path("b.jpg")], out_dir=Path("output/"))

Outputs (in out_dir):
    fused_composite.jpg   – warped frames blended together
    fused_map.json        – component grid map
    fused_map.svg         – annotated SVG
    registration.json     – per-image homographies + scores
    *_warped.jpg          – individual warped frames (with debug=True)
"""

import json
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from .mapper import (
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

MAX_DIM = 1600


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
    """Detect grid, compute flatness score, extract SIFT keypoints."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    holes, grid_info = detect_breadboard_holes(gray)

    flatness = _flatness_score(holes, grid_info) if holes is not None else 0.0

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
# ─────────────────────────────────────────────────────────────────────────────

def _flatness_score(holes: np.ndarray, grid_info: dict) -> float:
    """
    Returns a score in [0, 1]: 1.0 = perfectly top-down, 0.0 = heavily tilted.
    Combines NN distance uniformity and axis orthogonality.
    """
    if holes is None or len(holes) < 16:
        return 0.0

    from scipy.spatial import KDTree
    tree = KDTree(holes)
    dists, idxs = tree.query(holes, k=5)

    nn = dists[:, 1]
    cov = np.std(nn) / (np.mean(nn) + 1e-6)
    score_dist = float(np.exp(-3.0 * cov))

    vectors = []
    for i in range(len(holes)):
        for j in range(1, 5):
            v = holes[idxs[i, j]] - holes[i]
            if np.linalg.norm(v) > 0:
                vectors.append(v)
    vectors = np.array(vectors)
    angles = np.degrees(np.arctan2(vectors[:, 1], vectors[:, 0])) % 180.0

    hist, edges = np.histogram(angles, bins=180, range=(0, 180))
    hist = np.convolve(hist, np.ones(5) / 5, mode='same')
    peaks = _find_two_peaks(hist)
    if peaks is not None:
        a1, a2 = edges[peaks[0]], edges[peaks[1]]
        delta = abs(abs(a1 - a2) - 90.0)
        score_ortho = float(np.exp(-0.05 * delta))
    else:
        score_ortho = 0.3

    return round(float(0.5 * score_dist + 0.5 * score_ortho), 4)


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

MIN_MATCHES = 20


def estimate_homography(src_frame: dict, dst_frame: dict,
                        debug: bool = False) -> Optional[np.ndarray]:
    """
    Estimate homography H such that:  dst_pts ≈ H @ src_pts
    Uses SIFT + FLANN matching + RANSAC. Returns H (3x3) or None.
    """
    descs_src = src_frame["descriptors"]
    descs_dst = dst_frame["descriptors"]

    if descs_src is None or descs_dst is None:
        return None
    if len(descs_src) < MIN_MATCHES or len(descs_dst) < MIN_MATCHES:
        return None

    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=100)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    try:
        matches = flann.knnMatch(descs_src, descs_dst, k=2)
    except cv2.error:
        return None

    good = [m for m, n in matches if m.distance < 0.72 * n.distance]

    if len(good) < MIN_MATCHES:
        print(f"    Only {len(good)} good matches between "
              f"'{src_frame['name']}' -> '{dst_frame['name']}' (need {MIN_MATCHES})")
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
    print(f"    {inliers}/{len(good)} inliers ({inlier_ratio:.0%})  "
          f"'{src_frame['name']}' -> '{dst_frame['name']}'")

    if inlier_ratio < 0.25 or inliers < MIN_MATCHES:
        print(f"    Homography rejected (low inlier ratio)")
        return None

    if not _homography_is_sane(H, src_frame["img"].shape):
        print(f"    Homography rejected (degenerate transform)")
        return None

    return H


def _homography_is_sane(H: np.ndarray, shape: tuple) -> bool:
    """Reject degenerate homographies by checking warped corners form a valid quad."""
    h, w = shape[:2]
    corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    warped = cv2.perspectiveTransform(corners, H).reshape(-1, 2)

    hull = cv2.convexHull(warped.astype(np.float32))
    if len(hull) < 4:
        return False

    orig_area = w * h
    warped_area = float(cv2.contourArea(hull))
    ratio = warped_area / (orig_area + 1e-6)
    return 0.1 < ratio < 10.0


# ─────────────────────────────────────────────────────────────────────────────
# 4. GRID-BASED HOMOGRAPHY ESTIMATION  (primary method)
#    The breadboard hole grid is a physical planar ground truth at 25 mm pitch.
#    Every frame has detected holes with integer grid coordinates assigned by
#    pixel_to_grid(). Two frames seeing the same physical holes will agree on
#    grid coords up to a constant integer offset (dc, dr) — we find that offset
#    by voting, build pixel correspondences, then run RANSAC homography.
#    Far more reliable than SIFT on repetitive black mounts.
# ─────────────────────────────────────────────────────────────────────────────

def _vote_grid_offset(src_gc: np.ndarray, dst_gc: np.ndarray,
                      search_range: int = 80):
    """
    Find integer offset (dc, dr) maximising hole overlap between two frames.

    For each sampled pair (src_i, dst_j) compute candidate offset
    (col_j - col_i, row_j - row_i). The true overlap region produces a sharp
    peak; unrelated holes scatter uniformly.

    Returns (dc, dr), vote_count  — or (None, 0) on failure.
    """
    rng = np.random.default_rng(42)
    cap = 500
    s = src_gc[rng.choice(len(src_gc), min(cap, len(src_gc)), replace=False)]
    d = dst_gc[rng.choice(len(dst_gc), min(cap, len(dst_gc)), replace=False)]

    # All pairwise differences: shape (len_s, len_d, 2)
    diffs = d[np.newaxis, :, :] - s[:, np.newaxis, :]
    dc_arr = diffs[:, :, 0]
    dr_arr = diffs[:, :, 1]

    in_range = (np.abs(dc_arr) <= search_range) & (np.abs(dr_arr) <= search_range)
    dc_vals = dc_arr[in_range].astype(np.int32)
    dr_vals = dr_arr[in_range].astype(np.int32)

    if len(dc_vals) == 0:
        return None, 0

    # Encode as single integer for fast unique-counting
    span = 2 * search_range + 1
    encoded = (dc_vals + search_range) * span + (dr_vals + search_range)
    unique, counts = np.unique(encoded, return_counts=True)
    best_enc = unique[np.argmax(counts)]
    best_count = int(counts.max())
    best_dc = int(best_enc // span) - search_range
    best_dr = int(best_enc % span) - search_range
    return (best_dc, best_dr), best_count


def estimate_homography_from_grid(src_frame: dict,
                                  dst_frame: dict) -> Optional[np.ndarray]:
    """
    Estimate homography using breadboard hole-grid correspondences.

    1. Assign integer grid coords to all detected holes in each frame.
    2. Vote for the grid offset (dc, dr) between the two coord systems.
    3. Build pixel correspondences: src_hole_i <-> dst_hole at (col+dc, row+dr).
    4. RANSAC homography from matched pixel positions.
    """
    src_holes = src_frame.get("holes")
    dst_holes = dst_frame.get("holes")

    if src_holes is None or len(src_holes) < 9:
        return None
    if dst_holes is None or len(dst_holes) < 9:
        return None

    src_gc = np.array([pixel_to_grid(x, y, src_frame["grid_info"])
                       for x, y in src_holes])
    dst_gc = np.array([pixel_to_grid(x, y, dst_frame["grid_info"])
                       for x, y in dst_holes])

    (dc, dr), n_votes = _vote_grid_offset(src_gc, dst_gc)
    if n_votes < 8:
        print(f"    Grid vote: only {n_votes} votes "
              f"'{src_frame['name']}' -> '{dst_frame['name']}'")
        return None
    print(f"    Grid offset ({dc:+d},{dr:+d})  votes={n_votes}")

    # Build dst lookup: (col, row) -> hole index
    dst_lookup = {(int(c), int(r)): j for j, (c, r) in enumerate(dst_gc)}

    src_pts, dst_pts = [], []
    used = set()
    for i, (ci, ri) in enumerate(src_gc):
        # ±1 tolerance absorbs rounding errors in grid coord assignment
        for ddc in range(-1, 2):
            for ddr in range(-1, 2):
                j = dst_lookup.get((int(ci) + dc + ddc, int(ri) + dr + ddr))
                if j is not None and j not in used:
                    src_pts.append(src_holes[i])
                    dst_pts.append(dst_holes[j])
                    used.add(j)
                    break
            else:
                continue
            break

    n_pairs = len(src_pts)
    if n_pairs < 8:
        print(f"    Grid match: only {n_pairs} correspondences")
        return None

    src_arr = np.float32(src_pts).reshape(-1, 1, 2)
    dst_arr = np.float32(dst_pts).reshape(-1, 1, 2)
    thresh = dst_frame["grid_info"].get("pitch_px", 40) * 0.4

    H, mask = cv2.findHomography(src_arr, dst_arr, cv2.RANSAC,
                                 ransacReprojThreshold=thresh)
    if H is None:
        return None

    n_inliers = int(mask.sum())
    print(f"    Grid homography: {n_inliers}/{n_pairs} inliers "
          f"({n_inliers/n_pairs:.0%})")

    if n_inliers < 8 or not _homography_is_sane(H, src_frame["img"].shape):
        return None

    return H


# ─────────────────────────────────────────────────────────────────────────────
# 4b. GRID-GUIDED HOMOGRAPHY REFINEMENT  (fallback refinement after SIFT)
# ─────────────────────────────────────────────────────────────────────────────

def refine_with_grid(H_init: np.ndarray,
                     src_frame: dict, dst_frame: dict) -> np.ndarray:
    """
    Refine H using matched breadboard hole positions.
    Falls back to H_init if not enough holes are matched.
    """
    src_holes = src_frame.get("holes")
    dst_holes = dst_frame.get("holes")

    if src_holes is None or dst_holes is None:
        return H_init
    if len(src_holes) < 9 or len(dst_holes) < 9:
        return H_init

    src_pts = src_holes.reshape(-1, 1, 2).astype(np.float32)
    projected = cv2.perspectiveTransform(src_pts, H_init).reshape(-1, 2)

    from scipy.spatial import KDTree
    dst_pitch = dst_frame["grid_info"].get("pitch_px", 40)
    tree = KDTree(dst_holes)
    dists, idxs = tree.query(projected, k=1)

    threshold = dst_pitch * 0.5
    mask = dists < threshold
    if mask.sum() < 8:
        return H_init

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
    print(f"    Grid refinement: {n_inliers}/{mask.sum()} hole pairs used")
    return H_refined


# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPOSITE FUSION
# ─────────────────────────────────────────────────────────────────────────────

def fuse_frames(ref_frame: dict,
                other_frames: list,
                homographies: dict,
                out_dir: Path,
                debug: bool = False) -> np.ndarray:
    """
    Warp all frames into reference space and blend, weighting by flatness score.
    """
    ref_img = ref_frame["img"]
    h_ref, w_ref = ref_img.shape[:2]

    acc = np.zeros((h_ref, w_ref, 3), dtype=np.float64)
    weight_acc = np.zeros((h_ref, w_ref, 1), dtype=np.float64)

    ref_weight = max(ref_frame["flatness"], 0.5)
    acc += ref_img.astype(np.float64) * ref_weight
    weight_acc += ref_weight

    for frame in other_frames:
        name = frame["name"]
        H = homographies.get(name)
        if H is None:
            print(f"  Skipping '{name}' – no valid homography")
            continue

        warped = cv2.warpPerspective(
            frame["img"], H, (w_ref, h_ref),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )

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
            print(f"    Warped frame saved -> {dbg_path}")

    safe_weight = np.where(weight_acc > 0, weight_acc, 1.0)
    composite = (acc / safe_weight).clip(0, 255).astype(np.uint8)
    return composite


# ─────────────────────────────────────────────────────────────────────────────
# 6. CROSS-FRAME DETECTION MERGING
# ─────────────────────────────────────────────────────────────────────────────

def merge_detections(composite: np.ndarray,
                     ref_grid_info: dict,
                     ref_frame: dict,
                     other_frames: list,
                     homographies: dict) -> tuple:
    """
    Run OCR on the composite + warp per-frame labels into reference space,
    then cluster everything into components.
    """
    print("\n  Running OCR on fused composite...")
    composite_labels = read_labels(composite)
    print(f"  -> {len(composite_labels)} text regions in composite")

    all_labels = list(composite_labels)

    for frame in other_frames:
        H = homographies.get(frame["name"])
        if H is None:
            continue
        frame_labels = read_labels(frame["img"])
        if frame_labels:
            pts = np.float32([[l["cx"], l["cy"]] for l in frame_labels]
                             ).reshape(-1, 1, 2)
            warped_pts = cv2.perspectiveTransform(pts, H).reshape(-1, 2)
            for lbl, (wx, wy) in zip(frame_labels, warped_pts):
                lbl = dict(lbl)
                lbl["cx"] = float(wx)
                lbl["cy"] = float(wy)
                all_labels.append(lbl)

    ref_labels = read_labels(ref_frame["img"])
    all_labels.extend(ref_labels)

    print(f"  -> {len(all_labels)} total text regions across all frames")

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

    print("[1/6] Loading and analysing frames...")
    frames = []
    for path in image_paths:
        print(f"  Loading '{path.name}'...")
        img = load_image(path)
        frame = analyse_frame(img, path.stem)
        grid_ok = "ok" if frame["holes"] is not None else "no grid"
        print(f"  [{grid_ok}] '{path.name}'  "
              f"size={img.shape[1]}x{img.shape[0]}  "
              f"flatness={frame['flatness']:.3f}  "
              f"keypoints={len(frame['keypoints'])}  "
              f"holes={frame['grid_info'].get('n_holes', 0)}")
        frames.append(frame)

    if len(frames) < 2:
        print("ERROR: need at least 2 images")
        sys.exit(1)

    print("\n[2/6] Selecting reference frame (flattest view)...")
    ref_idx = int(np.argmax([f["flatness"] for f in frames]))
    ref_frame = frames[ref_idx]
    other_frames = [f for i, f in enumerate(frames) if i != ref_idx]
    print(f"  Reference: '{ref_frame['name']}'  flatness={ref_frame['flatness']:.3f}")

    print("\n[3/6] Estimating homographies (other -> reference)...")
    homographies = {}
    for frame in other_frames:
        print(f"  Registering '{frame['name']}'...")
        H = estimate_homography_from_grid(frame, ref_frame)
        if H is None:
            print(f"    Grid method failed — trying SIFT fallback...")
            H = estimate_homography(frame, ref_frame, debug=debug)
            if H is not None:
                H = refine_with_grid(H, frame, ref_frame)
        if H is not None:
            homographies[frame["name"]] = H
        else:
            print(f"  Could not register '{frame['name']}'")

    n_registered = len(homographies)
    print(f"\n  {n_registered}/{len(other_frames)} frames successfully registered")

    print("\n[4/6] Saving registration metadata...")
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
    print(f"  -> {reg_path}")

    print("\n[5/6] Fusing frames into composite...")
    composite = fuse_frames(ref_frame, other_frames, homographies,
                            out_dir, debug=debug)
    comp_path = out_dir / "fused_composite.jpg"
    cv2.imwrite(str(comp_path), composite, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"  -> {comp_path}")

    print("\n[6/6] Merging detections across frames...")
    ref_grid = ref_frame["grid_info"]
    if not ref_grid:
        print("  Warning: reference frame has no grid – using fallback pitch")
        ref_grid = {"pitch_px": 50, "angle_deg": 0,
                    "origin_px": [0, 0], "n_holes": 0}

    components, all_labels = merge_detections(
        composite, ref_grid, ref_frame, other_frames, homographies
    )
    print(f"  -> {len(components)} components identified")
    for c in components[:15]:
        print(f"     ({c['grid_col']:3d},{c['grid_row']:3d})  {c['label']}")

    result = {
        "reference_frame": ref_frame["name"],
        "n_frames_fused": 1 + n_registered,
        "grid": ref_grid,
        "components": components,
    }
    json_path = out_dir / "fused_map.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"\n  JSON -> {json_path}")

    svg_path = out_dir / "fused_map.svg"
    holes = ref_frame["holes"]
    build_svg(composite, holes, ref_grid, all_labels, components, svg_path)

    if debug:
        dbg_path = out_dir / "fused_debug.jpg"
        save_debug_image(composite, holes, all_labels, components, dbg_path)

    print("\n=== Done ===\n")
    return result
