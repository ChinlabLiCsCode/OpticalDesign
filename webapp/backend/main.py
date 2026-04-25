"""
FastAPI backend for the LiCs optical design editor.
Reads element positions and beam paths from Google Sheets, triggers PDF generation.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Optical Design API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SHEET_ID   = "1mzK37AdseAbvQxTp3GW4Nsm7sQxGh-2In53QMjHEb7w"
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "Design_v4"

LASER_COLORS = {
    "li h imaging":      "magenta",
    "li eom":            "magenta",
    "li repump":         "lime",
    "li mot":            "purple",
    "cs h imaging":      "cyan",
    "cs h img":          "cyan",
    "li zeeman":         "red",
    "cs zeeman":         "blue",
    "cs mot":            "green",
    "cs v optical pump": "navy",
    "cs h optical pump": "hotpink",
    "rsc":               "coral",
    "otop":              "crimson",
    "dual color":        "violet",
    "bfl":               "cornflowerblue",
}

SETUP_CONFIG = {
    "Breadboard": {
        "table_length": 50,
        "table_width":  82,
        "origin_x":     24,
        "origin_y":     40,
    },
    "Table": {
        "table_length": 100,
        "table_width":  60,
        "origin_x":     50,
        "origin_y":     30,
    },
}


def load_elements(setup: str) -> list[dict]:
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    df = pd.read_csv(url)
    df = df[df["Setup Location"].str.strip() == setup].copy()
    df = df.dropna(subset=["O-number"])

    _num = df["O-number"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["Label"]      = _num.where(_num.str.startswith("O-"), "O-" + _num)
    df["Position x"] = df["Position X"]
    df["Position y"] = df["Position Y"]

    import math

    elements = []
    for _, row in df.iterrows():
        try:
            x = float(row["Position x"])
            y = float(row["Position y"])
        except (ValueError, TypeError):
            continue
        if math.isnan(x) or math.isnan(y):
            continue

        label = str(row["Label"]).strip()
        # Strip trailing .0 from numeric part of label
        if "-" in label:
            prefix, num_part = label.rsplit("-", 1)
            if num_part.endswith(".0"):
                num_part = num_part[:-2]
            label = f"{prefix}-{num_part}"

        # Parse O-number — keep as string to avoid NaN/float issues in JSON
        raw = str(row["O-number"]).strip()
        eid = raw  # always a string; frontend doesn't need it as a number

        orient_raw = row.get("Orientation")
        try:
            orient = float(orient_raw) if pd.notna(orient_raw) else 0.0
            orient = orient if not math.isnan(orient) else 0.0
        except (ValueError, TypeError):
            orient = 0.0

        elements.append({
            "id":          eid,
            "label":       label,
            "type":        str(row.get("Type", "")).strip(),
            "x":           x,
            "y":           y,
            "orientation": orient,
        })

    return elements


def segments_to_edges(segments: list[list[str]]) -> list[list[str]]:
    """Convert ordered segment lists to directed [src, dest] edge pairs."""
    edges = []
    for seg in segments:
        for i in range(len(seg) - 1):
            edges.append([seg[i], seg[i + 1]])
    return edges


def load_beam_paths() -> dict:
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet=Beam+Paths"
    )
    bp_df = pd.read_csv(url)

    paths: dict[str, dict] = {}
    for col in bp_df.columns:
        if col.startswith("Unnamed"):
            continue
        color = LASER_COLORS.get(col.lower(), "gray")
        segments: list[list[str]] = []
        current: list[str] = []
        for val in bp_df[col]:
            if pd.isna(val):
                break
            val = str(val).strip()
            if val == "-":
                if current:
                    segments.append(current)
                    current = []
            else:
                current.append(val)
        if current:
            segments.append(current)
        paths[col] = {"color": color, "edges": segments_to_edges(segments)}

    return paths


@app.get("/api/elements")
def get_elements(setup: str = "Breadboard"):
    if setup not in SETUP_CONFIG:
        raise HTTPException(400, f"Unknown setup: {setup}. Use 'Breadboard' or 'Table'.")
    try:
        elements = load_elements(setup)
        cfg = SETUP_CONFIG[setup]
        return {"elements": elements, "config": cfg}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/beampaths")
def get_beam_paths():
    try:
        return load_beam_paths()
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/generate")
def generate_pdfs():
    try:
        result = subprocess.run(
            [sys.executable, "generate_all.py"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise HTTPException(500, result.stderr or result.stdout)
        return {"ok": True, "output": result.stdout}
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "PDF generation timed out")
