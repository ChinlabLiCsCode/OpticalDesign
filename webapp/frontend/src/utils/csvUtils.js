export const LASER_COLORS = {
  'li h imaging':      'magenta',
  'li eom':            'magenta',
  'li repump':         'lime',
  'li mot':            'purple',
  'cs h imaging':      'cyan',
  'cs h img':          'cyan',
  'li zeeman':         'red',
  'cs zeeman':         'blue',
  'cs mot':            'green',
  'cs v optical pump': 'navy',
  'cs h optical pump': 'hotpink',
  'rsc':               'coral',
  'otop':              'crimson',
  'dual color':        'violet',
  'bfl':               'cornflowerblue',
}

function parseCSVLine(line) {
  const fields = []
  let field = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { field += '"'; i++ }
      else { inQuotes = !inQuotes }
    } else if (ch === ',' && !inQuotes) {
      fields.push(field); field = ''
    } else {
      field += ch
    }
  }
  fields.push(field)
  return fields
}

// ── Elements ──────────────────────────────────────────────────────────────────

const ELEM_COL_ALIASES = {
  'label': 'label', 'o-number': 'label', 'o number': 'label',
  'type': 'type',
  'position x': 'x', 'pos x': 'x', 'x': 'x',
  'position y': 'y', 'pos y': 'y', 'y': 'y',
  'orientation': 'orientation', 'orient': 'orientation', 'angle': 'orientation',
}
const REQUIRED = ['label', 'type', 'x', 'y']

export function parseElementsCsv(text) {
  const allLines = text.split(/\r?\n/)

  let config = null
  const cfgLine = allLines.find(l => l.trimStart().startsWith('# config:'))
  if (cfgLine) {
    config = {}
    cfgLine.replace(/^.*# config:/, '').split(',').forEach(pair => {
      const [k, v] = pair.trim().split('=')
      if (k && v) config[k.trim()] = parseFloat(v.trim())
    })
  }

  const dataLines = allLines.filter(l => !l.trimStart().startsWith('#') && l.trim())
  if (dataLines.length === 0) return { elements: [], config, error: 'Empty file' }

  const headers = parseCSVLine(dataLines[0]).map(h => h.trim())
  const colIdx = {}
  const extraCols = []
  headers.forEach((h, i) => {
    const canonical = ELEM_COL_ALIASES[h.toLowerCase()]
    if (canonical && !(canonical in colIdx)) colIdx[canonical] = i
    else if (h) extraCols.push({ name: h, index: i })
  })

  const missing = REQUIRED.filter(k => !(k in colIdx))
  if (missing.length) return { elements: [], config, error: `Missing columns: ${missing.join(', ')}` }

  const elements = []
  for (let i = 1; i < dataLines.length; i++) {
    const row = parseCSVLine(dataLines[i])
    const label = (row[colIdx.label] ?? '').trim()
    if (!label) continue
    const xStr = (row[colIdx.x] ?? '').trim()
    const yStr = (row[colIdx.y] ?? '').trim()
    if (!xStr || !yStr) continue
    const x = parseFloat(xStr), y = parseFloat(yStr)
    if (isNaN(x) || isNaN(y)) continue
    const orientRaw = colIdx.orientation != null ? (row[colIdx.orientation] ?? '').trim() : ''
    const orientation = orientRaw ? (parseFloat(orientRaw) || 0) : 0
    // Normalize O-numbers: strip trailing ".0", prepend "O-" if purely numeric
    const rawLabel = label.replace(/\.0$/, '')
    const normalizedLabel = /^\d+(\.\d+)?$/.test(rawLabel) ? `O-${rawLabel}` : rawLabel
    const type = (row[colIdx.type] ?? '').trim()
    const meta = {}
    extraCols.forEach(({ name, index }) => {
      const v = (row[index] ?? '').trim(); if (v) meta[name] = v
    })
    elements.push({ label: normalizedLabel, type, x, y, orientation, ...meta })
  }

  if (!config && elements.length > 0) {
    const xs = elements.map(e => e.x), ys = elements.map(e => e.y)
    const pad = 4
    config = {
      table_length: Math.ceil(Math.max(...xs) - Math.min(...xs) + 2 * pad),
      table_width:  Math.ceil(Math.max(...ys) - Math.min(...ys) + 2 * pad),
      origin_x:     (Math.min(...xs) + Math.max(...xs)) / 2,
      origin_y:     (Math.min(...ys) + Math.max(...ys)) / 2,
    }
  }

  return { elements, config }
}

const CORE_KEYS = new Set(['label', 'type', 'x', 'y', 'orientation', 'id'])

function csvEscape(val) {
  const s = String(val ?? '')
  return s.includes(',') || s.includes('"') || s.includes('\n')
    ? `"${s.replace(/"/g, '""')}"` : s
}

export function serializeElementsCsv(elements, config) {
  if (!elements.length) return ''
  const extraKeys = []
  const seen = new Set()
  elements.forEach(el => Object.keys(el).forEach(k => {
    if (!CORE_KEYS.has(k) && !seen.has(k)) { seen.add(k); extraKeys.push(k) }
  }))
  const lines = []
  if (config) lines.push(`# config: ${Object.entries(config).map(([k, v]) => `${k}=${v}`).join(',')}`)
  lines.push(['Label', 'Type', 'Position x', 'Position y', 'Orientation', ...extraKeys].join(','))
  elements.forEach(el => {
    lines.push([el.label, el.type ?? '', el.x, el.y, el.orientation ?? 0,
      ...extraKeys.map(k => csvEscape(el[k] ?? ''))].join(','))
  })
  return lines.join('\n')
}

// ── Beam paths ────────────────────────────────────────────────────────────────
//
// CSV format: each path occupies two adjacent columns — "[Name] src" and "[Name] dest".
// Each data row is one directed edge. Empty rows are ignored.
//
// Example:
//   Li H Imaging src,Li H Imaging dest,Li MOT src,Li MOT dest
//   O-37,O-6,O-16,O-40
//   O-6,O-5,O-40,O-78

export function parseBeamPathsCsv(text) {
  const lines = text.split(/\r?\n/).filter(l => l.trim() && !l.trimStart().startsWith('#'))
  if (!lines.length) return { beamPaths: {} }

  const headers = parseCSVLine(lines[0]).map(h => h.trim())

  // Identify paths from " src" / " dest" column pairs
  const pathNames = []
  const srcIdx = {}, destIdx = {}
  headers.forEach((h, i) => {
    if (h.endsWith(' src'))  { const n = h.slice(0, -4).trim(); srcIdx[n]  = i; if (!pathNames.includes(n)) pathNames.push(n) }
    if (h.endsWith(' dest')) { const n = h.slice(0, -5).trim(); destIdx[n] = i; if (!pathNames.includes(n)) pathNames.push(n) }
  })

  const beamPaths = {}
  pathNames.forEach(name => {
    const si = srcIdx[name], di = destIdx[name]
    if (si == null || di == null) return
    const color = LASER_COLORS[name.toLowerCase()] ?? 'gray'
    const edges = []
    for (let i = 1; i < lines.length; i++) {
      const row = parseCSVLine(lines[i])
      const src  = (row[si] ?? '').trim()
      const dest = (row[di] ?? '').trim()
      if (src && dest) edges.push([src, dest])
    }
    beamPaths[name] = { color, edges }
  })

  return { beamPaths }
}

// ── Background objects ────────────────────────────────────────────────────────
//
// CSV format: one row per line segment, grouped by name.
//   Group,Color,StrokeWidth,x1,y1,x2,y2
//   blue outline,blue,4,-24.5,-40.5,2.5,-40.5

export function parseBgObjectsCsv(text) {
  const lines = text.split(/\r?\n/).filter(l => l.trim() && !l.trimStart().startsWith('#'))
  if (!lines.length) return { bgGroups: {} }

  const headers = parseCSVLine(lines[0]).map(h => h.trim().toLowerCase())
  const gi  = headers.indexOf('group')
  const ci  = headers.indexOf('color')
  const si  = headers.indexOf('strokewidth')
  const x1i = headers.indexOf('x1')
  const y1i = headers.indexOf('y1')
  const x2i = headers.indexOf('x2')
  const y2i = headers.indexOf('y2')
  if (gi < 0 || x1i < 0 || y1i < 0 || x2i < 0 || y2i < 0)
    return { bgGroups: {}, error: 'Missing required columns (Group, x1, y1, x2, y2)' }

  const bgGroups = {}
  for (let i = 1; i < lines.length; i++) {
    const row  = parseCSVLine(lines[i])
    const name = (row[gi] ?? '').trim()
    if (!name) continue
    const x1 = parseFloat(row[x1i] ?? ''), y1 = parseFloat(row[y1i] ?? '')
    const x2 = parseFloat(row[x2i] ?? ''), y2 = parseFloat(row[y2i] ?? '')
    if (isNaN(x1) || isNaN(y1) || isNaN(x2) || isNaN(y2)) continue
    if (!bgGroups[name]) {
      bgGroups[name] = {
        color:       (row[ci] ?? '').trim() || '#888888',
        strokeWidth: parseFloat(row[si] ?? '') || 2,
        edges: [],
      }
    }
    bgGroups[name].edges.push([x1, y1, x2, y2])
  }
  return { bgGroups }
}

export function serializeBgObjectsCsv(bgGroups) {
  const rows = ['Group,Color,StrokeWidth,x1,y1,x2,y2']
  Object.entries(bgGroups).forEach(([name, { color, strokeWidth, edges }]) => {
    edges.forEach(([x1, y1, x2, y2]) => {
      rows.push([csvEscape(name), color, strokeWidth, x1, y1, x2, y2].join(','))
    })
  })
  return rows.join('\n')
}

export function serializeBeamPathsCsv(beamPaths) {
  const names = Object.keys(beamPaths)
  if (!names.length) return ''

  // Header: alternating src/dest column pairs
  const header = names.flatMap(n => [`${n} src`, `${n} dest`]).join(',')

  // Collect all edge rows, one path at a time
  const edgesPerPath = names.map(n => beamPaths[n].edges ?? [])
  const maxRows = Math.max(...edgesPerPath.map(e => e.length), 0)

  const rows = [header]
  for (let i = 0; i < maxRows; i++) {
    rows.push(names.flatMap((_, pi) => {
      const edge = edgesPerPath[pi][i]
      return edge ? [edge[0], edge[1]] : ['', '']
    }).join(','))
  }
  return rows.join('\n')
}
