// ── Library symbol definitions ──────────────────────────────────────────────
// Each entry: { href, w, h, displayH, orientation? }
// displayH: target rendered height in SVG canvas pixels
// orientation: additional fixed rotation (degrees) applied to the symbol
const MIR   = { href: '/symbols/b-mir.svg',   w: 10.671, h: 29.096 }
const BSP   = { href: '/symbols/b-bsp.svg',   w: 23.427, h: 23.427 }
const WPYEL = { href: '/symbols/b-wpyel.svg', w: 5,      h: 23.428 }
const WPRED = { href: '/symbols/b-wpred.svg', w: 5.002,  h: 23.428 }
const LENS1 = { href: '/symbols/b-lens1.svg', w: 6.418,  h: 23.426 }
const PD1   = { href: '/symbols/e-pd1.svg',   w: 16.34,  h: 23.428 }

export const DEFAULT_SYMBOL_DEFS = {
  // Fiber couplers (glob match: "fiber: *")
  'fiber: *': { href: '/symbols/b-coupler.svg', w: 17.754, h: 23.427, displayH: 18 },

  // Mirrors
  'mirror':               { ...MIR, displayH: 11 },
  'large mirror':         { ...MIR, displayH: 14 },
  'small mirror':         { ...MIR, displayH: 9  },
  'tall mirror':          { ...MIR, displayH: 14 },
  'eo2 mirror':           { ...MIR, displayH: 11 },
  'eo3 mirror':           { ...MIR, displayH: 11 },
  'silver mirror':        { ...MIR, displayH: 11 },
  '1064 mirror':          { ...MIR, displayH: 11 },
  'dichroic mirror':      { ...MIR, displayH: 11 },
  'small dichroic mirror':{ ...MIR, displayH: 9  },
  'periscope mirror':     { ...MIR, displayH: 11 },
  'quadrant mirror':      { ...MIR, displayH: 11 },
  '2 inch eo2 mirror':    { ...MIR, displayH: 14 },

  // PBS
  'pbs':                  { ...BSP, displayH: 4.5 },
  'flat pbs':             { ...BSP, displayH: 4.5 },
  'large pbs':            { ...BSP, displayH: 6   },
  'beam sampler':         { ...BSP, displayH: 4.5 },
  '50-50 beam splitter':  { ...BSP, displayH: 4.5 },

  // Waveplates
  'waveplate':                          { ...WPYEL, displayH: 9 },
  'half waveplate':                     { ...WPYEL, displayH: 9 },
  'double waveplate':                   { ...WPYEL, displayH: 9 },
  'tall waveplate':                     { ...WPYEL, displayH: 11 },
  '671 half waveplate':                 { ...WPYEL, displayH: 9 },
  '671 hwp':                            { ...WPYEL, displayH: 9 },
  '852 hwp':                            { ...WPYEL, displayH: 9 },
  'qwp':                                { ...WPRED, displayH: 9 },
  'quarter waveplate':                  { ...WPRED, displayH: 9 },
  '671 qwp':                            { ...WPRED, displayH: 9 },
  'waveplate & polarizer in front of camera': { ...WPYEL, displayH: 9 },

  // Lenses
  'lens':                  { ...LENS1, displayH: 9 },
  'convex rectangular lens':{ ...LENS1, displayH: 9 },
  'telescope lens tube':   { ...LENS1, displayH: 11 },

  // Detectors
  'photodetector':        { ...PD1, displayH: 16 },

  // Homemade symbols
  'iris':           { href: '/symbols/h-iris.svg',       w: 5.62024,     h: 29.0104, displayH: 11 },
  'lens tube':      { href: '/symbols/h-lenstube.svg',   w: 37.4545, h: 23.428, displayH: 9  },
  'fiber coupler':  { href: '/symbols/h-fibercoupl.svg', w: 63.463, h: 39.599, displayH: 12 },
  'shutter':        { href: '/symbols/h-shutter.svg',    w: 7.6019, h: 1.14803,  displayH: 6  },
}

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
  'h-fibercoupl.svg','h-iris.svg','h-lenstube.svg','h-shutter.svg',
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
