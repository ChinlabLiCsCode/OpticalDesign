#!/usr/bin/env python3
"""
SVG Metadata Stripper
=====================
Conversion rules used when porting SVG symbols from ComponentLibrary_files/
into frontend/public/symbols/. Removes non-visual metadata while preserving
all visual content (gradients, shapes, colours, strokes).

Rules applied
-------------
1.  XML generator comments       <!-- Generator: Adobe Illustrator ... -->
2.  <metadata> element           XMP data, variableSets, sfw settings,
                                 embedded JPEG thumbnails
3.  <sodipodi:namedview>         Inkscape editor viewport / ruler state
4.  <a:midPointStop>             Adobe SVG Viewer Extension; non-standard,
                                 silently ignored by all modern renderers
5.  All prefixed attrs from      any inkscape:*, sodipodi:*, i:*, a:*,
    dropped-namespace prefixes   dc:*, rdf:*, ns:*, ns0:*, xap:*, xapGImg:*,
                                 x:* attribute on any element (leaving these
                                 in place after dropping their namespace
                                 declaration produces invalid XML that some
                                 parsers, e.g. Inkscape, reject).
6.  Deprecated <svg> root attrs  overflow="visible", enable-background,
                                 xml:space="preserve"
7.  Namespace declarations       sodipodi, inkscape, rdf, dc, i (Illustrator),
                                 a (AdobeSVGViewerExtensions), ns (Variables),
                                 ns0 (SaveForWeb), xap, xapGImg, svg (redundant),
                                 x (adobe meta)

Namespaces retained
-------------------
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"   (needed for xlink:href)

Optional post-processing
------------------------
--fit-viewbox     After stripping, invoke Inkscape to compute the true visual
                  bounding box of the drawing and rewrite the <svg> viewBox
                  (plus width/height) so the artwork fills the canvas without
                  padding. Requires Inkscape (found at $INKSCAPE or the
                  default macOS install path).

--out-dir DIR     Copy stripped output into DIR (typically
                  webapp/frontend/public/symbols/), preserving the source
                  filename. May be combined with --fit-viewbox.

--sync-symbols-js PATH
                  For each processed file, if PATH's DEFAULT_SYMBOL_DEFS
                  contains an entry whose href matches the file's basename,
                  rewrite that entry's w and h to the new viewBox dimensions.
                  displayH is left untouched. Also appends the filename to
                  AVAILABLE_SYMBOLS if it's not already listed, so the SVG
                  picker in the app sees the new icon. Requires
                  --fit-viewbox to be meaningful.

Usage
-----
    # Modify files in-place (one or more):
    python3 strip_svg_metadata.py symbols/h-iris.svg symbols/h-lenstube.svg

    # Full end-to-end publish: strip, fit viewBox, copy to public/symbols/
    python3 strip_svg_metadata.py --fit-viewbox \\
        --out-dir ../frontend/public/symbols \\
        homemade/*.svg

    # Write to a specific single file:
    python3 strip_svg_metadata.py input.svg -o output.svg
"""

import os
import re
import shutil
import subprocess
import sys
import pathlib


# ---------------------------------------------------------------------------
# Ordered list of (pattern, replacement) substitutions applied to raw text.
# Using raw-text regex avoids namespace-mangling from xml.etree parsers.
# ---------------------------------------------------------------------------

_SUBS = []

def _sub(pattern, repl='', flags=re.DOTALL):
    _SUBS.append((re.compile(pattern, flags), repl))


# 1. XML generator / editor comments
_sub(r'[ \t]*<!--[^-]*(?:-(?!->)[^-]*)*-->[ \t]*\n?')

# 2. <metadata> block (may be very long; contains xpacket, RDF, thumbnails)
_sub(r'[ \t]*<metadata\b[^>]*>.*?</metadata>[ \t]*\n?')

# 3. <sodipodi:namedview> (self-closing or with children)
_sub(r'[ \t]*<sodipodi:namedview\b[^>]*/?>[ \t]*\n?')
_sub(r'[ \t]*<sodipodi:namedview\b[^>]*>.*?</sodipodi:namedview>[ \t]*\n?')

# 4. <a:midPointStop> (always self-closing, always inside a gradient)
_sub(r'[ \t]*<a:midPointStop\b[^/]*/>\n?')

# 5. Any attribute whose prefix belongs to a dropped namespace, from any element.
# Leaving these in place after we drop the xmlns declaration below produces
# invalid XML (Inkscape's parser hard-fails on it).
_DROPPED_PREFIXES = [
    'inkscape', 'sodipodi', 'i', 'a', 'dc', 'rdf',
    'ns', 'ns0', 'xap', 'xapGImg', 'x',
]
for _prefix in _DROPPED_PREFIXES:
    _sub(
        r'\s+' + re.escape(_prefix) + r':[A-Za-z_][\w.-]*'
        r'(?:="[^"]*"|=\'[^\']*\')',
        repl='', flags=0,
    )

# 6. Deprecated <svg> root attributes
for _attr in [
    r'overflow',           # only ever "visible" on svg root in these files
    r'enable-background',
    r'xml:space',
]:
    _sub(r'\s+' + _attr + r'(?:="[^"]*"|=\'[^\']*\')', repl='', flags=0)

# 7. Namespace declarations to drop
for _ns in [
    r'xmlns:x\b',
    r'xmlns:sodipodi',
    r'xmlns:inkscape',
    r'xmlns:rdf',
    r'xmlns:dc\b',
    r'xmlns:i\b',
    r'xmlns:a\b',
    r'xmlns:ns\b',
    r'xmlns:ns0\b',
    r'xmlns:xap\b',
    r'xmlns:xapGImg',
    r'xmlns:svg\b',
]:
    _sub(r'\s+' + _ns + r'(?:="[^"]*"|=\'[^\']*\')', repl='', flags=0)

# Collapse runs of 3+ blank lines left by removals
_sub(r'\n{3,}', repl='\n\n')


def strip(text: str) -> str:
    for pattern, repl in _SUBS:
        text = pattern.sub(repl, text)
    return text.strip() + '\n'


# ---------------------------------------------------------------------------
# Optional: rewrite viewBox / width / height to the drawing's true visual
# bounding box, using Inkscape's headless renderer.
# ---------------------------------------------------------------------------

_INKSCAPE_CANDIDATES = [
    os.environ.get('INKSCAPE') or '',
    '/Applications/Inkscape.app/Contents/MacOS/inkscape',
    'inkscape',
]


def _find_inkscape() -> str | None:
    for c in _INKSCAPE_CANDIDATES:
        if not c:
            continue
        if os.path.sep in c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def _query_bbox(inkscape: str, path: pathlib.Path) -> tuple[float, float, float, float]:
    """Return (x, y, w, h) of the SVG's top-level content bbox in user units."""
    out = subprocess.run(
        [inkscape, '--query-x', '--query-y', '--query-width', '--query-height', str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    x, y, w, h = (float(v) for v in out[:4])
    return x, y, w, h


_VIEWBOX_RE = re.compile(r'\sviewBox\s*=\s*"[^"]*"')
_WIDTH_RE = re.compile(r'\swidth\s*=\s*"[^"]*"')
_HEIGHT_RE = re.compile(r'\sheight\s*=\s*"[^"]*"')
_SVG_OPEN_RE = re.compile(r'<svg\b[^>]*>', re.DOTALL)


def fit_viewbox(svg_path: pathlib.Path, inkscape: str) -> tuple[float, float, bool] | None:
    """Shrink the <svg> viewBox to Inkscape's queried content bbox.
    Only applied when the queried bbox is smaller than the current viewBox —
    otherwise (e.g. arrow markers with overflow:visible inflating the query)
    the existing viewBox is left untouched.
    Returns (width, height, was_fitted) or None on error."""
    try:
        x, y, w, h = _query_bbox(inkscape, svg_path)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f'  ! bbox query failed for {svg_path.name}: {e}', file=sys.stderr)
        return None
    if w <= 0 or h <= 0:
        return None
    text = svg_path.read_text(encoding='utf-8')
    m = _SVG_OPEN_RE.search(text)
    if not m:
        return None
    tag = m.group(0)
    # Refuse to expand the viewBox: if the queried bbox is larger than the
    # current viewBox in either dimension, keep the source viewBox as-is.
    vb_match = re.search(r'viewBox\s*=\s*"\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*"', tag)
    if vb_match:
        cur_w = float(vb_match.group(3))
        cur_h = float(vb_match.group(4))
        if w > cur_w * 1.001 or h > cur_h * 1.001:
            return cur_w, cur_h, False  # kept source viewBox
    new_vb = f' viewBox="{x:g} {y:g} {w:g} {h:g}"'
    new_w = f' width="{w:g}"'
    new_h = f' height="{h:g}"'
    tag = _VIEWBOX_RE.sub('', tag)
    tag = _WIDTH_RE.sub('', tag)
    tag = _HEIGHT_RE.sub('', tag)
    # Collapse any blank / whitespace-only lines the removals left behind.
    tag = re.sub(r'\n[ \t]*(?=\n)', '', tag)
    tag = tag[:4] + new_vb + new_w + new_h + tag[4:]  # insert after "<svg"
    text = text[:m.start()] + tag + text[m.end():]
    svg_path.write_text(text, encoding='utf-8')
    return w, h, True


def sync_symbols_js(js_path: pathlib.Path, basename: str,
                    w: float, h: float) -> bool:
    """Rewrite w/h in any DEFAULT_SYMBOL_DEFS entry whose href matches basename.
    Returns True if the file was modified."""
    text = js_path.read_text(encoding='utf-8')
    # Match: href: '/symbols/<basename>', w: <num>, h: <num>
    # Capture the "href..., w: " prefix and the ", h: " separator so we can
    # rewrite only the numeric fields. displayH (which follows) is untouched.
    pattern = re.compile(
        r"(href:\s*'/symbols/" + re.escape(basename) + r"'\s*,\s*w:\s*)"
        r"[-\d.eE+]+"
        r"(\s*,\s*h:\s*)"
        r"[-\d.eE+]+"
    )
    replacement = rf"\g<1>{w:g}\g<2>{h:g}"
    new_text, n = pattern.subn(replacement, text)
    if n == 0:
        return False
    js_path.write_text(new_text, encoding='utf-8')
    return True


_AVAILABLE_RE = re.compile(
    r"(export\s+const\s+AVAILABLE_SYMBOLS\s*=\s*\[)([^\]]*?)(\])",
    re.DOTALL,
)


def register_in_available_symbols(js_path: pathlib.Path, basename: str) -> bool:
    """Insert basename into AVAILABLE_SYMBOLS (sorted, 4 per line).
    Returns True if the file was modified (i.e. it wasn't already listed)."""
    text = js_path.read_text(encoding='utf-8')
    m = _AVAILABLE_RE.search(text)
    if not m:
        return False
    existing = re.findall(r"'([^']+\.svg)'", m.group(2))
    if basename in existing:
        return False
    names = sorted(set(existing + [basename]))
    # Wrap 4 names per line to match the existing formatting.
    lines = []
    for i in range(0, len(names), 4):
        chunk = ",".join(f"'{n}'" for n in names[i:i + 4])
        lines.append("  " + chunk + ",")
    body = "\n" + "\n".join(lines) + "\n"
    new_text = text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]
    js_path.write_text(new_text, encoding='utf-8')
    return True


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    out_path = None
    out_dir = None
    fit = False
    sync_js = None

    if '-o' in args:
        idx = args.index('-o')
        out_path = pathlib.Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if '--out-dir' in args:
        idx = args.index('--out-dir')
        out_dir = pathlib.Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
        out_dir.mkdir(parents=True, exist_ok=True)

    if '--sync-symbols-js' in args:
        idx = args.index('--sync-symbols-js')
        sync_js = pathlib.Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if '--fit-viewbox' in args:
        fit = True
        args = [a for a in args if a != '--fit-viewbox']

    inkscape = _find_inkscape() if fit else None
    if fit and not inkscape:
        print('  ! --fit-viewbox requested but Inkscape not found; skipping fit',
              file=sys.stderr)

    for src in args:
        p = pathlib.Path(src)
        original = p.read_text(encoding='utf-8')
        result = strip(original)
        if out_path is not None:
            dest = out_path
        elif out_dir is not None:
            dest = out_dir / p.name
        else:
            dest = p
        dest.write_text(result, encoding='utf-8')
        saved = len(original.encode()) - len(result.encode())
        line = f'  {p.name}  {len(original.encode()):,} → {len(result.encode()):,} bytes  (-{saved:,})'
        if fit and inkscape:
            result = fit_viewbox(dest, inkscape)
            if result:
                w, h, fitted = result
                line += f'  viewBox={w:g}×{h:g}'
                line += ' (fitted)' if fitted else ' (kept source)'
                if sync_js is not None:
                    if sync_symbols_js(sync_js, p.name, w, h):
                        line += '  symbols.js synced'
                    if register_in_available_symbols(sync_js, p.name):
                        line += '  AVAILABLE_SYMBOLS +'
        print(line)


if __name__ == '__main__':
    main()
