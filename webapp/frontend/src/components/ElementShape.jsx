// SVG shapes for optical element types.
// Shapes using library SVGs are centered at (0,0) via x/y offsets.
// Fallback geometric shapes are used for types without a library symbol.

// ── Library symbol definitions ──────────────────────────────────────────────
// Each entry: { href, w, h, displayH }
// displayH: target rendered height in SVG canvas pixels
const MIR   = { href: '/symbols/b-mir.svg',   w: 10.671, h: 29.096 }
const BSP   = { href: '/symbols/b-bsp.svg',   w: 23.427, h: 23.427 }
const WPYEL = { href: '/symbols/b-wpyel.svg', w: 5,      h: 23.428 }
const WPRED = { href: '/symbols/b-wpred.svg', w: 5.002,  h: 23.428 }
const LENS1 = { href: '/symbols/b-lens1.svg', w: 6.418,  h: 23.426 }
const PD1   = { href: '/symbols/e-pd1.svg',   w: 16.34,  h: 23.428 }

export const DEFAULT_SYMBOL_DEFS = {
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
}

export const FIBER_SYMBOL = { href: '/symbols/b-coupler.svg', w: 17.754, h: 23.427, displayH: 18 }

// ── Fallback geometric shapes ────────────────────────────────────────────────
const R = 4

function BeamDump({ selected }) {
  return <circle r={R} fill={selected ? '#ff6b6b' : '#bf616a'} />
}
function Post({ selected }) {
  return <circle r={R * 0.5} fill="none" stroke={selected ? '#fff' : '#4c566a'} strokeWidth={1.5} />
}
function Iris({ selected }) {
  return (
    <g>
      <circle r={R} fill="none" stroke={selected ? '#fff' : '#81a1c1'} strokeWidth={1.5} />
      <circle r={R * 0.4} fill="none" stroke={selected ? '#fff' : '#81a1c1'} strokeWidth={1} />
    </g>
  )
}
function Unknown({ selected }) {
  return (
    <circle r={R * 0.6}
      fill={selected ? '#fff4' : '#2a3a4a'}
      stroke={selected ? '#fff' : '#4a6a8a'} strokeWidth={1} />
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
function SymbolImage({ def, selected }) {
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
          fill="none" stroke="#fff8" strokeWidth={1} strokeDasharray="3 2" rx={1}
        />
      )}
    </>
  )
}

// ── Main export ──────────────────────────────────────────────────────────────
export default function ElementShape({ type, orientation, selected, symbolDefs }) {
  const defs = symbolDefs ?? DEFAULT_SYMBOL_DEFS
  const normalized = (type || '').toLowerCase().trim()
  const angle = orientation || 0

  if (normalized.startsWith('fiber:')) {
    return (
      <g transform={`rotate(${-angle})`}>
        <SymbolImage def={FIBER_SYMBOL} selected={selected} />
      </g>
    )
  }

  const symDef = defs[normalized]
  if (symDef) {
    return (
      <g transform={`rotate(${-angle})`}>
        <SymbolImage def={symDef} selected={selected} />
      </g>
    )
  }

  const FallbackComponent = FALLBACK_SHAPES[normalized] || Unknown
  return (
    <g transform={`rotate(${-angle})`}>
      <FallbackComponent selected={selected} />
      {selected && <circle r={R + 3} fill="none" stroke="#fff8" strokeWidth={1} strokeDasharray="3 2" />}
    </g>
  )
}
