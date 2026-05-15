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
5.  inkscape:collect attr        Inkscape internal link bookkeeping
6.  i:knockout attr              Illustrator compositing hint; non-standard
7.  i:layer / i:dimmedPercent /
    i:rgbTrio attrs              Illustrator layer metadata
8.  Adobe <svg> root attrs       i:viewOrigin, i:rulerOrigin, i:pageBounds
9.  Inkscape <svg> root attrs    sodipodi:docname, inkscape:version
10. Deprecated <svg> root attrs  overflow="visible", enable-background,
                                 xml:space="preserve"
11. Namespace declarations       sodipodi, inkscape, rdf, dc, i (Illustrator),
                                 a (AdobeSVGViewerExtensions), ns (Variables),
                                 ns0 (SaveForWeb), xap, xapGImg, svg (redundant),
                                 x (adobe meta)

Namespaces retained
-------------------
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"   (needed for xlink:href)

Usage
-----
    # Modify files in-place (one or more):
    python3 strip_svg_metadata.py symbols/h-iris.svg symbols/h-lenstube.svg

    # Write to a new file:
    python3 strip_svg_metadata.py input.svg -o output.svg
"""

import re
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

# 5–7. Per-element attributes (non-visual, from any element)
for _attr in [
    r'inkscape:collect',
    r'i:knockout',
    r'i:layer',
    r'i:dimmedPercent',
    r'i:rgbTrio',
]:
    _sub(r'\s+' + _attr + r'(?:="[^"]*"|=\'[^\']*\')', repl='', flags=0)

# 8–10. <svg> root attributes (non-visual presentation / editor state)
for _attr in [
    r'i:viewOrigin',
    r'i:rulerOrigin',
    r'i:pageBounds',
    r'sodipodi:docname',
    r'inkscape:version',
    r'overflow',           # only ever "visible" on svg root in these files
    r'enable-background',
    r'xml:space',
]:
    _sub(r'\s+' + _attr + r'(?:="[^"]*"|=\'[^\']*\')', repl='', flags=0)

# 11. Namespace declarations to drop
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


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    out_path = None
    if '-o' in args:
        idx = args.index('-o')
        out_path = pathlib.Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    for src in args:
        p = pathlib.Path(src)
        original = p.read_text(encoding='utf-8')
        result = strip(original)
        dest = out_path or p
        dest.write_text(result, encoding='utf-8')
        saved = len(original.encode()) - len(result.encode())
        print(f'  {p.name}  {len(original.encode()):,} → {len(result.encode()):,} bytes  (-{saved:,})')


if __name__ == '__main__':
    main()
