// SVG shapes for optical element types.
// Shapes using library SVGs are centered at (0,0) via x/y offsets.
// Fallback geometric shapes are used for types without a library symbol.

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
  'lens tube':             { ...LENS1, displayH: 9 },
  'telescope lens tube':   { ...LENS1, displayH: 11 },

  // Detectors
  'photodetector':        { ...PD1, displayH: 16 },

  // Homemade symbols
  'iris':      { href: '/symbols/h-iris.svg',     w: 11,     h: 28.967, displayH: 11 },
  'lens tube': { href: '/symbols/h-lenstube.svg', w: 37.601, h: 23.428, displayH: 9  },
}

// ── Symbol lookup with glob-wildcard fallback ────────────────────────────────
// Keys in defs are tried as exact match first, then as glob patterns (* → .*)
function lookupSymbolDef(defs, normalized) {
  if (defs[normalized] !== undefined) return defs[normalized]
  for (const [key, def] of Object.entries(defs)) {
    try {
      const pattern = key
        .replace(/[.+?^${}()|[\]\\]/g, '\\$&') // escape regex specials
        .replace(/\*/g, '.*')                    // * becomes wildcard
      if (new RegExp(`^${pattern}$`, 'i').test(normalized)) return def
    } catch { continue }
  }
  return null
}

// ── Fallback geometric shapes ────────────────────────────────────────────────
const R = 4

function BeamDump({ selected }) {
  return <circle r={R} fill={selected ? '#ff6b6b' : '#bf616a'} />
}
function Post({ selected, selColor }) {
  return <circle r={R * 0.5} fill="none" stroke={selected ? selColor : '#4c566a'} strokeWidth={1.5} />
}
function Iris({ selected, selColor }) {
  return (
    <g>
      <circle r={R} fill="none" stroke={selected ? selColor : '#81a1c1'} strokeWidth={1.5} />
      <circle r={R * 0.4} fill="none" stroke={selected ? selColor : '#81a1c1'} strokeWidth={1} />
    </g>
  )
}
function Unknown({ selected, selColor }) {
  return (
    <circle r={R * 0.6}
      fill={selected ? `${selColor}44` : '#2a3a4a'}
      stroke={selected ? selColor : '#4a6a8a'} strokeWidth={1} />
  )
}

const FALLBACK_SHAPES = {
  'beam dump':               BeamDump,
  'water-cooled beam dump':  BeamDump,
  post:                      Post,
  iris:                      Iris,
  'generic circle':          Unknown,
}

// ── SVG image helper ─────────────────────────────────────────────────────────
function SymbolImage({ def, selected, dark }) {
  const dH = def.displayH
  const dW = (def.w / def.h) * dH
  return (
    <>
      <image
        href={def.href}
        x={-dW / 2} y={-dH / 2}
        width={dW} height={dH}
        style={{ imageRendering: 'crisp-edges' }}
      />
      {selected && (
        <rect
          x={-dW / 2 - 2} y={-dH / 2 - 2}
          width={dW + 4} height={dH + 4}
          fill="none" stroke={dark ? '#fff8' : '#0007'} strokeWidth={1} strokeDasharray="3 2" rx={1}
        />
      )}
    </>
  )
}

// ── Main export ──────────────────────────────────────────────────────────────
export default function ElementShape({ type, orientation, selected, symbolDefs, dark = false }) {
  const defs = symbolDefs ?? DEFAULT_SYMBOL_DEFS
  const normalized = (type || '').toLowerCase().trim()
  const angle = orientation || 0
  const selColor = dark ? '#fff' : '#1a2a3a'

  const symDef = lookupSymbolDef(defs, normalized)
  if (symDef) {
    return (
      <g transform={`rotate(${180 - angle + (symDef.orientation ?? 0)})`}>
        <SymbolImage def={symDef} selected={selected} dark={dark} />
      </g>
    )
  }

  const FallbackComponent = FALLBACK_SHAPES[normalized] || Unknown
  return (
    <g transform={`rotate(${180 - angle})`}>
      <FallbackComponent selected={selected} selColor={selColor} />
      {selected && <circle r={R + 3} fill="none" stroke={`${selColor}88`} strokeWidth={1} strokeDasharray="3 2" />}
    </g>
  )
}
