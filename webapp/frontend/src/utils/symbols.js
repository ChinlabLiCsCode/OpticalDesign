export const AVAILABLE_SYMBOLS = [
  'b-bsp.svg','b-bspcube.svg','b-coupler.svg','b-credit.svg',
  'b-crystalcc.svg','b-crystalfc.svg','b-crystalff.svg','b-diccube.svg',
  'b-dicgrn.svg','b-dicred.svg','b-dump.svg','b-grat.svg',
  'b-lens1.svg','b-lens2.svg','b-lens3.svg','b-mir.svg',
  'b-mirc.svg','b-mircpzt.svg','b-mirpzt.svg','b-npro.svg',
  'b-phase.svg','b-wpgn.svg','b-wpred.svg','b-wpyel.svg',
  'c-aom.svg','c-diodegrn.svg','c-eom1.svg','c-eom2.svg',
  'c-fiber.svg','c-fibercoupl.svg','c-flip.svg','c-isolator.svg',
  'c-laser1.svg','c-laser2.svg','c-mirpzt3ax.svg','c-modeclean.svg',
  'c-modecleanpzt.svg','c-opacc.svg','c-opaccplates.svg','c-opacfplates.svg',
  'c-opafc.svg','c-opaff.svg','c-opaffplates.svg','c-opakerr.svg',
  'c-opared.svg','c-rotator.svg','e-amp.svg','e-computer.svg',
  'e-diff.svg','e-frq1.svg','e-frq2.svg','e-hipass.svg',
  'e-hvampleft.svg','e-hvampright.svg','e-lopass.svg','e-mix.svg',
  'e-pd1.svg','e-pd2.svg','e-pdgrn1.svg','e-pdgrn2.svg',
  'e-qpd.svg','e-servoleft.svg','e-servoright.svg','e-spekki.svg',
  'e-sum.svg','e-sumdiff.svg','e-wincam.svg',
  'h-iris.svg','h-lenstube.svg',
]

// Convert any CSS color (name or hex) to a hex string for <input type="color">
const _cvs = typeof document !== 'undefined' ? document.createElement('canvas') : null
if (_cvs) { _cvs.width = 1; _cvs.height = 1 }

export function colorToHex(color) {
  if (!_cvs) return '#888888'
  if (color && /^#[0-9a-fA-F]{6}$/.test(color)) return color
  try {
    const ctx = _cvs.getContext('2d')
    ctx.clearRect(0, 0, 1, 1)
    ctx.fillStyle = color
    ctx.fillRect(0, 0, 1, 1)
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
    return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`
  } catch { return '#888888' }
}
