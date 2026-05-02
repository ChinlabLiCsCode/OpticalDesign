import jsPDF from 'jspdf'
import { svg2pdf } from 'svg2pdf.js'

// Replace every <image href="*.svg"> with the symbol's inline SVG paths.
// This produces a fully vector PDF — no rasterisation of optics symbols.
// <defs> from each symbol (gradients, patterns) are hoisted to a root-level
// <defs> so svg2pdf can resolve gradient references regardless of nesting depth.
async function inlineSVGImages(rootEl) {
  const cache = {}

  // Ensure there's a root <defs> for hoisted gradient/pattern definitions
  let rootDefs = rootEl.querySelector(':scope > defs')
  if (!rootDefs) {
    rootDefs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    rootEl.insertBefore(rootDefs, rootEl.firstChild)
  }

  await Promise.all([...rootEl.querySelectorAll('image')].map(async img => {
    const href = img.getAttribute('href') || img.getAttribute('xlink:href') || ''
    if (!href) return

    const abs = href.startsWith('/') ? `${window.location.origin}${href}` : href
    if (!cache[abs]) {
      try {
        const text = await fetch(abs).then(r => r.text())
        const doc  = new DOMParser().parseFromString(text, 'image/svg+xml')
        cache[abs] = doc.documentElement
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

    ;[...srcSvg.childNodes]
      .filter(n => n.nodeType === Node.ELEMENT_NODE)
      .forEach(node => {
        if (/^defs$/i.test(node.tagName)) {
          // Hoist gradient/pattern defs to root so svg2pdf resolves url() references
          ;[...node.childNodes]
            .filter(n => n.nodeType === Node.ELEMENT_NODE)
            .forEach(def => rootDefs.appendChild(def.cloneNode(true)))
        } else {
          g.appendChild(node.cloneNode(true))
        }
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

  // Inline all symbol SVGs so the PDF is fully vector
  await inlineSVGImages(clone)

  // Hoist all gradient/pattern paint servers to root <defs>.
  // These SVGs define gradients directly inside <g> elements (valid SVG, but
  // svg2pdf only resolves url() references when the target is in <defs>).
  // appendChild moves existing nodes, so no cloning or ID patching needed.
  let rootDefs = clone.querySelector(':scope > defs')
  if (!rootDefs) {
    rootDefs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    clone.insertBefore(rootDefs, clone.firstChild)
  }
  clone.querySelectorAll('linearGradient, radialGradient, pattern').forEach(el => {
    if (el.parentNode !== rootDefs) rootDefs.appendChild(el)
  })

  // Inject font override via embedded <style> so svg2pdf's own stylesheet parser
  // resolves 'sans-serif' -> its built-in 'helvetica' alias (case-sensitive lookup fails otherwise)
  const styleEl = document.createElementNS('http://www.w3.org/2000/svg', 'style')
  styleEl.textContent = 'text { font-family: sans-serif }'
  clone.insertBefore(styleEl, clone.firstChild)

  // svg2pdf calls .tagName.toLowerCase() on every node and crashes on non-Element
  // nodes. React inserts comment nodes as conditional-render placeholders in the
  // live DOM; cloneNode captures them. Strip all non-Element nodes except text
  // nodes inside <text>/<tspan>/<style> (label content and font override CSS).
  function stripNonElements(el) {
    const keepText = /^(text|tspan|style)$/i.test(el.tagName)
    for (const child of [...el.childNodes]) {
      if (child.nodeType === Node.ELEMENT_NODE) stripNonElements(child)
      else if (!keepText || child.nodeType !== Node.TEXT_NODE) el.removeChild(child)
    }
  }
  stripNonElements(clone)

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
