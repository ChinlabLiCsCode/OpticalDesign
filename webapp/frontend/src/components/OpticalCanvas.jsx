import { useRef, useState, useCallback, useMemo, useEffect, forwardRef, useImperativeHandle } from 'react'
import ElementShape, { lookupSymbolDef } from './ElementShape'
import { exportSVGToPDF } from '../utils/pdfExport'

const PAD = 2

// Fallback perpendicular gap (in SVG units) between beams sharing an element pair,
// used when a project's settings predate the `beamSpacing` setting. Scales with zoom
// along with the rest of the canvas, matching beam stroke width.
const DEFAULT_BEAM_SPACING = 1

const DARK_THEME  = { canvasBg: '#0d1117', gridLine: '#1e2a3a', tableBorder: '#2a4a6a', labelColor: '#7ec8e3', labelColor2: '#8a9ab0' }
const LIGHT_THEME = { canvasBg: '#ffffff',  gridLine: '#d0dce8', tableBorder: '#4a7aaa', labelColor: '#1a5a90', labelColor2: '#4a6a90' }

const OpticalCanvas = forwardRef(function OpticalCanvas({
  elements, beamPaths, visiblePaths,
  bgGroups, visibleBg,
  config,
  selectedLabels, selectedElement,
  onSelectLabel, onStartEdit, onUpdateEdit, onDeleteSelected, onHardDeleteSelected,
  editingPath, onAddEdge, onDeleteEdge, onSetEditingPath,
  editingBgGroup, onAddBgEdge, onDeleteBgEdge, onSetEditingBgGroup,
  bgImages, onUpdateBgImage, onStartBgImageEdit,
  editingBgImage, onSetEditingBgImage,
  symbolDefs,
  settings,
  searchHighlights,
  onSelectLabels,
  onCursorMove,
}, ref) {
  const svgRef  = useRef(null)
  const wrapRef = useRef(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 })
  const [mode, setMode] = useState('select')
  const [pendingSrc,   setPendingSrc]   = useState(null)
  const [pendingBgPt,  setPendingBgPt]  = useState(null)
  const [selectionDrag, setSelectionDrag] = useState(null)
  // selectionDrag: null | { type:'box', x1,y1,x2,y2, additive }
  //                      | { type:'lasso', points:[{x,y}], additive }

  const drag = useRef(null)

  const SCALE = settings.scale ?? 10
  const theme = settings.darkMode ? DARK_THEME : LIGHT_THEME

  const { table_length, table_width } = config
  // origin_x/y = coordinate value shown at the bottom-left corner of the table
  const origin_x = config.origin_x ?? 0
  const origin_y = config.origin_y ?? 0
  const minX = origin_x - PAD
  const minY = origin_y - PAD
  const svgW = (table_length + 2 * PAD) * SCALE
  const svgH = (table_width  + 2 * PAD) * SCALE

  const px = useCallback(physX => (physX - minX) * SCALE, [minX, SCALE])
  const py = useCallback(physY => svgH - (physY - minY) * SCALE, [svgH, minY, SCALE])

  function screenToSVG(screenX, screenY) {
    const rect = svgRef.current.getBoundingClientRect()
    return {
      x: (screenX - rect.left - transform.x) / transform.k,
      y: (screenY - rect.top  - transform.y) / transform.k,
    }
  }

  function pointInPolygon(ptx, pty, pts) {
    let inside = false
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const xi = pts[i].x, yi = pts[i].y, xj = pts[j].x, yj = pts[j].y
      if (((yi > pty) !== (yj > pty)) && (ptx < (xj - xi) * (pty - yi) / (yj - yi) + xi))
        inside = !inside
    }
    return inside
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
  useEffect(() => {
    if (!selectedLabels?.size)
      setMode(m => (m === 'boxSelect' || m === 'lasso') ? m : 'select')
  }, [selectedLabels])

  // Keyboard shortcuts
  useEffect(() => {
    function onKeyDown(e) {
      const tag = document.activeElement?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return

      if (e.key === 'Escape') {
        e.preventDefault()
        if (pendingBgPt)    { setPendingBgPt(null); return }
        if (pendingSrc)     { setPendingSrc(null); return }
        if (editingBgGroup) { onSetEditingBgGroup(null); return }
        if (editingPath)    { onSetEditingPath(null); return }
        if (editingBgImage) { onSetEditingBgImage?.(null); return }
        if (mode !== 'select') { setMode('select'); return }
        if (selectedLabels?.size) { onSelectLabel(null, false); return }
      }

      if (e.key === 'b' || e.key === 'B') { e.preventDefault(); setMode('boxSelect'); return }
      if (e.key === 'l' || e.key === 'L') { e.preventDefault(); setMode('lasso'); return }
      if (!selectedLabels?.size) return
      if (e.key === 'm' || e.key === 'M') { e.preventDefault(); setMode('move') }
      if (e.key === 'r' || e.key === 'R') { e.preventDefault(); setMode('rotate') }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        e.preventDefault()
        if (e.shiftKey) onHardDeleteSelected()
        else            onDeleteSelected()
      }

      if (e.key.startsWith('Arrow')) {
        e.preventDefault()
        if (mode === 'rotate') {
          const delta = (e.key === 'ArrowRight' || e.key === 'ArrowDown') ? 45 : -45
          onStartEdit()
          elements.filter(el => selectedLabels.has(el.label)).forEach(el => {
            onUpdateEdit(el.label, { orientation: (el.orientation || 0) + delta })
          })
        } else {
          const s = settings.snapSpacing
          const dx = e.key === 'ArrowLeft' ? -s : e.key === 'ArrowRight' ? s : 0
          const dy = e.key === 'ArrowUp'   ? s  : e.key === 'ArrowDown'  ? -s : 0
          onStartEdit()
          elements.filter(el => selectedLabels.has(el.label)).forEach(el => {
            onUpdateEdit(el.label, { x: el.x + dx, y: el.y + dy })
          })
        }
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [selectedLabels, selectedElement, elements, mode, editingPath, editingBgGroup,
      editingBgImage,
      pendingSrc, pendingBgPt, settings, onDeleteSelected, onHardDeleteSelected,
      onStartEdit, onUpdateEdit, onSetEditingPath, onSetEditingBgGroup,
      onSetEditingBgImage])

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

    if (mode === 'rotate' && selectedLabels?.has(el.label)) {
      onStartEdit()
      const startOrientations = {}
      elements.filter(e2 => selectedLabels.has(e2.label)).forEach(e2 => {
        startOrientations[e2.label] = e2.orientation || 0
      })
      const svgPos0 = screenToSVG(e.clientX, e.clientY)
      const physX0 = svgPos0.x / SCALE + minX
      const physY0 = (svgH - svgPos0.y) / SCALE + minY
      const startAngle = Math.atan2(physY0 - el.y, physX0 - el.x) * 180 / Math.PI
      drag.current = { type: 'rotate', label: el.label, startPhys: { x: el.x, y: el.y }, startOrientations, startAngle }
      return
    }

    // Always start a potential drag-to-move (resolved on mousemove threshold)
    const svgPos = screenToSVG(e.clientX, e.clientY)
    const startPositions = {}
    // If dragging a selected element, move all selected; otherwise just this element
    const dragLabels = selectedLabels?.has(el.label)
      ? new Set(selectedLabels)
      : new Set([el.label])
    elements.filter(e2 => dragLabels.has(e2.label)).forEach(e2 => {
      startPositions[e2.label] = { x: e2.x, y: e2.y }
    })
    drag.current = {
      type: 'pendingMove', el,
      startSVG: svgPos, startPositions,
      dragLabels, shiftKey: e.shiftKey, hasMoved: false,
    }
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

    if (mode === 'boxSelect' || mode === 'lasso') {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      setSelectionDrag({
        type: mode === 'boxSelect' ? 'box' : 'lasso',
        x1: svgPos.x, y1: svgPos.y, x2: svgPos.x, y2: svgPos.y,
        points: [svgPos], additive: e.shiftKey,
      })
      return
    }

    drag.current = { type: 'pan', lastX: e.clientX, lastY: e.clientY, hasMoved: false }
  }

  function onMouseMove(e) {
    if (onCursorMove) {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      onCursorMove(svgToPhys(svgPos, 1, true))
    }
    if (selectionDrag) {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      if (selectionDrag.type === 'box') {
        setSelectionDrag(d => ({ ...d, x2: svgPos.x, y2: svgPos.y }))
      } else {
        setSelectionDrag(d => {
          const last = d.points[d.points.length - 1]
          const dxp = svgPos.x - last.x, dyp = svgPos.y - last.y
          if (dxp * dxp + dyp * dyp < 9) return d
          return { ...d, x2: svgPos.x, y2: svgPos.y, points: [...d.points, svgPos] }
        })
      }
      return
    }
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

    if (type === 'pendingMove') {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const dx = svgPos.x - drag.current.startSVG.x
      const dy = svgPos.y - drag.current.startSVG.y
      if (Math.sqrt(dx * dx + dy * dy) > 4) {
        // Crossed threshold — commit to move
        onStartEdit()
        // Ensure the dragged element is selected
        if (!selectedLabels?.has(drag.current.el.label)) {
          onSelectLabel(drag.current.el.label, drag.current.shiftKey)
        }
        drag.current = { ...drag.current, type: 'move', hasMoved: true }
        setMode('move')
      }
      return
    }

    if (type === 'move') {
      drag.current.hasMoved = true
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const dxPhys =  (svgPos.x - drag.current.startSVG.x) / SCALE
      const dyPhys = -(svgPos.y - drag.current.startSVG.y) / SCALE
      Object.entries(drag.current.startPositions).forEach(([label, start]) => {
        let newX = start.x + dxPhys
        let newY = start.y + dyPhys
        if (!e.shiftKey) {
          const s = settings.snapSpacing
          newX = Math.round(newX / s) * s
          newY = Math.round(newY / s) * s
        }
        onUpdateEdit(label, { x: newX, y: newY })
      })
      return
    }

    if (type === 'bgImageMove') {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const dxPhys =  (svgPos.x - drag.current.startSVG.x) / SCALE
      const dyPhys = -(svgPos.y - drag.current.startSVG.y) / SCALE
      let newX = drag.current.startX + dxPhys
      let newY = drag.current.startY + dyPhys
      // Skip snap on Shift for pixel-level positioning of reference photos.
      if (!e.shiftKey) {
        const s = settings.snapSpacing
        newX = Math.round(newX / s) * s
        newY = Math.round(newY / s) * s
      }
      onUpdateBgImage(drag.current.name, { x: newX, y: newY })
      return
    }

    if (type === 'bgImageResize') {
      // Corner handle sits at the top-right of the image on screen (bottom-right
      // in physics coords is the SVG top-right because y is flipped). Dragging
      // it changes widthIn; height auto-follows via aspect.
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const dxPhys = (svgPos.x - drag.current.startSVG.x) / SCALE
      let newWidth = drag.current.startWidthIn + dxPhys
      if (!e.shiftKey) {
        const s = settings.snapSpacing
        newWidth = Math.round(newWidth / s) * s
      }
      if (newWidth >= 0.25) onUpdateBgImage(drag.current.name, { widthIn: newWidth })
      return
    }

    if (type === 'rotate') {
      const svgPos = screenToSVG(e.clientX, e.clientY)
      const { startPhys, startOrientations, startAngle } = drag.current
      const physX = svgPos.x / SCALE + minX
      const physY = (svgH - svgPos.y) / SCALE + minY
      let currentAngle = Math.atan2(physY - startPhys.y, physX - startPhys.x) * 180 / Math.PI
      let delta = currentAngle - startAngle
      if (!e.shiftKey) delta = Math.round(delta / 45) * 45
      Object.entries(startOrientations).forEach(([label, startOrient]) => {
        onUpdateEdit(label, { orientation: startOrient + delta })
      })
    }
  }

  function onMouseUp() {
    if (selectionDrag) {
      const sd = selectionDrag
      setSelectionDrag(null)
      if (sd.type === 'box') {
        const w = Math.abs(sd.x2 - sd.x1), h = Math.abs(sd.y2 - sd.y1)
        if (w < 4 && h < 4) { onSelectLabel(null, false); return }
        const [minX, maxX] = [Math.min(sd.x1, sd.x2), Math.max(sd.x1, sd.x2)]
        const [minY, maxY] = [Math.min(sd.y1, sd.y2), Math.max(sd.y1, sd.y2)]
        const found = new Set(elements
          .filter(el => { const ex = px(el.x), ey = py(el.y); return ex >= minX && ex <= maxX && ey >= minY && ey <= maxY })
          .map(el => el.label))
        onSelectLabels(sd.additive ? new Set([...(selectedLabels ?? []), ...found]) : found)
      } else {
        if (sd.points.length < 4) { onSelectLabel(null, false); return }
        const found = new Set(elements
          .filter(el => pointInPolygon(px(el.x), py(el.y), sd.points))
          .map(el => el.label))
        onSelectLabels(sd.additive ? new Set([...(selectedLabels ?? []), ...found]) : found)
      }
      return
    }
    if (drag.current?.type === 'pan' && !drag.current.hasMoved) onSelectLabel(null, false)
    if (drag.current?.type === 'pendingMove') {
      // No drag threshold crossed — treat as a click
      onSelectLabel(drag.current.el.label, drag.current.shiftKey)
    }
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
  }, [minX, minY, svgW, svgH, table_length, table_width, px, py, theme.gridLine, settings.gridLineWidth])

  const elemByLabel = useMemo(() => {
    const m = {}; elements.forEach(el => { m[el.label] = el }); return m
  }, [elements])

  // Element labels that appear as source or destination in ANY beam path
  // (regardless of visibility). Used by the "highlight orphans" view mode.
  const inPathLabels = useMemo(() => {
    const s = new Set()
    Object.values(beamPaths).forEach(({ edges = [] }) => {
      edges.forEach(([src, dest]) => { s.add(src); s.add(dest) })
    })
    return s
  }, [beamPaths])

  // ── Parallel beam fan-out ─────────────────────────────────────────────────
  // Beams sharing the same pair of elements would otherwise draw exactly on top of
  // one another. Group them by the unordered pair and give each a perpendicular
  // offset, evenly spaced and centred on zero (5 beams → -2,-1,0,+1,+2 × spacing).
  // Only visible beams are counted, so hiding one re-centres the rest.
  const beamEdgeOffsets = useMemo(() => {
    const groups = new Map()
    Object.entries(beamPaths)
      // Sort by path name so the slot each beam lands in is stable across renders
      // rather than depending on object insertion order.
      .sort(([a], [b]) => a.localeCompare(b))
      .forEach(([name, path]) => {
        if (!visiblePaths[name]) return
        ;(path.edges ?? []).forEach(([src, dest], ei) => {
          if (!elemByLabel[src] || !elemByLabel[dest]) return
          // NUL separator: labels and path names are free text that may contain
          // spaces, which would let distinct pairs collide on a shared key.
          const key = [src, dest].slice().sort().join('\u0000')
          if (!groups.has(key)) groups.set(key, [])
          groups.get(key).push(`${name}\u0000${ei}`)
        })
      })
    const spacing = settings.beamSpacing ?? DEFAULT_BEAM_SPACING
    const offsets = new Map()
    groups.forEach(members => {
      if (members.length < 2 || !spacing) return
      const mid = (members.length - 1) / 2
      members.forEach((id, i) => offsets.set(id, (i - mid) * spacing))
    })
    return offsets
  }, [beamPaths, visiblePaths, elemByLabel, settings.beamSpacing])

  // Unit perpendicular for an element pair, derived from the pair's canonical
  // (label-sorted) direction — not the individual edge's — so that an A→B beam and
  // a B→A beam fan out to opposite sides instead of landing on the same one.
  function pairNormal(src, dest) {
    const [a, b] = [src, dest].slice().sort()
    const ea = elemByLabel[a], eb = elemByLabel[b]
    if (!ea || !eb) return null
    const dx = px(eb.x) - px(ea.x)
    const dy = py(eb.y) - py(ea.y)
    const len = Math.hypot(dx, dy)
    if (!len) return null
    return { nx: -dy / len, ny: dx / len }
  }

  // ── Background image rendering ────────────────────────────────────────────
  function onBgImageMouseDown(e, name, img) {
    if (e.button !== 0) return
    e.stopPropagation()
    onStartBgImageEdit?.()
    const startSVG = screenToSVG(e.clientX, e.clientY)
    drag.current = {
      type: 'bgImageMove',
      name,
      startX: img.x, startY: img.y,
      startSVG,
      hasMoved: false,
    }
  }

  function onBgImageResizeMouseDown(e, name, img) {
    if (e.button !== 0) return
    e.stopPropagation()
    onStartBgImageEdit?.()
    drag.current = {
      type: 'bgImageResize',
      name,
      startWidthIn: img.widthIn,
      startSVG: screenToSVG(e.clientX, e.clientY),
      hasMoved: false,
    }
  }

  function renderBgImages() {
    if (!bgImages) return null
    return Object.entries(bgImages).map(([name, img]) => {
      if (img.visible === false) return null
      const isEditing = name === editingBgImage
      const heightIn = img.widthIn * img.aspect
      // physY grows up but SVG y grows down, so anchor at the top-left in SVG
      // space, which corresponds to the image's top edge (y + heightIn) on the table.
      const sx = px(img.x)
      const sy = py(img.y + heightIn)
      const sw = img.widthIn * SCALE
      const sh = heightIn * SCALE
      // Handle size scales inversely with zoom so it stays clickable at any zoom.
      const handleR = 5 / transform.k
      return (
        <g key={`bgimg-${name}`}>
          <image
            href={img.href}
            x={sx} y={sy} width={sw} height={sh}
            opacity={img.opacity ?? 1}
            preserveAspectRatio="none"
            // pointerEvents 'none' when not being edited so the image is inert
            // — clicks pass through to the elements/beams underneath and there
            // is no drag cursor to suggest it moves.
            style={{
              pointerEvents: isEditing ? 'auto' : 'none',
              cursor: isEditing ? 'move' : 'default',
            }}
            onMouseDown={isEditing ? e => onBgImageMouseDown(e, name, img) : undefined}
          />
          {isEditing && (
            <>
              <rect x={sx} y={sy} width={sw} height={sh}
                fill="none"
                stroke="var(--accent-bright, #1a8abf)"
                strokeWidth={1 / transform.k}
                strokeDasharray={`${3 / transform.k} ${2 / transform.k}`}
                pointerEvents="none" />
              {/* Corner handle at SVG top-right (physics bottom-right). */}
              <circle cx={sx + sw} cy={sy} r={handleR}
                fill="var(--accent-bright, #1a8abf)"
                stroke="#fff"
                strokeWidth={1 / transform.k}
                style={{ cursor: 'nesw-resize' }}
                onMouseDown={e => onBgImageResizeMouseDown(e, name, img)} />
            </>
          )}
        </g>
      )
    })
  }

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

    const tableLeft   = px(origin_x)
    const tableBottom = py(origin_y)
    const labelOffX   = fontSize * 1.2
    const labelOffY   = fontSize * 1.4

    // X-axis: labels below the bottom table edge
    const xStart = Math.ceil(origin_x / xStep) * xStep
    const xEnd   = Math.floor((origin_x + table_length) / xStep) * xStep
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
    const yStart = Math.ceil(origin_y / yStep) * yStep
    const yEnd   = Math.floor((origin_y + table_width) / yStep) * yStep
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
        let x1 = px(srcEl.x), y1 = py(srcEl.y)
        let x2 = px(dstEl.x), y2 = py(dstEl.y)
        const off = beamEdgeOffsets.get(`${name}\u0000${ei}`)
        if (off) {
          const n = pairNormal(src, dest)
          if (n) {
            x1 += n.nx * off; y1 += n.ny * off
            x2 += n.nx * off; y2 += n.ny * off
          }
        }
        out.push(
          <g key={`${name}-${ei}`}>
            <line x1={x1} y1={y1} x2={x2} y2={y2}
              stroke={color} strokeWidth={isEditing ? 2 : 1}
              strokeOpacity={opacity} strokeLinecap="round" />
            {settings.showBeamArrows && (() => {
              const mx = (x1 + x2) / 2, my = (y1 + y2) / 2
              const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI
              const s = settings.beamArrowSize ?? 1
              return (
                <polygon
                  points="4,0 -3,-2.4 -3,2.4"
                  transform={`translate(${mx},${my}) rotate(${angle}) scale(${s})`}
                  fill={color} fillOpacity={opacity}
                  style={{ pointerEvents: 'none' }}
                />
              )
            })()}
            {isEditing ? (
              <line x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="transparent" strokeWidth={12}
                style={{ cursor: 'pointer' }}
                onClick={ev => { ev.stopPropagation(); onDeleteEdge(ei) }}
              />
            ) : (
              <line x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="transparent" strokeWidth={12}
                style={{ cursor: 'pointer' }}
                onDoubleClick={ev => { ev.stopPropagation(); onSetEditingPath(name) }}
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
    exportPDF: () => exportSVGToPDF(svgRef.current, svgW, svgH, transform.k, settings.pdfFontSize ?? 4),
    centerOn: (labels) => {
      const targets = elements.filter(el => labels.has(el.label))
      if (!targets.length) return
      // compute SVG-space bounding centre directly (avoids stale px/py closure)
      const _px = x => (x - (config.origin_x ?? 0) + PAD) * (settings.scale ?? 10)
      const _py = y => ((config.table_width + 2 * PAD) - (y - (config.origin_y ?? 0) + PAD)) * (settings.scale ?? 10)
      const xs = targets.map(e => _px(e.x))
      const ys = targets.map(e => _py(e.y))
      const cx = (Math.min(...xs) + Math.max(...xs)) / 2
      const cy = (Math.min(...ys) + Math.max(...ys)) / 2
      const rect = wrapRef.current?.getBoundingClientRect()
      if (!rect) return
      setTransform(t => ({ k: t.k, x: rect.width / 2 - cx * t.k, y: rect.height / 2 - cy * t.k }))
    },
  }), [svgW, svgH, elements, config, settings, transform.k])

  // ── Cursor ────────────────────────────────────────────────────────────────
  const bgCursor = (editingPath || editingBgGroup)
    ? 'crosshair'
    : (mode === 'boxSelect' || mode === 'lasso') ? 'crosshair'
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
          {settings.showGrid !== false && gridLines}
          <rect
            x={px(origin_x)} y={py(origin_y + table_width)}
            width={table_length * SCALE} height={table_width * SCALE}
            fill="none" stroke={theme.tableBorder} strokeWidth="2"
          />
          <g>{renderCoordLabels()}</g>
          <g>{renderBgImages()}</g>
          <g>{renderBgEdges()}</g>
          <g>{renderBeamEdges()}</g>

          {elements.map(el => {
            const isSel     = selectedLabels?.has(el.label) ?? false
            const isPendSrc = el.label === pendingSrc
            const elColor   = beamPaths[editingPath]?.color ?? (bgGroups?.[editingBgGroup]?.color ?? '#ffffff')
            const elCursor  = (editingPath || editingBgGroup) ? 'crosshair'
              : isSel ? (mode === 'move' ? 'grab' : mode === 'rotate' ? 'crosshair' : 'pointer')
              : 'pointer'
            const isOrphan  = settings.highlightOrphans && !inPathLabels.has(el.label)
            const dimmed    = settings.highlightOrphans && inPathLabels.has(el.label)
            return (
              <g key={el.label}
                transform={`translate(${px(el.x)},${py(el.y)})`}
                onMouseDown={e => onElementMouseDown(e, el)}
                style={{ cursor: elCursor, opacity: dimmed ? 0.25 : 1 }}
              >
                <ElementShape type={el.type} orientation={el.orientation} selected={isSel} symbolDefs={symbolDefs} dark={settings.darkMode} />
                {isOrphan && (
                  <circle r={11} fill="none" stroke="#ff6b35"
                    strokeWidth={Math.max(1.5, 2 / transform.k)}
                    strokeDasharray="3 2" opacity={0.9}
                    style={{ pointerEvents: 'none' }}
                  />
                )}
                {searchHighlights?.has(el.label) && (
                  <circle r={9} fill="none" stroke="#ffd700"
                    strokeWidth={Math.max(1, 1.5 / transform.k)} opacity={0.9} />
                )}
                {isPendSrc && (
                  <circle r={10} fill="none" stroke={elColor}
                    strokeWidth={2} strokeDasharray="4 2" opacity={0.9} />
                )}
                {(settings.showONumber || settings.showType || settings.showAnnotation) && (() => {
                  const parts = [
                    settings.showONumber   ? el.label      : null,
                    settings.showType      ? el.type       : null,
                    settings.showAnnotation ? el.Annotation : null,
                  ].filter(Boolean)
                  const def = lookupSymbolDef(symbolDefs, (el.type || '').toLowerCase().trim())
                  const clearance = def?.labelClearance ?? 6
                  const labelY   = Math.min(-clearance, -8 / transform.k)
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

          {/* Box / lasso selection overlay */}
          {selectionDrag?.type === 'box' && (() => {
            const sx = Math.min(selectionDrag.x1, selectionDrag.x2)
            const sy = Math.min(selectionDrag.y1, selectionDrag.y2)
            const sw = Math.abs(selectionDrag.x2 - selectionDrag.x1)
            const sh = Math.abs(selectionDrag.y2 - selectionDrag.y1)
            return (
              <rect x={sx} y={sy} width={sw} height={sh}
                fill="rgba(100,160,255,0.12)" stroke="#6ab4ff"
                strokeWidth={1 / transform.k}
                strokeDasharray={`${4 / transform.k} ${2 / transform.k}`}
                style={{ pointerEvents: 'none' }} />
            )
          })()}
          {selectionDrag?.type === 'lasso' && selectionDrag.points.length > 1 && (
            <polygon
              points={selectionDrag.points.map(p => `${p.x},${p.y}`).join(' ')}
              fill="rgba(100,160,255,0.12)" stroke="#6ab4ff"
              strokeWidth={1 / transform.k}
              strokeDasharray={`${4 / transform.k} ${2 / transform.k}`}
              style={{ pointerEvents: 'none' }} />
          )}

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

      {/* Canvas toolbar */}
      {!editingPath && !editingBgGroup && (
        <div className="edit-toolbar">
          <button className={`tb-btn ${mode === 'select' ? 'active' : ''}`}
            onClick={() => setMode('select')} title="Select (Esc)">↖</button>
          <button className={`tb-btn ${mode === 'boxSelect' ? 'active' : ''}`}
            onClick={() => setMode('boxSelect')} title="Box Select (B) · drag to select area">⬚ B</button>
          <button className={`tb-btn ${mode === 'lasso' ? 'active' : ''}`}
            onClick={() => setMode('lasso')} title="Lasso Select (L) · draw to select area">⌾ L</button>
          {selectedLabels?.size > 0 && <>
            <div className="tb-sep" />
            <button className={`tb-btn ${mode === 'move' ? 'active' : ''}`}
              onClick={() => setMode('move')} title="Move (M) · drag · arrow keys · Shift=free">✥ M</button>
            <button className={`tb-btn ${mode === 'rotate' ? 'active' : ''}`}
              onClick={() => setMode('rotate')} title="Rotate (R) · drag · arrow keys · Shift=free 45°">↻ R</button>
            <div className="tb-sep" />
            <button className="tb-btn tb-delete"
              onClick={() => onDeleteSelected()} title="Delete (Del)">✕</button>
          </>}
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

      {/* Mode hint */}
      {!editingPath && !editingBgGroup && mode !== 'select' && (
        <div className="mode-hint">
          {mode === 'boxSelect'
            ? 'Drag to box-select · Shift+drag to add to selection'
            : mode === 'lasso'
            ? 'Drag to lasso-select · Shift+drag to add to selection'
            : mode === 'move'
            ? 'Drag or arrow keys to move · Shift = free position'
            : 'Drag or arrow keys to rotate · Shift = free angle'}
        </div>
      )}
    </div>
  )
})

export default OpticalCanvas
