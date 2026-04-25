import { useState, useMemo, useEffect, useRef } from 'react'
import OpticalCanvas from './components/OpticalCanvas'
import Sidebar from './components/Sidebar'
import { DEFAULT_SYMBOL_DEFS } from './components/ElementShape'
import {
  parseElementsCsv, serializeElementsCsv,
  parseBeamPathsCsv, serializeBeamPathsCsv,
  parseBgObjectsCsv, serializeBgObjectsCsv,
} from './utils/csvUtils'
import './App.css'

const DEFAULT_CONFIG = { table_length: 48, table_width: 36, origin_x: 24, origin_y: 18 }

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

export default function App() {
  const [elements,     setElements]     = useState([])
  const [config,       setConfig]       = useState(DEFAULT_CONFIG)
  const [beamPaths,    setBeamPaths]    = useState({})
  const [visiblePaths, setVisiblePaths] = useState({})
  const [bgGroups,     setBgGroups]     = useState({})
  const [visibleBg,    setVisibleBg]    = useState({})
  const [error,        setError]        = useState(null)

  const [selectedLabel, setSelectedLabel] = useState(null)
  const [overrides,  setOverrides]  = useState({})
  const [history,    setHistory]    = useState([])
  const [editingPath,    setEditingPath]    = useState(null)
  const [editingBgGroup, setEditingBgGroup] = useState(null)

  const [symbolDefs, setSymbolDefs] = useState(() => ({ ...DEFAULT_SYMBOL_DEFS }))

  const [settings, setSettings] = useState({
    snapSpacing:   0.5,
    showONumber:   true,
    showType:      false,
    darkMode:      true,
    gridLineWidth: 0.5,
    scale:         10,
    showCoords:    false,
  })

  const canvasRef        = useRef(null)
  const elemFileRef      = useRef(null)
  const pathFileRef      = useRef(null)
  const bgFileRef        = useRef(null)
  const settingsFileRef  = useRef(null)

  useEffect(() => {
    document.documentElement.dataset.theme = settings.darkMode ? 'dark' : 'light'
  }, [settings.darkMode])

  // ── Derived state ──────────────────────────────────────────────────────────
  const effectiveElements = useMemo(() =>
    elements
      .filter(el => !overrides[el.label]?.deleted)
      .map(el => {
        const ov = overrides[el.label]
        return ov ? { ...el, ...ov, deleted: undefined } : el
      }),
    [elements, overrides]
  )

  const selectedElement = useMemo(
    () => effectiveElements.find(el => el.label === selectedLabel) ?? null,
    [effectiveElements, selectedLabel]
  )

  // ── Element edit helpers ───────────────────────────────────────────────────
  function startEdit()  { setHistory(h => [...h, overrides]) }

  function updateEdit(label, patch) {
    setOverrides(ov => ({ ...ov, [label]: { ...(ov[label] ?? {}), ...patch } }))
  }

  function deleteElement(label) {
    setHistory(h => [...h, overrides])
    setOverrides(ov => ({ ...ov, [label]: { ...(ov[label] ?? {}), deleted: true } }))
    setSelectedLabel(null)
  }

  function undo() {
    setHistory(h => {
      if (!h.length) return h
      const prev = h[h.length - 1]
      setOverrides(prev)
      return h.slice(0, -1)
    })
  }

  useEffect(() => {
    function onKeyDown(e) {
      const tag = document.activeElement?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault(); undo()
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [history, overrides])

  // ── Beam path helpers ──────────────────────────────────────────────────────
  function addEdge(src, dest) {
    if (!editingPath) return
    setBeamPaths(bp => {
      const path = bp[editingPath]
      if (!path) return bp
      return { ...bp, [editingPath]: { ...path, edges: [...(path.edges ?? []), [src, dest]] } }
    })
  }

  function deleteEdge(edgeIndex) {
    if (!editingPath) return
    setBeamPaths(bp => {
      const path = bp[editingPath]
      if (!path) return bp
      return { ...bp, [editingPath]: { ...path, edges: (path.edges ?? []).filter((_, i) => i !== edgeIndex) } }
    })
  }

  function addBeamPath(name, color) {
    if (!name || beamPaths[name]) return
    setBeamPaths(bp => ({ ...bp, [name]: { color, edges: [] } }))
    setVisiblePaths(vp => ({ ...vp, [name]: true }))
  }

  function deleteBeamPath(name) {
    setBeamPaths(bp => { const n = { ...bp }; delete n[name]; return n })
    setVisiblePaths(vp => { const n = { ...vp }; delete n[name]; return n })
    if (editingPath === name) setEditingPath(null)
  }

  function setPathColor(name, color) {
    setBeamPaths(bp => ({ ...bp, [name]: { ...bp[name], color } }))
  }

  // ── Background object helpers ──────────────────────────────────────────────
  function addBgGroup(name, color, strokeWidth) {
    if (!name || bgGroups[name]) return
    setBgGroups(g => ({ ...g, [name]: { color, strokeWidth, edges: [] } }))
    setVisibleBg(v => ({ ...v, [name]: true }))
  }

  function deleteBgGroup(name) {
    setBgGroups(g => { const n = { ...g }; delete n[name]; return n })
    setVisibleBg(v => { const n = { ...v }; delete n[name]; return n })
    if (editingBgGroup === name) setEditingBgGroup(null)
  }

  function setBgGroupColor(name, color) {
    setBgGroups(g => ({ ...g, [name]: { ...g[name], color } }))
  }

  function setBgGroupStroke(name, sw) {
    setBgGroups(g => ({ ...g, [name]: { ...g[name], strokeWidth: sw } }))
  }

  function addBgEdge(groupName, x1, y1, x2, y2) {
    setBgGroups(g => {
      const grp = g[groupName]
      if (!grp) return g
      return { ...g, [groupName]: { ...grp, edges: [...grp.edges, [x1, y1, x2, y2]] } }
    })
  }

  function deleteBgEdge(groupName, idx) {
    setBgGroups(g => {
      const grp = g[groupName]
      if (!grp) return g
      return { ...g, [groupName]: { ...grp, edges: grp.edges.filter((_, i) => i !== idx) } }
    })
  }

  function updateBgEdge(groupName, idx, patch) {
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

  // ── Project save / load ───────────────────────────────────────────────────
  async function saveProject() {
    if (!('showDirectoryPicker' in window)) {
      setError('Project save requires Chrome or Edge (File System Access API).')
      return
    }
    try {
      const dir = await window.showDirectoryPicker({ mode: 'readwrite' })

      async function writeFile(name, text) {
        const fh = await dir.getFileHandle(name, { create: true })
        const w  = await fh.createWritable()
        await w.write(text); await w.close()
      }

      await writeFile('settings.json', JSON.stringify({ settings, config, symbolDefs }, null, 2))
      if (effectiveElements.length)          await writeFile('elements.csv',           serializeElementsCsv(effectiveElements, config))
      if (Object.keys(beamPaths).length)     await writeFile('beam_paths.csv',         serializeBeamPathsCsv(beamPaths))
      if (Object.keys(bgGroups).length)      await writeFile('background_objects.csv', serializeBgObjectsCsv(bgGroups))
    } catch (e) { if (e.name !== 'AbortError') setError('Save project failed: ' + e.message) }
  }

  async function loadProject() {
    if (!('showDirectoryPicker' in window)) {
      setError('Project load requires Chrome or Edge (File System Access API).')
      return
    }
    try {
      const dir = await window.showDirectoryPicker()

      async function readFile(name) {
        try { const fh = await dir.getFileHandle(name); return await (await fh.getFile()).text() }
        catch { return null }
      }

      const [settingsText, elemText, pathsText, bgText] = await Promise.all([
        readFile('settings.json'),
        readFile('elements.csv'),
        readFile('beam_paths.csv'),
        readFile('background_objects.csv'),
      ])

      if (settingsText) {
        try {
          const { settings: s, config: c, symbolDefs: sd } = JSON.parse(settingsText)
          if (s)  setSettings(prev => ({ ...prev, ...s }))
          if (c)  setConfig(c)
          if (sd) setSymbolDefs(sd)
        } catch {}
      }

      if (elemText) {
        const { elements: parsed, config: parsedCfg, error: err } = parseElementsCsv(elemText)
        if (!err || parsed.length) {
          setElements(parsed)
          if (parsedCfg && !settingsText) setConfig(parsedCfg)
          setSelectedLabel(null); setOverrides({}); setHistory([])
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
    } catch (e) { if (e.name !== 'AbortError') setError('Load project failed: ' + e.message) }
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
      setSelectedLabel(null); setOverrides({}); setHistory([])
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
    const csv = serializeElementsCsv(effectiveElements, config)
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

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app">
      <header className="app-header">
        <span className="app-title">LiCs Optical Design</span>
        <div className="header-controls">
          <button className="file-btn" onClick={loadProject}>Open Project</button>
          <button className="file-btn" onClick={saveProject}>Save Project</button>
          <span className="hdr-sep" />
          <button className="file-btn" onClick={() => elemFileRef.current.click()}>Load Elements</button>
          <button className="file-btn" onClick={() => pathFileRef.current.click()}>Load Paths</button>
          <button className="file-btn" onClick={() => bgFileRef.current.click()}>Load Objects</button>
          <span className="hdr-sep" />
          <button className="file-btn" onClick={saveElementsCSV} disabled={!effectiveElements.length}>Save Elements</button>
          <button className="file-btn" onClick={savePathsCSV} disabled={!Object.keys(beamPaths).length}>Save Paths</button>
          <button className="file-btn" onClick={saveBgCSV} disabled={!Object.keys(bgGroups).length}>Save Objects</button>
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

      <div className="app-body">
        <OpticalCanvas
          ref={canvasRef}
          elements={effectiveElements}
          beamPaths={beamPaths}
          visiblePaths={visiblePaths}
          bgGroups={bgGroups}
          visibleBg={visibleBg}
          config={config}
          selectedLabel={selectedLabel}
          selectedElement={selectedElement}
          onSelectLabel={setSelectedLabel}
          onStartEdit={startEdit}
          onUpdateEdit={updateEdit}
          onDeleteElement={deleteElement}
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
        />
        <Sidebar
          beamPaths={beamPaths}
          visiblePaths={visiblePaths}
          onToggle={togglePath}
          onToggleAll={toggleAll}
          onAddPath={addBeamPath}
          onDeletePath={deleteBeamPath}
          onSetPathColor={setPathColor}
          selectedElement={selectedElement}
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
        />
      </div>

      <input ref={elemFileRef} type="file" accept=".csv" style={{ display: 'none' }}
        onChange={e => loadElementsFile(e.target.files[0])} />
      <input ref={pathFileRef} type="file" accept=".csv" style={{ display: 'none' }}
        onChange={e => loadPathsFile(e.target.files[0])} />
      <input ref={bgFileRef}   type="file" accept=".csv" style={{ display: 'none' }}
        onChange={e => loadBgFile(e.target.files[0])} />
      <input ref={settingsFileRef} type="file" accept=".json" style={{ display: 'none' }}
        onChange={e => loadSettingsFile(e.target.files[0])} />
    </div>
  )
}
