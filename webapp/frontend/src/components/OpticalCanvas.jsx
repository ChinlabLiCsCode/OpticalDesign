import { useRef, useState, useCallback, useMemo, useEffect, forwardRef, useImperativeHandle } from 'react'
import ElementShape from './ElementShape'
import { exportSVGToPDF } from '../utils/pdfExport'

const PAD = 2

const DARK_THEME  = { canvasBg: '#0d1117', gridLine: '#1e2a3a', tableBorder: '#2a4a6a', labelColor: '#7ec8e3', labelColor2: '#8a9ab0' }
const LIGHT_THEME = { canvasBg: '#ffffff',  gridLine: '#d0dce8', tableBorder: '#4a7aaa', labelColor: '#1a5a90', labelColor2: '#4a6a90' }

const OpticalCanvas = forwardRef(function OpticalCanvas({
  elements, beamPaths, visiblePaths,
  bgGroups, visibleBg,
  config,
  selectedLabel, selectedElement,
  onSelectLabel, onStartEdit, onUpdateEdit, onDeleteElement,
  editingPath, onAddEdge, onDeleteEdge, onSetEditingPath,
  editingBgGroup, onAddBgEdge, onDeleteBgEdge, onSetEditingBgGroup,
  symbolDefs,
  settings,
}, ref) {
  const svgRef  = useRef(null)
  const wrapRef = useRef(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 })
  const [mode, setMode] = useState('select')
  const [pendingSrc,   setPendingSrc]   = useState(null)
  const [pendingBgPt,  setPendingBgPt]  = useState(null)

  const drag = useRef(null)

  const SCALE = settings.scale ?? 10
  const theme = settings.darkMode ? DARK_THEME : LIGHT_THEME

  const { origin_x, origin_y, table_length, table_width } = config
  const minX = origin_x - table_length / 2 - PAD
  const minY = origin_y - table_width  / 2 - PAD
  const svgW = (table_length + 2 * PAD) * SCALE
  const svgH = (table_width  + 2 * PAD) * SCALE

  function px(physX) { return (physX - minX) * SCALE }
  function py(physY) { return svgH - (physY - minY) * SCALE }

  function screenToSVG(screenX, screenY) {
    const rect = svgRef.current.getBoundingClientRect()
    return {
      x: (screenX - rect.left - transform.x) / transform.k,
      y: (screenY - rect.top  - transform.y) / transform.k,
    }
  }

  function svgToPhys(svgPos, snapSpacing, free) {
    let x = svgPos.x / SCALE + minX
    let y = (svgH - svgPos.y) / SCALE + minY
    if (!free) {
      const s = snapSpacing
      x = Math.round(x / s) * s
      y = Math.round(y / s) * s
    }
    return { x, y }
  }

  useEffect(() => { setPendingSrc(null) }, [editingPath])
  useEffect(() => { setPendingBgPt(null) }, [editingBgGroup])
  useEffect(() => { if (!selectedElement) setMode('select') }, [selectedElement])

  // Keyboard shortcuts
  useEffect(() => {
    function onKeyDown(e) {
      const tag = document.activeElement?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return

      if (e.key === 'Escape') {
        e.preventDefault()
        if (pendingBgPt)   { setPendingBgPt(null); return }
        if (pendingSrc)    { setPendingSrc(null); return }
        if (editingBgGroup){ onSetEditingBgGroup(null); return }
        if (editingPath)   { onSetEditingPath(null); return }
        setMode('select'); return
      }

      if (!selectedElement) return
      if (e.key === 'm' || e.key === 'M') { e.preventDefault(); setMode('move') }
      if (e.key === 'r' || e.key === 'R') { e.preventDefault(); setMode('rotate') }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        e.preventDefault(); onDeleteElement(selectedElement.label)
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [selectedElement, editingPath, editingBgGroup, pendingSrc, pendingBgPt, onDeleteElement, onSetEditingPath, onSetEditingBgGroup])

  // ── Element click / drag start ────────────────────────────────────────────
  function onElementMouseDown(e, el) {
    if (e.button !== 0) return
    e.stopPropagation()

    // In bg edit mode, clicking an element snaps the bg edge point to the element's position
    if (editingBgGroup) {
      const { x, y } = el
      if (!pendingBgPt) {
        setPendingBgPt({ x, y })
      } else if (pendingBgPt.x === x && pendingBgPt.y === y) {
        setPendingBgPt(null)
      } else {
        onAddBgEdge(editingBgGroup, pendingBgPt.x, pendingBgPt.y, x, y)
        setPendingBgPt(null)
      }
      return
    }

    // Path edit mode: clicks build edges
    if (editingPath) {
      if (!pendingSrc) {
        setPendingSrc(el.label)
      } else if (pendingSrc === el.label) {
        setPendingSrc(null)
      } else {
        onAddEdge(pendingSrc, el.label)
        setPendingSrc(null)
      }
      return
    }

    if (mode === 'move' && el.label === selectedLabel) {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      onStartEdit()
      drag.current = {
        type: 'move', label: el.label,
        startSVG: svgPos, startPhys: { x: el.x, y: el.y }, hasMoved: false,
      }
      return
    }

    if (mode === 'rotate' && el.label === selectedLabel) {
      onStartEdit()
      drag.current = { type: 'rotate', label: el.label, startPhys: { x: el.x, y: el.y } }
      return
    }

    onSelectLabel(el.label === selectedLabel ? null : el.label)
  }

  function onBgMouseDown(e) {
    if (e.button !== 0 || drag.current) return

    if (editingBgGroup) {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const { x, y } = svgToPhys(svgPos, settings.snapSpacing, e.shiftKey)
      if (!pendingBgPt) {
        setPendingBgPt({ x, y })
      } else {
        onAddBgEdge(editingBgGroup, pendingBgPt.x, pendingBgPt.y, x, y)
        setPendingBgPt(null)
      }
      return
    }

    drag.current = { type: 'pan', lastX: e.clientX, lastY: e.clientY, hasMoved: false }
  }

  function onMouseMove(e) {
    if (!drag.current) return
    const { type } = drag.current

    if (type === 'pan') {
      const dx = e.clientX - drag.current.lastX
      const dy = e.clientY - drag.current.lastY
      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) drag.current.hasMoved = true
      drag.current.lastX = e.clientX; drag.current.lastY = e.clientY
      setTransform(t => ({ ...t, x: t.x + dx, y: t.y + dy }))
      return
    }

    if (type === 'move') {
      drag.current.hasMoved = true
      const svgPos = screenToSVG(e.clientX, e.clientY)
      let newX = drag.current.startPhys.x + (svgPos.x - drag.current.startSVG.x) / SCALE
      let newY = drag.current.startPhys.y - (svgPos.y - drag.current.startSVG.y) / SCALE
      if (!e.shiftKey) {
        const s = settings.snapSpacing
        newX = Math.round(newX / s) * s
        newY = Math.round(newY / s) * s
      }
      onUpdateEdit(drag.current.label, { x: newX, y: newY })
      return
    }

    if (type === 'rotate') {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const { startPhys } = drag.current
      const physX = svgPos.x / SCALE + minX
      const physY = (svgH - svgPos.y) / SCALE + minY
      let orient = Math.atan2(physY - startPhys.y, physX - startPhys.x) * 180 / Math.PI
      if (!e.shiftKey) orient = Math.round(orient / 45) * 45
      onUpdateEdit(drag.current.label, { orientation: orient })
    }
  }

  function onMouseUp() {
    if (drag.current?.type === 'pan' && !drag.current.hasMoved) onSelectLabel(null)
    drag.current = null
  }

  // ── Zoom ──────────────────────────────────────────────────────────────────
  const onWheel = useCallback((e) => {
    e.preventDefault()
    const rect = svgRef.current.getBoundingClientRect()
    const mx = e.clientX - rect.left, my = e.clientY - rect.top
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1
    setTransform(t => {
      const k2 = Math.max(0.15, Math.min(8, t.k * factor))
      return { k: k2, x: mx - (mx - t.x) * (k2 / t.k), y: my - (my - t.y) * (k2 / t.k) }
    })
  }, [])

  // ── Grid ──────────────────────────────────────────────────────────────────
  const gridLines = useMemo(() => {
    const lines = []
    for (let gx = Math.ceil(minX); gx <= minX + table_length + 2 * PAD; gx++) {
      lines.push(<line key={`gx${gx}`} x1={px(gx)} y1={0} x2={px(gx)} y2={svgH}
        stroke={theme.gridLine} strokeWidth={settings.gridLineWidth} />)
    }
    for (let gy = Math.ceil(minY); gy <= minY + table_width + 2 * PAD; gy++) {
      lines.push(<line key={`gy${gy}`} x1={0} y1={py(gy)} x2={svgW} y2={py(gy)}
        stroke={theme.gridLine} strokeWidth={settings.gridLineWidth} />)
    }
    return lines
  }, [config, SCALE, theme.gridLine, settings.gridLineWidth])

  const elemByLabel = useMemo(() => {
    const m = {}; elements.forEach(el => { m[el.label] = el }); return m
  }, [elements])

  // ── Background object rendering ───────────────────────────────────────────
  function renderBgEdges() {
    const out = []
    Object.entries(bgGroups ?? {}).forEach(([name, { color, strokeWidth = 2, edges = [] }]) => {
      if (!visibleBg?.[name]) return
      const isEditing = name === editingBgGroup
      const opacity   = editingBgGroup && !isEditing ? 0.2 : 0.7
      edges.forEach(([x1, y1, x2, y2], ei) => {
        out.push(
          <g key={`bg-${name}-${ei}`}>
            <line x1={px(x1)} y1={py(y1)} x2={px(x2)} y2={py(y2)}
              stroke={color} strokeWidth={isEditing ? strokeWidth * 1.5 : strokeWidth}
              strokeOpacity={opacity} strokeLinecap="round" />
            {isEditing && (
              <line x1={px(x1)} y1={py(y1)} x2={px(x2)} y2={py(y2)}
                stroke="transparent" strokeWidth={14}
                style={{ cursor: 'pointer' }}
                onClick={ev => { ev.stopPropagation(); onDeleteBgEdge(name, ei) }}
              />
            )}
          </g>
        )
      })
    })
    return out
  }

  // ── Coordinate axis labels ────────────────────────────────────────────────
  function renderCoordLabels() {
    if (!settings.showCoords) return null
    const labels = []
    const fontSize = Math.max(4, 7 / transform.k)
    const tickLen  = 3 / transform.k

    const xStep = table_length <= 15 ? 1 : 5
    const yStep = table_width  <= 15 ? 1 : 5

    const tableLeft   = px(origin_x - table_length / 2)
    const tableRight  = px(origin_x + table_length / 2)
    const tableBottom = py(origin_y - table_width  / 2)
    const tableTop    = py(origin_y + table_width  / 2)
    const labelOffX   = fontSize * 1.2
    const labelOffY   = fontSize * 1.4

    // X-axis: labels below the bottom table edge
    const xStart = Math.ceil((origin_x - table_length / 2) / xStep) * xStep
    const xEnd   = Math.floor((origin_x + table_length / 2) / xStep) * xStep
    for (let x = xStart; x <= xEnd; x += xStep) {
      const sx = px(x)
      labels.push(
        <g key={`cx${x}`} style={{ pointerEvents: 'none' }}>
          <line x1={sx} y1={tableBottom} x2={sx} y2={tableBottom + tickLen}
            stroke={theme.labelColor2} strokeWidth={0.5 / transform.k} />
          <text x={sx} y={tableBottom + labelOffY}
            textAnchor="middle" fontSize={fontSize} fill={theme.labelColor2}>
            {x}
          </text>
        </g>
      )
    }

    // Y-axis: labels to the left of the left table edge
    const yStart = Math.ceil((origin_y - table_width / 2) / yStep) * yStep
    const yEnd   = Math.floor((origin_y + table_width / 2) / yStep) * yStep
    for (let y = yStart; y <= yEnd; y += yStep) {
      const sy = py(y)
      labels.push(
        <g key={`cy${y}`} style={{ pointerEvents: 'none' }}>
          <line x1={tableLeft} y1={sy} x2={tableLeft - tickLen} y2={sy}
            stroke={theme.labelColor2} strokeWidth={0.5 / transform.k} />
          <text x={tableLeft - labelOffX} y={sy}
            textAnchor="end" dominantBaseline="middle" fontSize={fontSize} fill={theme.labelColor2}>
            {y}
          </text>
        </g>
      )
    }
    return labels
  }

  // ── Beam edge rendering ───────────────────────────────────────────────────
  function renderBeamEdges() {
    const out = []
    Object.entries(beamPaths).forEach(([name, { color, edges = [] }]) => {
      if (!visiblePaths[name]) return
      const isEditing = name === editingPath
      const opacity   = editingPath && !isEditing ? 0.2 : 0.85
      edges.forEach(([src, dest], ei) => {
        const srcEl = elemByLabel[src], dstEl = elemByLabel[dest]
        if (!srcEl || !dstEl) return
        const x1 = px(srcEl.x), y1 = py(srcEl.y)
        const x2 = px(dstEl.x), y2 = py(dstEl.y)
        out.push(
          <g key={`${name}-${ei}`}>
            <line x1={x1} y1={y1} x2={x2} y2={y2}
              stroke={color} strokeWidth={isEditing ? 2 : 1}
              strokeOpacity={opacity} strokeLinecap="round" />
            {isEditing && (
              <line x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="transparent" strokeWidth={12}
                style={{ cursor: 'pointer' }}
                onClick={ev => { ev.stopPropagation(); onDeleteEdge(ei) }}
              />
            )}
          </g>
        )
      })
    })
    return out
  }

  // ── Expose exportPDF ──────────────────────────────────────────────────────
  useImperativeHandle(ref, () => ({
    exportPDF: () => exportSVGToPDF(svgRef.current, svgW, svgH),
  }), [svgW, svgH])

  // ── Cursor ────────────────────────────────────────────────────────────────
  const bgCursor = (editingPath || editingBgGroup)
    ? 'crosshair'
    : (mode === 'move' ? 'move' : mode === 'rotate' ? 'crosshair' : 'grab')

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div ref={wrapRef}
      style={{ flex: 1, overflow: 'hidden', background: theme.canvasBg, cursor: bgCursor, position: 'relative', userSelect: 'none' }}
      onMouseDown={onBgMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
    >
      <svg ref={svgRef} width="100%" height="100%" onWheel={onWheel} style={{ display: 'block' }}>
        <g transform={`translate(${transform.x},${transform.y}) scale(${transform.k})`}>
          <rect x={0} y={0} width={svgW} height={svgH} fill={theme.canvasBg} />
          {gridLines}
          <rect
            x={px(origin_x - table_length / 2)} y={py(origin_y + table_width / 2)}
            width={table_length * SCALE} height={table_width * SCALE}
            fill="none" stroke={theme.tableBorder} strokeWidth="2"
          />
          <g>{renderCoordLabels()}</g>
          <g>{renderBgEdges()}</g>
          <g>{renderBeamEdges()}</g>

          {elements.map(el => {
            const isSel     = el.label === selectedLabel
            const isPendSrc = el.label === pendingSrc
            const elColor   = beamPaths[editingPath]?.color ?? (bgGroups?.[editingBgGroup]?.color ?? '#ffffff')
            const elCursor  = (editingPath || editingBgGroup) ? 'crosshair'
              : isSel ? (mode === 'move' ? 'grab' : mode === 'rotate' ? 'crosshair' : 'pointer')
              : 'pointer'
            return (
              <g key={el.label}
                transform={`translate(${px(el.x)},${py(el.y)})`}
                onMouseDown={e => onElementMouseDown(e, el)}
                style={{ cursor: elCursor }}
              >
                <ElementShape type={el.type} orientation={el.orientation} selected={isSel} symbolDefs={symbolDefs} />
                {isPendSrc && (
                  <circle r={10} fill="none" stroke={elColor}
                    strokeWidth={2} strokeDasharray="4 2" opacity={0.9} />
                )}
                {(settings.showONumber || settings.showType) && (() => {
                  const parts = [
                    settings.showONumber ? el.label : null,
                    settings.showType    ? el.type  : null,
                  ].filter(Boolean)
                  const labelY   = Math.min(-6, -8 / transform.k)
                  const fontSize = Math.max(3, 8 / transform.k)
                  return parts.map((text, i) => (
                    <text key={i} x={0} y={labelY - i * fontSize * 1.2}
                      textAnchor="middle" fontSize={fontSize}
                      fill={i === 0 ? theme.labelColor : theme.labelColor2}
                      style={{ pointerEvents: 'none', userSelect: 'none' }}>
                      {text}
                    </text>
                  ))
                })()}
              </g>
            )
          })}

          {/* Pending bg edge point indicator */}
          {pendingBgPt && (
            <g transform={`translate(${px(pendingBgPt.x)},${py(pendingBgPt.y)})`} style={{ pointerEvents: 'none' }}>
              <circle r={5} fill="none"
                stroke={bgGroups?.[editingBgGroup]?.color ?? '#fff'}
                strokeWidth={1.5} opacity={0.9} />
              <line x1={-7} y1={0} x2={7} y2={0} stroke={bgGroups?.[editingBgGroup]?.color ?? '#fff'} strokeWidth={1} opacity={0.7} />
              <line x1={0} y1={-7} x2={0} y2={7} stroke={bgGroups?.[editingBgGroup]?.color ?? '#fff'} strokeWidth={1} opacity={0.7} />
            </g>
          )}
        </g>
      </svg>

      {/* Element edit toolbar */}
      {selectedElement && !editingPath && !editingBgGroup && (
        <div className="edit-toolbar">
          <button className={`tb-btn ${mode === 'select' ? 'active' : ''}`}
            onClick={() => setMode('select')} title="Select (Esc)">↖</button>
          <button className={`tb-btn ${mode === 'move' ? 'active' : ''}`}
            onClick={() => setMode('move')} title="Move (M) · drag · Shift=free">✥ M</button>
          <button className={`tb-btn ${mode === 'rotate' ? 'active' : ''}`}
            onClick={() => setMode('rotate')} title="Rotate (R) · drag · Shift=free 45°">↻ R</button>
          <div className="tb-sep" />
          <button className="tb-btn tb-delete"
            onClick={() => onDeleteElement(selectedElement.label)} title="Delete (Del)">✕</button>
        </div>
      )}

      {/* Path edit hint */}
      {editingPath && (
        <div className="mode-hint">
          {pendingSrc
            ? `Source: ${pendingSrc} — click destination element`
            : 'Click source element · click edge line to delete · Esc to exit'}
        </div>
      )}

      {/* Bg edit hint */}
      {editingBgGroup && (
        <div className="mode-hint">
          {pendingBgPt
            ? `First point set — click second point (Shift = free)`
            : 'Click canvas or element for first point · click edge to delete · Esc to exit'}
        </div>
      )}

      {/* Element mode hint */}
      {selectedElement && !editingPath && !editingBgGroup && mode !== 'select' && (
        <div className="mode-hint">
          {mode === 'move' ? 'Drag to move · Shift = free position' : 'Drag to rotate · Shift = free angle'}
        </div>
      )}
    </div>
  )
})

export default OpticalCanvas
