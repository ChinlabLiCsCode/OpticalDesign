# Optical Table Designer

A browser-based tool for visualising and editing optical layouts on a 2D table diagram. Elements, beam paths, and background objects are stored as plain CSV/JSON files that round-trip cleanly with the lab's existing spreadsheets.

## Features

- **Interactive canvas** — pan (drag), zoom (scroll), snap-to-grid placement
- **Elements** — add, move, rotate, and soft-delete optical elements; O-number labels and type annotations rendered on canvas
- **Beam paths** — draw and colour-code beam paths between elements
- **Background objects** — overlay structural geometry (mounts, chamber ports, etc.)
- **Optics styles** — regex-matched symbol definitions map element type strings to SVG icons; 66 built-in symbols included
- **Search** — Cmd/Ctrl+F highlights matching elements and centres the view
- **In Design toggle** — elements can be hidden from the diagram without being deleted; restored via the Elements tab
- **Export** — vector PDF export; individual CSV/JSON saves; full project ZIP
- **Persistence** — layout state is saved to localStorage automatically

## File formats

The project uses four files, all human-readable and compatible with standard spreadsheet software.

### `elements.csv`

One row per optical element. Core columns:

| Column | Description |
|---|---|
| Label | O-number identifier (e.g. `O-42`) |
| Type | Free-text type string matched against optics styles |
| Position x / y | Physical coordinates in inches |
| Orientation | Angle in degrees (0 = +x, counter-clockwise positive) |
| In Design | `TRUE` = visible on diagram, `FALSE` = hidden |

Any additional columns (wavelength, beam path, cleaning status, etc.) are preserved on round-trip and shown in the element detail panel.

A `# config:` comment on the first line can store table dimensions and origin:
```
# config: table_length=55,table_width=85,origin_x=0,origin_y=0
```

### `beam_paths.csv`

Alternating `src` / `dest` column pairs, one pair per beam path. A `# colors:` comment on the first line stores per-path colours:
```
# colors: Li H Imaging=#61afef,Cs MOT=#e06c75
Li H Imaging src,Li H Imaging dest,Cs MOT src,Cs MOT dest
O-18,O-51,O-3,O-34
```

### `background_objects.csv`

Line segments grouped by name (chamber walls, mounts, etc.):

| Column | Description |
|---|---|
| Group | Group name |
| Color | Hex colour |
| StrokeWidth | Line width in canvas pixels |
| x1, y1, x2, y2 | Endpoint coordinates in inches |

### `settings.json`

Stores canvas settings, table config, and optics style definitions. Optics styles map type-name patterns (supports `*wildcards*`) to SVG symbol files.

## Running locally

```bash
cd webapp/frontend
npm install
npm run dev
```

The app runs entirely in the browser — no backend required.

## Deployment

The app is deployed via Netlify from this repository. Any push to `main` triggers a new build automatically. Build configuration is in [`netlify.toml`](netlify.toml).

## Example files

The [`webapp/example_files/`](webapp/example_files/) directory contains a sample layout that can be loaded via **Open Project** or by loading each CSV/JSON file individually using the header buttons.
