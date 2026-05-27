"""
optics_mapper.py  –  Phase 1: Breadboard grid detection + OCR label reading
                      Outputs a JSON component map and an SVG diagram.

Usage:
    python optics_mapper.py <image_path> [--debug]

Outputs:
    <image_stem>_map.json   – component positions in breadboard coordinates
    <image_stem>_map.svg    – visual map overlaid on a rectified top-down view
    <image_stem>_debug.jpg  – annotated source image (with --debug)
"""

import argparse
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


# ─────────────────────────────────────────────────────────────────────────────
# 1. GRID DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def detect_breadboard_holes(gray: np.ndarray, debug: bool = False):
    """
    Detect the regular grid of M6 mounting holes on an optical breadboard.

    M6 holes are ~6 mm diameter on a 25 mm pitch.  At typical lab photo
    distances with a phone camera the pitch spans roughly 30–120 px in a
    3–4 MP crop.  We scale search parameters to the image size.

    Returns:
        holes       – (N,2) float32 array of (x,y) pixel centres
        grid_info   – dict with pitch_px, origin_px, angle_deg
    """
    h, w = gray.shape
    # Estimate expected pitch range: assume the breadboard fills 60–100% of
    # the shorter image dimension and has ~10–30 holes across it.
    short_side = min(h, w)
    pitch_min = int(short_side / 40)   # very zoomed out
    pitch_max = int(short_side / 6)    # very zoomed in
    pitch_min = max(pitch_min, 15)
    pitch_max = min(pitch_max, 200)

    # Radius of M6 hole ≈ pitch * 0.12
    r_min = max(3, int(pitch_min * 0.10))
    r_max = max(r_min + 2, int(pitch_max * 0.18))

    # --- Pre-process ---
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    eq = clahe.apply(blurred)

    # --- Hough circles: sweep minDist across expected pitch range ---
    best_holes = None
    best_score = -1

    for frac in [0.7, 0.85, 1.0, 1.2]:
        min_dist = int(pitch_min * frac)
        min_dist = max(min_dist, 10)
        circles = cv2.HoughCircles(
            eq,
            cv2.HOUGH_GRADIENT,
            dp=1.5,
            minDist=min_dist,
            param1=50,
            param2=22,
            minRadius=r_min,
            maxRadius=r_max,
        )
        if circles is None:
            continue
        c = circles[0]
        # Only consider candidates whose pitch is in the expected range
        score = _grid_consistency_score(c[:, :2])
        if score > best_score:
            best_score = score
            best_holes = c[:, :2]

    if best_holes is None or len(best_holes) < 9:
        return None, {}

    # Filter to holes that fit the dominant grid pitch
    best_holes, grid_info = _fit_grid(best_holes)

    # Sanity check: pitch should be in expected range
    pitch = grid_info.get("pitch_px", 0)
    if not (pitch_min * 0.5 < pitch < pitch_max * 2.0):
        return None, {}

    return best_holes, grid_info


def _grid_consistency_score(pts: np.ndarray) -> float:
    """Score how well pts form a regular grid (higher = better)."""
    if len(pts) < 4:
        return 0.0
    from scipy.spatial import KDTree
    tree = KDTree(pts)
    dists, _ = tree.query(pts, k=5)
    nn = dists[:, 1]  # nearest-neighbour distances
    median = np.median(nn)
    if median == 0:
        return 0.0
    # Penalise variance in NN distances
    return float(len(pts)) / (1.0 + np.std(nn) / median)


def _fit_grid(holes: np.ndarray):
    """
    Estimate grid pitch and orientation from a cloud of hole centres.
    Returns filtered holes and grid_info dict.
    """
    from scipy.spatial import KDTree

    tree = KDTree(holes)
    dists, idxs = tree.query(holes, k=9)

    # Collect all nearest-neighbour vectors
    vectors = []
    for i in range(len(holes)):
        for j in range(1, 5):
            vec = holes[idxs[i, j]] - holes[i]
            vectors.append(vec)
    vectors = np.array(vectors)

    # Estimate pitch from NN distances
    nn_dists = dists[:, 1]
    pitch_px = float(np.median(nn_dists))

    # Estimate grid angle from dominant direction
    angles = np.arctan2(vectors[:, 1], vectors[:, 0]) % math.pi
    # Histogram angles
    hist, edges = np.histogram(angles, bins=180)
    peak_bin = np.argmax(hist)
    angle_deg = float(np.degrees(edges[peak_bin]))

    # Filter holes: keep those with at least 2 neighbours within 1.6×pitch
    counts = np.array([np.sum(dists[i, 1:] < pitch_px * 1.6) for i in range(len(holes))])
    filtered = holes[counts >= 2]

    # Origin = top-left most hole
    if len(filtered) > 0:
        origin = filtered[np.argmin(filtered[:, 0] + filtered[:, 1])]
    else:
        origin = holes[0]

    grid_info = {
        "pitch_px": round(pitch_px, 2),
        "angle_deg": round(angle_deg, 2),
        "origin_px": [round(float(origin[0]), 2), round(float(origin[1]), 2)],
        "n_holes": int(len(filtered)),
    }
    return filtered, grid_info


def pixel_to_grid(px: float, py: float, grid_info: dict):
    """Convert pixel coordinates to breadboard grid indices (col, row)."""
    pitch = grid_info["pitch_px"]
    ox, oy = grid_info["origin_px"]
    if pitch == 0:
        return 0, 0
    col = round((px - ox) / pitch)
    row = round((py - oy) / pitch)
    return int(col), int(row)


# ─────────────────────────────────────────────────────────────────────────────
# 2. OCR LABEL READING  (Tesseract via pytesseract)
# ─────────────────────────────────────────────────────────────────────────────

def read_labels(img_bgr: np.ndarray, min_confidence: float = 30.0):
    """
    Run Tesseract on the image with bounding-box detail.
    Returns a list of label dicts: { text, confidence, cx, cy, bbox }

    Strategy:
      • Upscale smaller images so Tesseract works better on tiny labels
      • Use LSTM engine (oem 1) with sparse-text PSM (11) – good for many
        small independent labels scattered across a scene
    """
    import pytesseract

    h, w = img_bgr.shape[:2]

    # Upscale if image is very large (Tesseract works best ~150-300 dpi equiv)
    # For a 3024×4032 lab photo, downsample to ~1500px on the long side first
    # so small labels are still readable but processing is faster.
    scale = min(1.0, 1500 / max(h, w))
    if scale < 1.0:
        proc = cv2.resize(img_bgr, (int(w * scale), int(h * scale)),
                          interpolation=cv2.INTER_AREA)
    else:
        proc = img_bgr.copy()

    # Pre-process: slight sharpen + adaptive threshold for small text on dark mounts
    gray = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharp = cv2.filter2D(gray, -1, kernel)
    # CLAHE for contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(sharp)

    config = (
        "--oem 1 "        # LSTM engine
        "--psm 11 "       # Sparse text – find as much text as possible
        "-c tessedit_char_whitelist="
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_./() "
    )

    data = pytesseract.image_to_data(
        enhanced,
        config=config,
        output_type=pytesseract.Output.DICT,
    )

    labels = []
    n = len(data["text"])
    for i in range(n):
        text = data["text"][i].strip()
        conf = float(data["conf"][i])
        if conf < min_confidence or len(text) < 2:
            continue
        x, y, bw, bh = (data["left"][i], data["top"][i],
                        data["width"][i], data["height"][i])
        # Map back to original pixel coords
        inv = 1.0 / scale
        x0, y0 = x * inv, y * inv
        x1, y1 = (x + bw) * inv, (y + bh) * inv
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        bbox = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        labels.append({
            "text": text,
            "confidence": round(conf, 1),
            "cx": round(cx, 1),
            "cy": round(cy, 1),
            "bbox": [[round(px, 1), round(py, 1)] for px, py in bbox],
        })
    return labels


# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPONENT CLUSTERING
#    Group nearby labels that belong to the same physical component
# ─────────────────────────────────────────────────────────────────────────────

def cluster_labels_into_components(labels: list, grid_info: dict):
    """
    Use DBSCAN to group labels that are spatially close into single components.
    Returns a list of component dicts with merged text and grid position.
    """
    from sklearn.cluster import DBSCAN

    if not labels:
        return []

    pts = np.array([[l["cx"], l["cy"]] for l in labels])
    pitch = grid_info.get("pitch_px", 40)
    eps = pitch * 2.5  # labels within ~2.5 holes belong to one component

    db = DBSCAN(eps=eps, min_samples=1).fit(pts)
    cluster_ids = db.labels_

    components = []
    for cid in set(cluster_ids):
        members = [labels[i] for i in range(len(labels)) if cluster_ids[i] == cid]
        # Sort by confidence desc, merge texts
        members.sort(key=lambda l: -l["confidence"])
        merged_text = " / ".join(
            dict.fromkeys(m["text"] for m in members)  # deduplicate, preserve order
        )
        # Centroid of the cluster
        cx = float(np.mean([m["cx"] for m in members]))
        cy = float(np.mean([m["cy"] for m in members]))
        col, row = pixel_to_grid(cx, cy, grid_info)
        components.append({
            "label": merged_text,
            "grid_col": col,
            "grid_row": row,
            "pixel_cx": round(cx, 1),
            "pixel_cy": round(cy, 1),
            "n_text_regions": len(members),
            "max_confidence": members[0]["confidence"],
        })

    # Sort by grid position for readability
    components.sort(key=lambda c: (c["grid_row"], c["grid_col"]))
    return components


# ─────────────────────────────────────────────────────────────────────────────
# 4. SVG OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

def build_svg(img_bgr: np.ndarray, holes, grid_info: dict,
              labels: list, components: list, out_path: Path):
    """
    Produce an SVG that overlays:
      • detected breadboard holes (blue circles)
      • OCR text regions (yellow boxes)
      • component labels at their grid position (coloured badges)
    on a scaled-down version of the source image embedded as a data URI.
    """
    import base64

    h, w = img_bgr.shape[:2]
    scale = min(1.0, 1200 / max(h, w))
    disp_w = int(w * scale)
    disp_h = int(h * scale)

    # Embed resized image
    small = cv2.resize(img_bgr, (disp_w, disp_h))
    _, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 80])
    b64 = base64.b64encode(buf).decode()

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{disp_w}" height="{disp_h}" '
        f'viewBox="0 0 {disp_w} {disp_h}">',
        f'  <image href="data:image/jpeg;base64,{b64}" width="{disp_w}" height="{disp_h}"/>',
    ]

    # Hole grid
    if holes is not None and len(holes):
        lines.append('  <g id="holes" opacity="0.6">')
        for hx, hy in holes:
            lines.append(
                f'    <circle cx="{hx*scale:.1f}" cy="{hy*scale:.1f}" r="4" '
                f'fill="none" stroke="#00aaff" stroke-width="1.2"/>'
            )
        lines.append("  </g>")

    # OCR bounding boxes
    lines.append('  <g id="ocr_boxes" opacity="0.7">')
    for lbl in labels:
        pts = [(x * scale, y * scale) for x, y in lbl["bbox"]]
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        lines.append(
            f'    <polygon points="{pts_str}" fill="none" '
            f'stroke="#ffdd00" stroke-width="1.2"/>'
        )
    lines.append("  </g>")

    # Component badges
    colors = ["#e74c3c", "#2ecc71", "#3498db", "#9b59b6",
              "#e67e22", "#1abc9c", "#e91e63", "#ff5722"]
    lines.append('  <g id="components">')
    for i, comp in enumerate(components):
        cx = comp["pixel_cx"] * scale
        cy = comp["pixel_cy"] * scale
        color = colors[i % len(colors)]
        text = comp["label"][:30]  # truncate long labels
        grid_tag = f'({comp["grid_col"]},{comp["grid_row"]})'

        # Badge background
        lines.append(
            f'    <rect x="{cx-4:.1f}" y="{cy-14:.1f}" width="10" height="10" '
            f'rx="2" fill="{color}" opacity="0.85"/>'
        )
        # Grid coordinate label (small, below badge)
        lines.append(
            f'    <text x="{cx+8:.1f}" y="{cy-5:.1f}" '
            f'font-family="monospace" font-size="9" fill="white" '
            f'stroke="black" stroke-width="0.4">{text}</text>'
        )
        lines.append(
            f'    <text x="{cx+8:.1f}" y="{cy+5:.1f}" '
            f'font-family="monospace" font-size="8" fill="#aaffaa" '
            f'stroke="black" stroke-width="0.3">{grid_tag}</text>'
        )
    lines.append("  </g>")

    # Legend
    pitch = grid_info.get("pitch_px", "?")
    n_holes = grid_info.get("n_holes", 0)
    lines += [
        f'  <rect x="4" y="4" width="240" height="44" rx="4" '
        f'fill="black" opacity="0.6"/>',
        f'  <text x="10" y="20" font-family="sans-serif" font-size="11" fill="white">'
        f'Grid: {n_holes} holes detected, pitch≈{pitch}px</text>',
        f'  <text x="10" y="36" font-family="sans-serif" font-size="11" fill="white">'
        f'Components: {len(components)} labelled regions</text>',
        "</svg>",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  SVG written → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. DEBUG OVERLAY
# ─────────────────────────────────────────────────────────────────────────────

def save_debug_image(img_bgr: np.ndarray, holes, labels: list,
                     components: list, out_path: Path):
    vis = img_bgr.copy()

    if holes is not None:
        for hx, hy in holes:
            cv2.circle(vis, (int(hx), int(hy)), 6, (255, 150, 0), 1)

    for lbl in labels:
        pts = np.array(lbl["bbox"], dtype=np.int32)
        cv2.polylines(vis, [pts], True, (0, 220, 220), 1)
        cv2.putText(vis, lbl["text"], (pts[0][0], pts[0][1] - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 220), 1)

    for comp in components:
        cx, cy = int(comp["pixel_cx"]), int(comp["pixel_cy"])
        cv2.circle(vis, (cx, cy), 10, (0, 80, 255), 2)
        cv2.putText(vis, f'({comp["grid_col"]},{comp["grid_row"]})',
                    (cx + 12, cy + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 80), 1)

    cv2.imwrite(str(out_path), vis)
    print(f"  Debug image → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def process_image(image_path: str, debug: bool = False):
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"ERROR: file not found: {img_path}")
        sys.exit(1)

    print(f"\n=== Optics Mapper – Phase 1 ===")
    print(f"Input : {img_path}")

    img_bgr = cv2.imread(str(img_path))
    if img_bgr is None:
        print("ERROR: could not read image")
        sys.exit(1)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    print(f"Image size: {img_bgr.shape[1]}×{img_bgr.shape[0]} px")

    # --- Step 1: Grid detection ---
    print("\n[1/3] Detecting breadboard hole grid…")
    holes, grid_info = detect_breadboard_holes(gray, debug=debug)
    if holes is None:
        print("  ⚠ Could not detect hole grid – using fallback pitch of 40 px")
        grid_info = {"pitch_px": 40, "angle_deg": 0,
                     "origin_px": [0, 0], "n_holes": 0}
    else:
        print(f"  ✓ {grid_info['n_holes']} holes  |  pitch ≈ {grid_info['pitch_px']} px  "
              f"|  angle ≈ {grid_info['angle_deg']}°")

    # --- Step 2: OCR ---
    print("\n[2/3] Reading labels via OCR…")
    labels = read_labels(img_bgr)
    print(f"  ✓ {len(labels)} text regions found")
    for lbl in sorted(labels, key=lambda l: -l["confidence"])[:10]:
        print(f"     '{lbl['text']}'  conf={lbl['confidence']:.2f}  "
              f"px=({lbl['cx']:.0f},{lbl['cy']:.0f})")

    # --- Step 3: Cluster into components ---
    print("\n[3/3] Clustering labels into components…")
    components = cluster_labels_into_components(labels, grid_info)
    print(f"  ✓ {len(components)} components identified")

    # --- Outputs ---
    stem = img_path.stem
    out_dir = Path("/home/claude")

    # JSON
    result = {
        "source_image": img_path.name,
        "grid": grid_info,
        "components": components,
    }
    json_path = out_dir / f"{stem}_map.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"\n  JSON written → {json_path}")

    # SVG
    svg_path = out_dir / f"{stem}_map.svg"
    build_svg(img_bgr, holes, grid_info, labels, components, svg_path)

    # Debug image
    if debug:
        dbg_path = out_dir / f"{stem}_debug.jpg"
        save_debug_image(img_bgr, holes, labels, components, dbg_path)

    print("\n=== Done ===\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optics table mapper – Phase 1")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("--debug", action="store_true",
                        help="Save annotated debug image")
    args = parser.parse_args()
    process_image(args.image, debug=args.debug)
