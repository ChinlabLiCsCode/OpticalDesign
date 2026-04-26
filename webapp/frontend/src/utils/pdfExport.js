import jsPDF from 'jspdf'
import { svg2pdf } from 'svg2pdf.js'

// Replace every <image href="*.svg"> with the symbol's inline SVG paths.
// This produces a fully vector PDF — no rasterisation of optics symbols.
async function inlineSVGImages(rootEl) {
  const cache = {}

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

    ;[...srcSvg.childNodes].forEach(node => g.appendChild(node.cloneNode(true)))
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

export async function exportSVGToPDF(svgEl, svgW, svgH) {
  const clone = svgEl.cloneNode(true)
  clone.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`)
  clone.setAttribute('width',  String(svgW))
  clone.setAttribute('height', String(svgH))

  // Remove pan/zoom transform from the top-level <g>
  const outerG = clone.querySelector(':scope > g')
  if (outerG) outerG.removeAttribute('transform')

  // Inline all symbol SVGs so the PDF is fully vector
  await inlineSVGImages(clone)

  // Inject font override via embedded <style> so svg2pdf's own stylesheet parser
  // resolves 'sans-serif' -> its built-in 'helvetica' alias (case-sensitive lookup fails otherwise)
  const styleEl = document.createElementNS('http://www.w3.org/2000/svg', 'style')
  styleEl.textContent = 'text { font-family: sans-serif }'
  clone.insertBefore(styleEl, clone.firstChild)

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
