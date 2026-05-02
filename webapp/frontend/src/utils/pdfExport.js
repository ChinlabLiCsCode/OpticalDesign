import jsPDF from 'jspdf'
import { svg2pdf } from 'svg2pdf.js'

// Adobe Illustrator generates the same IDs (XMLID_1_, XMLID_2_, …) in every SVG it
// exports. When multiple symbols are inlined into one document, those IDs collide and
// svg2pdf uses the first gradient it finds for every reference. Fix: stamp each
// inlined symbol instance with a unique prefix on all IDs and url() references.
function prefixIds(el, prefix) {
  if (el.hasAttribute('id'))
    el.setAttribute('id', prefix + el.getAttribute('id'))
  for (const attr of [...el.attributes]) {
    if (attr.value.includes('url(#'))
      el.setAttribute(attr.name, attr.value.replace(/url\(#([^)]+)\)/g, `url(#${prefix}$1)`))
    if ((attr.name === 'href' || attr.name === 'xlink:href') && attr.value.startsWith('#'))
      el.setAttribute(attr.name, '#' + prefix + attr.value.slice(1))
  }
  for (const child of el.children) prefixIds(child, prefix)
}

// Strip comment/text nodes — svg2pdf crashes on non-Element nodes (.tagName.toLowerCase()).
// Preserve text nodes only inside <text>/<tspan>/<style> (label content + font CSS).
function stripNonElements(el) {
  const keepText = /^(text|tspan|style)$/i.test(el.tagName)
  for (const child of [...el.childNodes]) {
    if (child.nodeType === Node.ELEMENT_NODE) stripNonElements(child)
    else if (!keepText || child.nodeType !== Node.TEXT_NODE) el.removeChild(child)
  }
}

// Replace every <image href="*.svg"> with the symbol's inline SVG paths.
// This produces a fully vector PDF — no rasterisation of optics symbols.
async function inlineSVGImages(rootEl) {
  const cache = {}
  let instanceCount = 0

  await Promise.all([...rootEl.querySelectorAll('image')].map(async img => {
    const href = img.getAttribute('href') || img.getAttribute('xlink:href') || ''
    if (!href) return

    const abs = href.startsWith('/') ? `${window.location.origin}${href}` : href
    if (!cache[abs]) {
      try {
        const text = await fetch(abs).then(r => r.text())
        const doc  = new DOMParser().parseFromString(text, 'image/svg+xml')
        const svg  = doc.documentElement
        // Promote stop-color/stop-opacity from style="" to presentation attributes
        // once on first load. Browsers may strip SVG-specific CSS properties when
        // elements are adopted from a parsed SVG document into an HTML document.
        svg.querySelectorAll('stop').forEach(stop => {
          const s = stop.getAttribute('style') || ''
          const color   = s.match(/stop-color\s*:\s*([^;]+)/)?.[1]?.trim()
          const opacity = s.match(/stop-opacity\s*:\s*([^;]+)/)?.[1]?.trim()
          if (color)   stop.setAttribute('stop-color',   color)
          if (opacity) stop.setAttribute('stop-opacity', opacity)
        })
        cache[abs] = svg
      } catch { return }
    }

    const srcSvg = cache[abs]
    if (!srcSvg || srcSvg.tagName !== 'svg') return

    // Natural dimensions from viewBox or width/height attributes
    let sw, sh
    const vb = srcSvg.getAttribute('viewBox')
    if (vb) {
      const p = vb.trim().split(/\s+/)
      sw = parseFloat(p[2]); sh = parseFloat(p[3])
    }
    sw = sw || parseFloat(srcSvg.getAttribute('width'))  || 10
    sh = sh || parseFloat(srcSvg.getAttribute('height')) || 10

    // Desired placement from the <image> element
    const ix = parseFloat(img.getAttribute('x')      ?? 0)
    const iy = parseFloat(img.getAttribute('y')      ?? 0)
    const iw = parseFloat(img.getAttribute('width')  ?? sw)
    const ih = parseFloat(img.getAttribute('height') ?? sh)

    // Build a <g> that maps the symbol's coordinate space onto the image's placement.
    // Use uniform scale (meet) + center offset to match SVG's default preserveAspectRatio.
    const scale   = Math.min(iw / sw, ih / sh)
    const offsetX = ix + (iw - sw * scale) / 2
    const offsetY = iy + (ih - sh * scale) / 2
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    g.setAttribute('transform', `translate(${offsetX},${offsetY}) scale(${scale})`)

    const opacity = img.getAttribute('opacity')
    if (opacity) g.setAttribute('opacity', opacity)

    const prefix = `i${instanceCount++}_`
    ;[...srcSvg.childNodes]
      .filter(n => n.nodeType === Node.ELEMENT_NODE)
      .forEach(node => {
        const clone = node.cloneNode(true)
        stripNonElements(clone)
        prefixIds(clone, prefix)
        g.appendChild(clone)
      })
    img.parentNode.replaceChild(g, img)
  }))
}

async function triggerSave(blob, name, mime, ext) {
  if ('showSaveFilePicker' in window) {
    try {
      const h = await window.showSaveFilePicker({
        suggestedName: name,
        types: [{ description: ext.toUpperCase(), accept: { [mime]: ['.' + ext] } }],
      })
      const w = await h.createWritable()
      await w.write(blob); await w.close()
      return
    } catch (e) { if (e.name === 'AbortError') return }
  }
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = name; a.click()
  URL.revokeObjectURL(url)
}

export async function exportSVGToPDF(svgEl, svgW, svgH, zoomScale = 1, pdfFontSize = 4) {
  const clone = svgEl.cloneNode(true)
  clone.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`)
  clone.setAttribute('width',  String(svgW))
  clone.setAttribute('height', String(svgH))

  // Remove pan/zoom transform from the top-level <g>
  const outerG = clone.querySelector(':scope > g')
  if (outerG) outerG.removeAttribute('transform')

  // Strip React comment nodes before inlining (runs on small tree; symbol SVG comments
  // are stripped per-clone inside inlineSVGImages)
  stripNonElements(clone)

  // Inline all symbol SVGs so the PDF is fully vector
  await inlineSVGImages(clone)

  // Inject font override via embedded <style> so svg2pdf's own stylesheet parser
  // resolves 'sans-serif' -> its built-in 'helvetica' alias (case-sensitive lookup fails otherwise)
  const styleEl = document.createElementNS('http://www.w3.org/2000/svg', 'style')
  styleEl.textContent = 'text { font-family: sans-serif }'
  clone.insertBefore(styleEl, clone.firstChild)

  // Normalise zoom-relative text sizes and offsets.
  // React stores fontSize as inline CSS (element.style.fontSize), not as a DOM attribute,
  // so getAttribute('font-size') returns null. We set a fixed intrinsic size directly
  // and remove any inline style override so svg2pdf sees a consistent value.
  // Negative y-offsets are element labels sitting above their symbol; they were
  // computed as -N/zoomScale so multiply by zoomScale to recover intrinsic values.
  clone.querySelectorAll('text').forEach(t => {
    t.setAttribute('font-size', pdfFontSize)
    t.style.removeProperty('font-size')
    const y = parseFloat(t.getAttribute('y') || '0')
    if (y < 0) t.setAttribute('y', y * zoomScale)
  })

  // Temporarily mount off-screen (svg2pdf requires the element to be in the DOM)
  clone.style.cssText = 'position:absolute;left:-99999px;top:0'
  document.body.appendChild(clone)

  const MM_PER_PX = 25.4 / 96
  const wMm = svgW * MM_PER_PX
  const hMm = svgH * MM_PER_PX

  const doc = new jsPDF({ orientation: wMm > hMm ? 'l' : 'p', unit: 'mm', format: [wMm, hMm] })

  try {
    await svg2pdf(clone, doc, { x: 0, y: 0, width: wMm, height: hMm })
  } finally {
    document.body.removeChild(clone)
  }

  await triggerSave(doc.output('blob'), 'optical_layout.pdf', 'application/pdf', 'pdf')
}
