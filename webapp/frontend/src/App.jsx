import { useState, useMemo, useEffect, useRef } from 'react'
import JSZip from 'jszip'
import OpticalCanvas from './components/OpticalCanvas'
import Sidebar from './components/Sidebar'
import SpreadsheetModal from './components/SpreadsheetModal'
import { DEFAULT_SYMBOL_DEFS } from './components/ElementShape'
import {
  parseElementsCsv, serializeElementsCsv,
  parseBeamPathsCsv, serializeBeamPathsCsv,
  parseBgObjectsCsv, serializeBgObjectsCsv,
} from './utils/csvUtils'
import './App.css'

const DEFAULT_CONFIG = { table_length: 55, table_width: 85, origin_x: 0, origin_y: 0 }

async function triggerSave(blob, suggestedName, mimeType, ext) {
  if ('showSaveFilePicker' in window) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName,
        types: [{ description: ext.toUpperCase() + ' file', accept: { [mimeType]: ['.' + ext] } }],
      })
      const w = await handle.createWritable()
      await w.write(blob); await w.close()
      return
    } catch (e) { if (e.name === 'AbortError') return }
  }
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = suggestedName; a.click()
  URL.revokeObjectURL(url)
}

function loadLocalState() {
  try {
    const raw = localStorage.getItem('optDesign_v1')
    if (!raw) return null
    return JSON.parse(raw)
  } catch { return null }
}

export default function App() {
  const _ls = useMemo(() => loadLocalState(), [])

  const [elements,     setElements]     = useState(() => _ls?.elements     ?? [])
  const [config,       setConfig]       = useState(() => _ls?.config ? { ...DEFAULT_CONFIG, ..._ls.config } : DEFAULT_CONFIG)
  const [beamPaths,    setBeamPaths]    = useState(() => _ls?.beamPaths    ?? {})
  const [visiblePaths, setVisiblePaths] = useState(() => _ls?.visiblePaths ?? {})
  const [bgGroups,     setBgGroups]     = useState(() => _ls?.bgGroups     ?? {})
  const [visibleBg,    setVisibleBg]    = useState(() => _ls?.visibleBg    ?? {})
  const [error,        setError]        = useState(null)

  const [selectedLabels, setSelectedLabels] = useState(() => new Set())
  const [overrides,  setOverrides]  = useState(() => _ls?.overrides  ?? {})
  const [history,    setHistory]    = useState([])
  const [editingPath,    setEditingPath]    = useState(null)
  const [editingBgGroup, setEditingBgGroup] = useState(null)

  const [symbolDefs, setSymbolDefs] = useState(() => _ls?.symbolDefs ?? { ...DEFAULT_SYMBOL_DEFS })

  const [settings, setSettings] = useState(() => _ls?.settings ?? {
    snapSpacing:   0.5,
    showONumber:   true,
    showType:      false,
    darkMode:      false,
    showGrid:      true,
    gridLineWidth: 0.5,
    scale:         10,
    showCoords:    true,
    uiFontSize:    12,
  })

  const [searchOpen,  setSearchOpen]  = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const [addElemAt,    setAddElemAt]    = useState(null)
  const [sidebarWidth, setSidebarWidth] = useState(() => _ls?.sidebarWidth ?? 280)
  const [fileMenuOpen, setFileMenuOpen] = useState(false)
  const [viewMenuOpen, setViewMenuOpen] = useState(false)
  const [viewModal,    setViewModal]    = useState(null) // 'elements' | 'paths' | 'objects'

  const searchInputRef   = useRef(null)
  const cursorPosRef     = useRef({ x: 0, y: 0 })
  const canvasRef        = useRef(null)
  const elemFileRef      = useRef(null)
  const pathFileRef      = useRef(null)
  const bgFileRef        = useRef(null)
  const settingsFileRef  = useRef(null)
  const zipFileRef       = useRef(null)
  const lastAddedTypeRef = useRef('')
  const persistTimer     = useRef(null)
  const fileMenuRef      = useRef(null)
  const viewMenuRef      = useRef(null)

  // Persist state to localStorage (debounced)
  useEffect(() => {
    clearTimeout(persistTimer.current)
    persistTimer.current = setTimeout(() => {
      try {
        localStorage.setItem('optDesign_v1', JSON.stringify({
          elements, overrides, beamPaths, bgGroups, visiblePaths, visibleBg,
          settings, config, symbolDefs, sidebarWidth,
        }))
      } catch {}
    }, 800)
  }, [elements, overrides, beamPaths, bgGroups, visiblePaths, visibleBg, settings, config, symbolDefs, sidebarWidth])

  useEffect(() => {
    document.documentElement.dataset.theme = settings.darkMode ? 'dark' : 'light'
  }, [settings.darkMode])

  // ── Derived state ──────────────────────────────────────────────────────────
  // All elements with overrides merged — used for the sidebar list (includes hidden)
  const allMergedElements = useMemo(() =>
    elements.map(el => {
      const ov = overrides[el.label]
      return ov ? { ...el, ...ov } : el
    }),
    [elements, overrides]
  )

  // Only elements with in_design !== false — rendered on canvas
  const effectiveElements = useMemo(() =>
    allMergedElements.filter(el => el.in_design !== false),
    [allMergedElements]
  )

  const searchHighlights = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!searchOpen || !q) return null
    const hits = new Set()
    effectiveElements.forEach(el => {
      if (el.label.toLowerCase().includes(q) || (el.type || '').toLowerCase().includes(q))
        hits.add(el.label)
    })
    return hits
  }, [searchOpen, searchQuery, effectiveElements])

  const selectedElement = useMemo(() => {
    const primary = [...selectedLabels][0] ?? null
    return allMergedElements.find(el => el.label === primary) ?? null
  }, [allMergedElements, selectedLabels])

  const allMetaKeys = useMemo(() => {
    const coreKeys = new Set(['label', 'type', 'x', 'y', 'orientation', 'in_design', 'Setup Location'])
    const keys = []; const seen = new Set()
    elements.forEach(el => Object.keys(el).forEach(k => {
      if (!coreKeys.has(k) && !seen.has(k)) { seen.add(k); keys.push(k) }
    }))
    return keys
  }, [elements])

  // ── Unified history ────────────────────────────────────────────────────────
  // Each entry snapshots all three mutable data layers.
  const MAX_HISTORY = 100

  function pushHistory() {
    setHistory(h => [...h.slice(-(MAX_HISTORY - 1)), { elements, overrides, beamPaths, bgGroups }])
  }

  function undo() {
    if (!history.length) return
    const prev = history[history.length - 1]
    setElements(prev.elements)
    setOverrides(prev.overrides)
    setBeamPaths(prev.beamPaths)
    setBgGroups(prev.bgGroups)
    setHistory(h => h.slice(0, -1))
  }

  function handleSelectLabel(label, shiftKey) {
    if (label === null) { setSelectedLabels(new Set()); return }
    if (shiftKey) {
      setSelectedLabels(prev => {
        const next = new Set(prev)
        if (next.has(label)) next.delete(label); else next.add(label)
        return next
      })
    } else {
      setSelectedLabels(prev =>
        prev.size === 1 && prev.has(label) ? new Set() : new Set([label])
      )
    }
  }

  useEffect(() => {
    function onKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
        e.preventDefault()
        setSearchOpen(true)
        setTimeout(() => searchInputRef.current?.focus(), 0)
        return
      }
      const tag = document.activeElement?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault(); undo()
      }
      if ((e.key === 'n' || e.key === 'N') && !e.metaKey && !e.ctrlKey) {
        e.preventDefault()
        const snap = settings.snapSpacing ?? 0.5
        const rx = Math.round(cursorPosRef.current.x / snap) * snap
        const ry = Math.round(cursorPosRef.current.y / snap) * snap
        setAddElemAt({ x: rx, y: ry, label: nextOLabel(elements), type: lastAddedTypeRef.current || '' })
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [history])

  useEffect(() => {
    if (!fileMenuOpen) return
    function onDown(e) {
      if (!fileMenuRef.current?.contains(e.target)) setFileMenuOpen(false)
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [fileMenuOpen])

  useEffect(() => {
    if (!viewMenuOpen) return
    function onDown(e) {
      if (!viewMenuRef.current?.contains(e.target)) setViewMenuOpen(false)
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [viewMenuOpen])

  // ── Element edit helpers ───────────────────────────────────────────────────
  function startEdit()  { pushHistory() }

  function updateEdit(label, patch) {
    setOverrides(ov => ({ ...ov, [label]: { ...(ov[label] ?? {}), ...patch } }))
  }

  // Soft delete: set in_design=false, hides from canvas but kept in elements list
  function deleteSelected() {
    if (!selectedLabels.size) return
    pushHistory()
    setOverrides(ov => {
      const next = { ...ov }
      selectedLabels.forEach(label => {
        next[label] = { ...(next[label] ?? {}), in_design: false }
      })
      return next
    })
    setSelectedLabels(new Set())
  }

  // Hard delete: remove from elements array entirely
  function hardDeleteSelected() {
    if (!selectedLabels.size) return
    pushHistory()
    setElements(els => els.filter(el => !selectedLabels.has(el.label)))
    setOverrides(ov => {
      const next = { ...ov }
      selectedLabels.forEach(label => { delete next[label] })
      return next
    })
    setSelectedLabels(new Set())
  }

  function nextOLabel(elems) {
    const nums = elems.map(el => { const m = el.label.match(/^O-(\d+(?:\.\d+)?)$/); return m ? parseFloat(m[1]) : 0 })
    return `O-${nums.length ? Math.floor(Math.max(...nums)) + 1 : 1}`
  }

  function addElement({ type, x, y, orientation = 0, label: providedLabel }) {
    const label = providedLabel?.trim() || nextOLabel(elements)
    lastAddedTypeRef.current = type
    pushHistory()
    const newEl = { label, type, x, y, orientation, in_design: true }
    setElements(els => [...els, newEl])
    setSelectedLabels(new Set([label]))
  }

  function updateElementField(label, key, value) {
    pushHistory()
    let parsed = value
    if (key === 'x' || key === 'y' || key === 'orientation') {
      const n = parseFloat(value); if (isNaN(n)) return; parsed = n
    }
    setOverrides(ov => ({ ...ov, [label]: { ...(ov[label] ?? {}), [key]: parsed } }))
  }

  useEffect(() => {
    if (searchHighlights?.size) canvasRef.current?.centerOn(searchHighlights)
  }, [searchHighlights])

  function startSidebarResize(e) {
    e.preventDefault()
    const startX = e.clientX
    const startW = sidebarWidth
    const onMove = ev => setSidebarWidth(Math.max(180, Math.min(600, startW + (startX - ev.clientX))))
    const onUp   = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }

  // ── Beam path helpers ──────────────────────────────────────────────────────
  function addEdge(src, dest) {
    if (!editingPath) return
    pushHistory()
    setBeamPaths(bp => {
      const path = bp[editingPath]
      if (!path) return bp
      return { ...bp, [editingPath]: { ...path, edges: [...(path.edges ?? []), [src, dest]] } }
    })
  }

  function deleteEdge(edgeIndex) {
    if (!editingPath) return
    pushHistory()
    setBeamPaths(bp => {
      const path = bp[editingPath]
      if (!path) return bp
      return { ...bp, [editingPath]: { ...path, edges: (path.edges ?? []).filter((_, i) => i !== edgeIndex) } }
    })
  }

  function addBeamPath(name, color) {
    if (!name || beamPaths[name]) return
    pushHistory()
    setBeamPaths(bp => ({ ...bp, [name]: { color, edges: [] } }))
    setVisiblePaths(vp => ({ ...vp, [name]: true }))
  }

  function deleteBeamPath(name) {
    pushHistory()
    setBeamPaths(bp => { const n = { ...bp }; delete n[name]; return n })
    setVisiblePaths(vp => { const n = { ...vp }; delete n[name]; return n })
    if (editingPath === name) setEditingPath(null)
  }

  function setPathColor(name, color) {
    setBeamPaths(bp => ({ ...bp, [name]: { ...bp[name], color } }))
  }

  function renameBeamPath(oldName, newName) {
    const trimmed = newName.trim()
    if (!trimmed || trimmed === oldName || beamPaths[trimmed]) return
    pushHistory()
    setBeamPaths(bp => {
      const next = {}
      Object.entries(bp).forEach(([k, v]) => { next[k === oldName ? trimmed : k] = v })
      return next
    })
    setVisiblePaths(vp => {
      const next = {}
      Object.entries(vp).forEach(([k, v]) => { next[k === oldName ? trimmed : k] = v })
      return next
    })
    if (editingPath === oldName) setEditingPath(trimmed)
  }

  // ── Background object helpers ──────────────────────────────────────────────
  function addBgGroup(name, color, strokeWidth) {
    if (!name || bgGroups[name]) return
    pushHistory()
    setBgGroups(g => ({ ...g, [name]: { color, strokeWidth, edges: [] } }))
    setVisibleBg(v => ({ ...v, [name]: true }))
  }

  function deleteBgGroup(name) {
    pushHistory()
    setBgGroups(g => { const n = { ...g }; delete n[name]; return n })
    setVisibleBg(v => { const n = { ...v }; delete n[name]; return n })
    if (editingBgGroup === name) setEditingBgGroup(null)
  }

  function setBgGroupColor(name, color) {
    setBgGroups(g => ({ ...g, [name]: { ...g[name], color } }))
  }

  function renameBgGroup(oldName, newName) {
    const trimmed = newName.trim()
    if (!trimmed || trimmed === oldName || bgGroups[trimmed]) return
    pushHistory()
    setBgGroups(g => {
      const next = {}
      Object.entries(g).forEach(([k, v]) => { next[k === oldName ? trimmed : k] = v })
      return next
    })
    setVisibleBg(v => {
      const next = {}
      Object.entries(v).forEach(([k, val]) => { next[k === oldName ? trimmed : k] = val })
      return next
    })
    if (editingBgGroup === oldName) setEditingBgGroup(trimmed)
  }

  function setBgGroupStroke(name, sw) {
    setBgGroups(g => ({ ...g, [name]: { ...g[name], strokeWidth: sw } }))
  }

  function addBgEdge(groupName, x1, y1, x2, y2) {
    pushHistory()
    setBgGroups(g => {
      const grp = g[groupName]
      if (!grp) return g
      return { ...g, [groupName]: { ...grp, edges: [...grp.edges, [x1, y1, x2, y2]] } }
    })
  }

  function deleteBgEdge(groupName, idx) {
    pushHistory()
    setBgGroups(g => {
      const grp = g[groupName]
      if (!grp) return g
      return { ...g, [groupName]: { ...grp, edges: grp.edges.filter((_, i) => i !== idx) } }
    })
  }

  function updateBgEdge(groupName, idx, patch) {
    pushHistory()
    setBgGroups(g => {
      const grp = g[groupName]
      if (!grp) return g
      const edges = grp.edges.map((e, i) => i === idx ? [
        patch.x1 ?? e[0], patch.y1 ?? e[1], patch.x2 ?? e[2], patch.y2 ?? e[3],
      ] : e)
      return { ...g, [groupName]: { ...grp, edges } }
    })
  }

  // ── Symbol def helpers ─────────────────────────────────────────────────────
  function addSymbolDef(typeName, def) {
    setSymbolDefs(d => ({ ...d, [typeName.toLowerCase()]: def }))
  }

  function updateSymbolDef(typeName, patch) {
    setSymbolDefs(d => ({ ...d, [typeName]: { ...d[typeName], ...patch } }))
  }

  function deleteSymbolDef(typeName) {
    setSymbolDefs(d => { const n = { ...d }; delete n[typeName]; return n })
  }

  function renameSymbolDef(oldKey, newKey) {
    const trimmed = newKey.trim().toLowerCase()
    if (!trimmed || trimmed === oldKey || symbolDefs[trimmed]) return
    setSymbolDefs(d => {
      const next = {}
      Object.entries(d).forEach(([k, v]) => { next[k === oldKey ? trimmed : k] = v })
      return next
    })
  }

  // ── Settings save / load ──────────────────────────────────────────────────
  async function saveSettingsJSON() {
    const data = JSON.stringify({ settings, config, symbolDefs }, null, 2)
    await triggerSave(new Blob([data], { type: 'application/json' }), 'settings.json', 'application/json', 'json')
  }

  function loadSettingsFile(file) {
    if (!file) return
    const reader = new FileReader()
    reader.onload = e => {
      try {
        const { settings: s, config: c, symbolDefs: sd } = JSON.parse(e.target.result)
        if (s)  setSettings(prev => ({ ...prev, ...s }))
        if (c)  setConfig(c)
        if (sd) setSymbolDefs(sd)
      } catch (err) { setError('Invalid settings file: ' + err.message) }
    }
    reader.readAsText(file)
    settingsFileRef.current.value = ''
  }

  // ── Project save / load (ZIP) ─────────────────────────────────────────────
  async function saveProject() {
    try {
      const zip = new JSZip()

      // Write uploaded SVGs as files; replace data URL hrefs with file paths in settings
      const processedSymbolDefs = {}
      const usedSlugs = new Set()
      for (const [type, def] of Object.entries(symbolDefs)) {
        if (def.href?.startsWith('data:')) {
          let slug = type.replace(/[^a-z0-9._-]/gi, '_').toLowerCase()
          if (usedSlugs.has(slug)) {
            let i = 2; while (usedSlugs.has(`${slug}_${i}`)) i++; slug = `${slug}_${i}`
          }
          usedSlugs.add(slug)
          const path = `symbols/${slug}.svg`
          const [, b64] = def.href.split(',')
          zip.file(path, b64, { base64: true })
          processedSymbolDefs[type] = { ...def, href: `/${path}` }
        } else {
          processedSymbolDefs[type] = def
        }
      }

      zip.file('settings.json', JSON.stringify({ settings, config, symbolDefs: processedSymbolDefs }, null, 2))
      if (elements.length)               zip.file('elements.csv',           serializeElementsCsv(elements, overrides, config))
      if (Object.keys(beamPaths).length) zip.file('beam_paths.csv',         serializeBeamPathsCsv(beamPaths))
      if (Object.keys(bgGroups).length)  zip.file('background_objects.csv', serializeBgObjectsCsv(bgGroups))
      const blob = await zip.generateAsync({ type: 'blob' })
      await triggerSave(blob, 'project.zip', 'application/zip', 'zip')
    } catch (e) { if (e.name !== 'AbortError') setError('Save project failed: ' + e.message) }
  }

  async function loadProjectZip(file) {
    if (!file) return
    try {
      const zip = await JSZip.loadAsync(file)

      // Read custom SVG files from the ZIP's symbols/ folder
      const customSvgMap = {}
      await Promise.all(
        Object.keys(zip.files)
          .filter(name => name.startsWith('symbols/') && name.endsWith('.svg'))
          .map(async name => {
            const b64 = await zip.files[name].async('base64')
            customSvgMap[`/${name}`] = `data:image/svg+xml;base64,${b64}`
          })
      )

      const readZipFile = async name => {
        const f = zip.file(name); return f ? await f.async('string') : null
      }
      const [settingsText, elemText, pathsText, bgText] = await Promise.all([
        readZipFile('settings.json'),
        readZipFile('elements.csv'),
        readZipFile('beam_paths.csv'),
        readZipFile('background_objects.csv'),
      ])
      if (settingsText) {
        try {
          const { settings: s, config: c, symbolDefs: sd } = JSON.parse(settingsText)
          if (s)  setSettings(prev => ({ ...prev, ...s }))
          if (c)  setConfig(c)
          if (sd) {
            // Resolve file-path hrefs back to data URLs for custom SVGs
            const resolved = {}
            for (const [type, def] of Object.entries(sd)) {
              resolved[type] = customSvgMap[def.href]
                ? { ...def, href: customSvgMap[def.href] }
                : def
            }
            setSymbolDefs(resolved)
          }
        } catch {}
      }
      if (elemText) {
        const { elements: parsed, config: parsedCfg, error: err } = parseElementsCsv(elemText)
        if (!err || parsed.length) {
          setElements(parsed)
          if (parsedCfg && !settingsText) setConfig(parsedCfg)
          setSelectedLabels(new Set()); setOverrides({}); setHistory([])
        }
      }
      if (pathsText) {
        const { beamPaths: parsed } = parseBeamPathsCsv(pathsText)
        setBeamPaths(parsed); setEditingPath(null)
        const vis = {}; Object.keys(parsed).forEach(k => { vis[k] = true })
        setVisiblePaths(vis)
      }
      if (bgText) {
        const { bgGroups: parsed } = parseBgObjectsCsv(bgText)
        setBgGroups(parsed); setEditingBgGroup(null)
        const vis = {}; Object.keys(parsed).forEach(k => { vis[k] = true })
        setVisibleBg(vis)
      }
      setError(null)
    } catch (e) { setError('Load project failed: ' + e.message) }
    zipFileRef.current.value = ''
  }

  // ── File I/O ───────────────────────────────────────────────────────────────
  function loadElementsFile(file) {
    if (!file) return
    const reader = new FileReader()
    reader.onload = e => {
      const { elements: parsed, config: parsedCfg, error: parseErr } = parseElementsCsv(e.target.result)
      if (parseErr && !parsed.length) { setError(parseErr); return }
      setError(null)
      setElements(parsed)
      if (parsedCfg) setConfig(parsedCfg)
      setSelectedLabels(new Set()); setOverrides({}); setHistory([])
    }
    reader.readAsText(file)
    elemFileRef.current.value = ''
  }

  function loadPathsFile(file) {
    if (!file) return
    const reader = new FileReader()
    reader.onload = e => {
      const { beamPaths: parsed } = parseBeamPathsCsv(e.target.result)
      setBeamPaths(parsed)
      setEditingPath(null)
      const vis = {}; Object.keys(parsed).forEach(k => { vis[k] = true })
      setVisiblePaths(vis)
    }
    reader.readAsText(file)
    pathFileRef.current.value = ''
  }

  function loadBgFile(file) {
    if (!file) return
    const reader = new FileReader()
    reader.onload = e => {
      const { bgGroups: parsed, error: parseErr } = parseBgObjectsCsv(e.target.result)
      if (parseErr) { setError(parseErr); return }
      setBgGroups(parsed)
      setEditingBgGroup(null)
      const vis = {}; Object.keys(parsed).forEach(k => { vis[k] = true })
      setVisibleBg(vis)
    }
    reader.readAsText(file)
    bgFileRef.current.value = ''
  }

  async function saveElementsCSV() {
    const csv = serializeElementsCsv(elements, overrides, config)
    await triggerSave(new Blob([csv], { type: 'text/csv' }), 'elements.csv', 'text/csv', 'csv')
  }

  async function savePathsCSV() {
    const csv = serializeBeamPathsCsv(beamPaths)
    await triggerSave(new Blob([csv], { type: 'text/csv' }), 'beam_paths.csv', 'text/csv', 'csv')
  }

  async function saveBgCSV() {
    const csv = serializeBgObjectsCsv(bgGroups)
    await triggerSave(new Blob([csv], { type: 'text/csv' }), 'background_objects.csv', 'text/csv', 'csv')
  }

  async function handleExportPDF() {
    try { await canvasRef.current?.exportPDF() }
    catch (e) { setError('PDF export failed: ' + e.message) }
  }

  function togglePath(name) { setVisiblePaths(v => ({ ...v, [name]: !v[name] })) }
  function toggleAll(val) {
    const vis = {}; Object.keys(beamPaths).forEach(k => { vis[k] = val })
    setVisiblePaths(vis)
  }
  function toggleBgGroup(name) { setVisibleBg(v => ({ ...v, [name]: !v[name] })) }
  function toggleAllBg(val) {
    const vis = {}; Object.keys(bgGroups).forEach(k => { vis[k] = val })
    setVisibleBg(vis)
  }

  // ── Spreadsheet view data ──────────────────────────────────────────────────
  const elemRows = useMemo(() =>
    allMergedElements.map(el => ({ ...el, _key: el.label })),
    [allMergedElements]
  )

  const elemColumns = useMemo(() => [
    { key: 'label',       label: 'Label',     width: 70  },
    { key: 'type',        label: 'Type',       width: 150 },
    { key: 'x',           label: 'X',          type: 'number', width: 60  },
    { key: 'y',           label: 'Y',          type: 'number', width: 60  },
    { key: 'orientation', label: 'Orient °',   type: 'number', width: 60  },
    { key: 'in_design',   label: 'In Design',  type: 'boolean', width: 70 },
    ...allMetaKeys.map(k => ({ key: k, label: k, width: 110, headerEditable: true })),
  ], [allMetaKeys])

  const beamPathRows = useMemo(() => {
    const rows = []
    Object.entries(beamPaths).sort(([a], [b]) => a.localeCompare(b)).forEach(([name, { color, edges }]) => {
      ;(edges ?? []).forEach(([src, dest], idx) => {
        rows.push({ _key: `${name}__${idx}`, _pathName: name, _edgeIdx: idx, name, color, src, dest })
      })
    })
    return rows
  }, [beamPaths])

  const PATH_COLUMNS = [
    { key: 'name',  label: 'Name',  width: 150, readOnly: true, dim: true },
    { key: 'color', label: 'Color', type: 'color', width: 50, readOnly: true },
    { key: 'src',   label: 'Src',   width: 80  },
    { key: 'dest',  label: 'Dest',  width: 80  },
  ]

  const bgObjectRows = useMemo(() => {
    const rows = []
    Object.entries(bgGroups).sort(([a], [b]) => a.localeCompare(b)).forEach(([group, { color, strokeWidth, edges }]) => {
      ;(edges ?? []).forEach(([x1, y1, x2, y2], idx) => {
        rows.push({ _key: `${group}__${idx}`, _groupName: group, _edgeIdx: idx, group, color, strokeWidth: strokeWidth ?? 2, x1, y1, x2, y2 })
      })
    })
    return rows
  }, [bgGroups])

  const BG_COLUMNS = [
    { key: 'group',       label: 'Group',  width: 130, readOnly: true, dim: true },
    { key: 'color',       label: 'Color',  type: 'color',  width: 50, readOnly: true },
    { key: 'strokeWidth', label: 'Stroke', type: 'number', width: 58 },
    { key: 'x1', label: 'x1', type: 'number', width: 70 },
    { key: 'y1', label: 'y1', type: 'number', width: 70 },
    { key: 'x2', label: 'x2', type: 'number', width: 70 },
    { key: 'y2', label: 'y2', type: 'number', width: 70 },
  ]

  // ── Spreadsheet edit handlers ──────────────────────────────────────────────
  function renameElement(oldLabel, newLabel) {
    const trimmed = newLabel.trim()
    if (!trimmed || trimmed === oldLabel || elements.some(el => el.label === trimmed)) return
    pushHistory()
    setElements(els => els.map(el => el.label === oldLabel ? { ...el, label: trimmed } : el))
    setOverrides(ov => {
      const n = { ...ov }
      if (n[oldLabel]) { n[trimmed] = n[oldLabel]; delete n[oldLabel] }
      return n
    })
    setSelectedLabels(prev => {
      const next = new Set(prev)
      if (next.has(oldLabel)) { next.delete(oldLabel); next.add(trimmed) }
      return next
    })
  }

  const CORE_COL_SET = new Set(['label', 'type', 'x', 'y', 'orientation', 'in_design'])

  function addMetaColumn(key) {
    const trimmed = key.trim()
    if (!trimmed || CORE_COL_SET.has(trimmed.toLowerCase()) || allMetaKeys.includes(trimmed)) return
    pushHistory()
    setElements(els => els.map(el => ({ ...el, [trimmed]: el[trimmed] ?? '' })))
  }

  function renameMetaColumn(oldKey, newKey) {
    const trimmed = newKey.trim()
    if (!trimmed || trimmed === oldKey || CORE_COL_SET.has(trimmed.toLowerCase()) || allMetaKeys.includes(trimmed)) return
    pushHistory()
    setElements(els => els.map(el => {
      if (!(oldKey in el)) return el
      const { [oldKey]: val, ...rest } = el
      return { ...rest, [trimmed]: val }
    }))
    setOverrides(ov => {
      const n = {}
      for (const [label, patch] of Object.entries(ov)) {
        if (oldKey in patch) {
          const { [oldKey]: val, ...rest } = patch
          n[label] = { ...rest, [trimmed]: val }
        } else {
          n[label] = patch
        }
      }
      return n
    })
  }

  function deleteMetaColumn(key) {
    pushHistory()
    setElements(els => els.map(el => { const { [key]: _, ...rest } = el; return rest }))
    setOverrides(ov => {
      const n = {}
      for (const [label, patch] of Object.entries(ov)) {
        const { [key]: _, ...rest } = patch
        n[label] = rest
      }
      return n
    })
  }

  function handleElemCellChange(row, key, value) {
    if (key === 'label') renameElement(row.label, value)
    else updateElementField(row.label, key, value)
  }

  function handleElemDeleteRow(row) {
    pushHistory()
    setElements(els => els.filter(el => el.label !== row.label))
    setOverrides(ov => { const n = { ...ov }; delete n[row.label]; return n })
    setSelectedLabels(prev => { const next = new Set(prev); next.delete(row.label); return next })
  }

  function handleElemAddRow() {
    const label = nextOLabel(elements)
    const ox = config.origin_x ?? 0, oy = config.origin_y ?? 0
    addElement({ type: '', x: Math.round((ox + config.table_length / 2) * 2) / 2, y: Math.round((oy + config.table_width / 2) * 2) / 2, label })
  }

  function handlePathCellChange(row, key, value) {
    const { _pathName, _edgeIdx } = row
    if (key === 'color') {
      pushHistory()
      setBeamPaths(bp => ({ ...bp, [_pathName]: { ...bp[_pathName], color: value } }))
    } else if (key === 'name' && value.trim() && value.trim() !== _pathName) {
      const trimmed = value.trim()
      const edge = (beamPaths[_pathName]?.edges ?? [])[_edgeIdx] ?? ['', '']
      const oldEdgesAfter = (beamPaths[_pathName]?.edges ?? []).filter((_, i) => i !== _edgeIdx)
      const isNewPath = !beamPaths[trimmed]
      pushHistory()
      setBeamPaths(bp => {
        const n = { ...bp }
        const kept = (n[_pathName]?.edges ?? []).filter((_, i) => i !== _edgeIdx)
        if (!kept.length) delete n[_pathName]; else n[_pathName] = { ...n[_pathName], edges: kept }
        if (!n[trimmed]) n[trimmed] = { color: row.color, edges: [] }
        n[trimmed] = { ...n[trimmed], edges: [...n[trimmed].edges, edge] }
        return n
      })
      if (isNewPath)          setVisiblePaths(v => ({ ...v, [trimmed]: true }))
      if (!oldEdgesAfter.length) setVisiblePaths(v => { const n = { ...v }; delete n[_pathName]; return n })
    } else if (key === 'src' || key === 'dest') {
      pushHistory()
      setBeamPaths(bp => {
        const path = bp[_pathName]
        const edges = [...(path?.edges ?? [])]
        const [s, d] = edges[_edgeIdx] ?? ['', '']
        edges[_edgeIdx] = key === 'src' ? [value, d] : [s, value]
        return { ...bp, [_pathName]: { ...path, edges } }
      })
    }
  }

  function handlePathDeleteRow(row) {
    const { _pathName, _edgeIdx } = row
    pushHistory()
    setBeamPaths(bp => {
      const path = bp[_pathName]
      if (!path) return bp
      return { ...bp, [_pathName]: { ...path, edges: (path.edges ?? []).filter((_, i) => i !== _edgeIdx) } }
    })
  }

  function handlePathAddRow() {
    const names = Object.keys(beamPaths).sort()
    pushHistory()
    if (!names.length) {
      setBeamPaths(bp => ({ ...bp, 'New Path': { color: '#4a90d9', edges: [['', '']] } }))
      setVisiblePaths(v => ({ ...v, 'New Path': true }))
    } else {
      const first = names[0]
      setBeamPaths(bp => ({ ...bp, [first]: { ...bp[first], edges: [...(bp[first].edges ?? []), ['', '']] } }))
    }
  }

  function handleBgCellChange(row, key, value) {
    const { _groupName, _edgeIdx } = row
    if (key === 'color') {
      pushHistory(); setBgGroupColor(_groupName, value)
    } else if (key === 'strokeWidth') {
      pushHistory(); setBgGroupStroke(_groupName, parseFloat(value) || 1)
    } else if (key === 'group' && value.trim() && value.trim() !== _groupName) {
      const trimmed = value.trim()
      const edge = (bgGroups[_groupName]?.edges ?? [])[_edgeIdx] ?? [0, 0, 0, 0]
      const oldEdgesAfter = (bgGroups[_groupName]?.edges ?? []).filter((_, i) => i !== _edgeIdx)
      const isNewGroup = !bgGroups[trimmed]
      pushHistory()
      setBgGroups(g => {
        const n = { ...g }
        const kept = (n[_groupName]?.edges ?? []).filter((_, i) => i !== _edgeIdx)
        if (!kept.length) delete n[_groupName]; else n[_groupName] = { ...n[_groupName], edges: kept }
        if (!n[trimmed]) n[trimmed] = { color: row.color, strokeWidth: row.strokeWidth, edges: [] }
        n[trimmed] = { ...n[trimmed], edges: [...n[trimmed].edges, edge] }
        return n
      })
      if (isNewGroup)           setVisibleBg(v => ({ ...v, [trimmed]: true }))
      if (!oldEdgesAfter.length) setVisibleBg(v => { const n = { ...v }; delete n[_groupName]; return n })
    } else if (['x1', 'y1', 'x2', 'y2'].includes(key)) {
      updateBgEdge(_groupName, _edgeIdx, { [key]: parseFloat(value) || 0 })
    }
  }

  function handleBgDeleteRow(row) { deleteBgEdge(row._groupName, row._edgeIdx) }

  function handleBgAddRow() {
    const names = Object.keys(bgGroups).sort()
    if (!names.length) {
      pushHistory()
      setBgGroups(g => ({ ...g, 'New Group': { color: '#888888', strokeWidth: 2, edges: [[0, 0, 0, 0]] } }))
      setVisibleBg(v => ({ ...v, 'New Group': true }))
    } else {
      addBgEdge(names[0], 0, 0, 0, 0)
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app">
      <header className="app-header">
        <span className="app-title">👁️ Optical Table Designer</span>
        <div className="header-controls">
          <a className="file-btn" href="https://github.com/ChinlabLiCsCode/OpticalDesign" target="_blank" rel="noreferrer">GitHub</a>
          <div className="file-menu" ref={fileMenuRef}>
            <button className="file-btn" onClick={() => setFileMenuOpen(o => !o)}>File ▾</button>
            {fileMenuOpen && (
              <div className="file-menu-dropdown">
                <div className="file-menu-label">Load</div>
                <button className="file-menu-item" onClick={() => { elemFileRef.current.click(); setFileMenuOpen(false) }}>Load Elements…</button>
                <button className="file-menu-item" onClick={() => { pathFileRef.current.click(); setFileMenuOpen(false) }}>Load Paths…</button>
                <button className="file-menu-item" onClick={() => { bgFileRef.current.click(); setFileMenuOpen(false) }}>Load Objects…</button>
                <button className="file-menu-item" onClick={() => { settingsFileRef.current.click(); setFileMenuOpen(false) }}>Load Settings…</button>
                <div className="file-menu-sep" />
                <div className="file-menu-label">Save</div>
                <button className="file-menu-item" onClick={() => { saveElementsCSV(); setFileMenuOpen(false) }} disabled={!effectiveElements.length}>Save Elements</button>
                <button className="file-menu-item" onClick={() => { savePathsCSV(); setFileMenuOpen(false) }} disabled={!Object.keys(beamPaths).length}>Save Paths</button>
                <button className="file-menu-item" onClick={() => { saveBgCSV(); setFileMenuOpen(false) }} disabled={!Object.keys(bgGroups).length}>Save Objects</button>
                <button className="file-menu-item" onClick={() => { saveSettingsJSON(); setFileMenuOpen(false) }}>Save Settings</button>
              </div>
            )}
          </div>
          <div className="file-menu" ref={viewMenuRef}>
            <button className="file-btn" onClick={() => setViewMenuOpen(o => !o)}>View ▾</button>
            {viewMenuOpen && (
              <div className="file-menu-dropdown">
                <button className="file-menu-item" onClick={() => { setViewModal('elements'); setViewMenuOpen(false) }}>Elements</button>
                <button className="file-menu-item" onClick={() => { setViewModal('paths'); setViewMenuOpen(false) }}>Beam Paths</button>
                <button className="file-menu-item" onClick={() => { setViewModal('objects'); setViewMenuOpen(false) }}>Background Objects</button>
              </div>
            )}
          </div>
          <span className="hdr-sep" />
          <button className="file-btn" onClick={() => zipFileRef.current.click()}>Open Project</button>
          <button className="file-btn" onClick={saveProject}>Save Project</button>
          <span className="hdr-sep" />
          <button className="file-btn file-btn-accent" onClick={handleExportPDF} disabled={!effectiveElements.length}>Export PDF</button>
        </div>
      </header>

      {error && (
        <div className="gen-banner gen-banner-error">
          <pre>{error}</pre>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="app-body" style={{ position: 'relative' }}>
        {searchOpen && (
          <div style={{
            position: 'absolute', top: 8, right: 8, zIndex: 200,
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'var(--bg-side)', border: '1px solid var(--border-side)',
            borderRadius: 5, padding: '4px 8px', boxShadow: '0 2px 8px #0004',
          }}>
            <input ref={searchInputRef}
              className="snap-input"
              style={{ width: 200 }}
              placeholder="Search label or type…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Escape') { setSearchOpen(false); setSearchQuery('') }
              }} />
            {searchHighlights && (
              <span style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {searchHighlights.size} match{searchHighlights.size !== 1 ? 'es' : ''}
              </span>
            )}
            <button className="small-btn" onClick={() => { setSearchOpen(false); setSearchQuery('') }}>✕</button>
          </div>
        )}
        <OpticalCanvas
          ref={canvasRef}
          elements={effectiveElements}
          beamPaths={beamPaths}
          visiblePaths={visiblePaths}
          bgGroups={bgGroups}
          visibleBg={visibleBg}
          config={config}
          selectedLabels={selectedLabels}
          selectedElement={selectedElement}
          onSelectLabel={handleSelectLabel}
          onSelectLabels={setSelectedLabels}
          onStartEdit={startEdit}
          onUpdateEdit={updateEdit}
          onDeleteSelected={deleteSelected}
          onHardDeleteSelected={hardDeleteSelected}
          editingPath={editingPath}
          onAddEdge={addEdge}
          onDeleteEdge={deleteEdge}
          onSetEditingPath={setEditingPath}
          editingBgGroup={editingBgGroup}
          onAddBgEdge={addBgEdge}
          onDeleteBgEdge={deleteBgEdge}
          onSetEditingBgGroup={setEditingBgGroup}
          symbolDefs={symbolDefs}
          settings={settings}
          searchHighlights={searchHighlights}
          onCursorMove={pos => { cursorPosRef.current = pos }}
        />
        <div
          onMouseDown={startSidebarResize}
          style={{
            width: 4, flexShrink: 0, cursor: 'col-resize', zIndex: 10,
            background: 'transparent', transition: 'background 0.15s',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-bright)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        />
        <Sidebar
          sidebarWidth={sidebarWidth}
          beamPaths={beamPaths}
          visiblePaths={visiblePaths}
          onToggle={togglePath}
          onToggleAll={toggleAll}
          onAddPath={addBeamPath}
          onDeletePath={deleteBeamPath}
          onSetPathColor={setPathColor}
          onRenamePath={renameBeamPath}
          selectedLabels={selectedLabels}
          selectedElement={selectedElement}
          allMetaKeys={allMetaKeys}
          onUpdateElement={updateElementField}
          editingPath={editingPath}
          onSetEditingPath={setEditingPath}
          onDeleteEdge={deleteEdge}
          bgGroups={bgGroups}
          visibleBg={visibleBg}
          onToggleBg={toggleBgGroup}
          onToggleAllBg={toggleAllBg}
          onAddBgGroup={addBgGroup}
          onDeleteBgGroup={deleteBgGroup}
          onSetBgGroupColor={setBgGroupColor}
          onSetBgGroupStroke={setBgGroupStroke}
          onRenameBgGroup={renameBgGroup}
          editingBgGroup={editingBgGroup}
          onSetEditingBgGroup={setEditingBgGroup}
          onDeleteBgEdge={deleteBgEdge}
          onUpdateBgEdge={updateBgEdge}
          config={config}
          onConfigChange={setConfig}
          settings={settings}
          onSettingsChange={setSettings}
          onSaveSettings={saveSettingsJSON}
          onLoadSettings={() => settingsFileRef.current.click()}
          symbolDefs={symbolDefs}
          onAddSymbolDef={addSymbolDef}
          onUpdateSymbolDef={updateSymbolDef}
          onDeleteSymbolDef={deleteSymbolDef}
          onRenameSymbolDef={renameSymbolDef}
          onSelectElement={handleSelectLabel}
          elements={allMergedElements}
          onAddElement={addElement}
          lastAddedTypeRef={lastAddedTypeRef}
          addElemAt={addElemAt}
          onAddElemAtDone={() => setAddElemAt(null)}
        />
      </div>

      {viewModal === 'elements' && (
        <SpreadsheetModal title="Elements" columns={elemColumns} rows={elemRows}
          onCellChange={handleElemCellChange} onDeleteRow={handleElemDeleteRow} onAddRow={handleElemAddRow}
          onRenameColumn={renameMetaColumn} onDeleteColumn={deleteMetaColumn} onAddColumn={addMetaColumn}
          onClose={() => setViewModal(null)} />
      )}
      {viewModal === 'paths' && (
        <SpreadsheetModal title="Beam Paths" columns={PATH_COLUMNS} rows={beamPathRows}
          onCellChange={handlePathCellChange} onDeleteRow={handlePathDeleteRow} onAddRow={handlePathAddRow}
          onClose={() => setViewModal(null)} />
      )}
      {viewModal === 'objects' && (
        <SpreadsheetModal title="Background Objects" columns={BG_COLUMNS} rows={bgObjectRows}
          onCellChange={handleBgCellChange} onDeleteRow={handleBgDeleteRow} onAddRow={handleBgAddRow}
          onClose={() => setViewModal(null)} />
      )}

      <input ref={elemFileRef} type="file" accept=".csv" style={{ display: 'none' }}
        onChange={e => loadElementsFile(e.target.files[0])} />
      <input ref={pathFileRef} type="file" accept=".csv" style={{ display: 'none' }}
        onChange={e => loadPathsFile(e.target.files[0])} />
      <input ref={bgFileRef}   type="file" accept=".csv" style={{ display: 'none' }}
        onChange={e => loadBgFile(e.target.files[0])} />
      <input ref={settingsFileRef} type="file" accept=".json" style={{ display: 'none' }}
        onChange={e => loadSettingsFile(e.target.files[0])} />
      <input ref={zipFileRef} type="file" accept=".zip" style={{ display: 'none' }}
        onChange={e => loadProjectZip(e.target.files[0])} />
    </div>
  )
}
