# Optics Mapper – Claude Code Handoff

## Goal
Build a pipeline that takes photos of an optical breadboard setup and outputs
a 2D map of what components are where, identified by their label stickers.
This is being added as a feature branch on an existing repo at:
`/Users/henry/Documents/CodeProjects/OpticalDesign`

Suggested branch name: `feature/optics-mapper`

---

## Current State
Two working scripts (attach both to this session):
- `optics_mapper.py` — Phase 1: single-image grid detection + OCR
- `optics_register.py` — Phase 2: multi-image registration + fusion

---

## Architecture

### Phase 1 – Single image (`optics_mapper.py`)
1. **Breadboard hole detection** — Hough circles on CLAHE-enhanced grayscale.
   Pitch range is inferred from image size (assumes board fills ~60–100% of
   shorter dimension). Filters to holes with ≥2 neighbours within 1.6× pitch.
2. **Grid fitting** — estimates pitch, angle, origin from NN vectors.
   Converts pixel coords → grid coords (col, row) in 25mm hole units.
3. **OCR** — Tesseract with PSM 11 (sparse text), LSTM engine, sharpening +
   CLAHE pre-processing. Image downscaled to ~1500px before OCR.
4. **Clustering** — DBSCAN (eps = 2.5× pitch) groups nearby text regions
   into single components.
5. **Output** — JSON map + SVG overlay.

### Phase 2 – Multi-image registration (`optics_register.py`)
1. **Flatness scoring** — scores each frame on how rectilinear its detected
   hole grid looks (NN distance uniformity + axis orthogonality). The flattest
   frame becomes the reference coordinate system.
2. **SIFT feature matching** — FLANN matcher + Lowe ratio test (0.72) +
   RANSAC homography. Rejects if <20 inliers or inlier ratio <25%.
3. **Grid-guided refinement** — projects src holes through initial H, matches
   to nearest dst holes within 0.5× pitch, re-estimates H from hole pairs.
   More geometrically grounded than SIFT features alone.
4. **Fusion** — weighted blend of all warped frames; flatness score used as
   per-frame weight so more top-down views contribute more.
5. **Cross-frame OCR merging** — OCR run on composite + each individual
   warped frame; all label centroids transformed to reference space; DBSCAN
   clusters merged with best-confidence text winning per cluster.
6. **Output** — `fused_composite.jpg`, `fused_map.json`, `fused_map.svg`,
   `registration.json` (per-frame homographies + scores).

---

## Key Design Decisions & Why

| Decision | Rationale |
|---|---|
| Multi-image over single top-down camera | Dense setups have heavy occlusion; vacuum chambers / overhead equipment block a fixed top-down view |
| Auto-detect flattest frame as reference | User shoots handheld from multiple angles; no guarantee any specific frame is most top-down |
| Grid refinement on top of SIFT | SIFT matches arbitrary texture; hole grid gives physically meaningful anchors at known 25mm spacing |
| Tesseract PSM 11 (sparse text) | Labels are scattered independently across the image, not in paragraphs |
| DBSCAN for label clustering | Number of components unknown; handles irregular spatial distributions better than k-means |
| Flatness-weighted blend | More top-down frames have less perspective distortion so labels are more legible; their pixels should dominate |

---

## Known Weaknesses (next things to fix)

1. **OCR quality is poor on angled shots** — labels on sides of mounts are
   foreshortened. Fix: per-region crop + deskew before Tesseract. Each
   detected text region should be rectified to a frontal view before OCR.

2. **No component type classification yet** — we read the label sticker
   (e.g. "C230 TMD-B") but don't yet look it up against a Thorlabs catalogue
   to identify what the component actually is (mirror mount, EOM, etc.).
   Thorlabs has structured product pages; could scrape or use their API.

3. **No handling of components without labels** — many mounts have no sticker.
   Phase 3 will need visual classification against Thorlabs reference images.

4. **Testing only done on synthetic second view** — a programmatic perspective
   warp of the original image was used to validate the pipeline. Real
   multi-angle photos are the immediate next test.

---

## Setup

```bash
pip install opencv-python numpy Pillow pytesseract scikit-learn scipy
# also: brew install tesseract  (or apt install tesseract-ocr)
```

### Single image
```bash
python optics_mapper.py photo.jpg --debug
```

### Multi-image
```bash
python optics_register.py photo1.jpg photo2.jpg photo3.jpg --debug --out-dir output/
```

`optics_register.py` imports from `optics_mapper.py` — keep them in the same
directory (or package them together).

---

## Suggested Next Steps for Claude Code

1. Create `feature/optics-mapper` branch
2. Add scripts as `optics_mapper/mapper.py` and `optics_mapper/register.py`
   (or wherever fits the existing repo structure)
3. Run against real multi-angle photos of the lab setup
4. Improve OCR: implement per-region deskew — for each Tesseract bounding box,
   crop + warp to frontal view before re-reading
5. Add a simple CLI entry point / `__main__.py`
