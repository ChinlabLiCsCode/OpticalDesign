import { useState } from 'react'
import { colorToHex, AVAILABLE_SYMBOLS } from '../utils/symbols'
import './Sidebar.css'

const SNAP_PRESETS = [0.25, 0.5, 1, 2]

// ── Tiny color swatch that doubles as a color picker ──────────────────────────
function ColorSwatch({ color, onChange, size = 10 }) {
  return (
    <label className="color-swatch" style={{ width: size, height: size, background: color }} title="Change color">
      <input type="color" value={colorToHex(color)} onChange={e => onChange(e.target.value)} />
    </label>
  )
}

export default function Sidebar({
  // Beam paths
  beamPaths, visiblePaths, onToggle, onToggleAll,
  onAddPath, onDeletePath, onSetPathColor,
  // Beam path editing
  selectedElement,
  editingPath, onSetEditingPath, onDeleteEdge,
  // Background objects
  bgGroups, visibleBg, onToggleBg, onToggleAllBg,
  onAddBgGroup, onDeleteBgGroup, onSetBgGroupColor, onSetBgGroupStroke,
  editingBgGroup, onSetEditingBgGroup, onDeleteBgEdge, onUpdateBgEdge,
  // Config + settings
  config, onConfigChange,
  settings, onSettingsChange,
  onSaveSettings, onLoadSettings,
  // Symbol defs
  symbolDefs, onAddSymbolDef, onUpdateSymbolDef, onDeleteSymbolDef,
}) {
  const [tab, setTab] = useState('paths')

  // Beam path add form
  const [addingPath, setAddingPath] = useState(false)
  const [newPathName,  setNewPathName]  = useState('')
  const [newPathColor, setNewPathColor] = useState('#4a90d9')

  // Bg group add form
  const [addingBg,     setAddingBg]     = useState(false)
  const [newBgName,    setNewBgName]    = useState('')
  const [newBgColor,   setNewBgColor]   = useState('#888888')
  const [newBgStroke,  setNewBgStroke]  = useState(2)

  // Symbol def add form
  const [addingSymbol,    setAddingSymbol]    = useState(false)
  const [newSymType,      setNewSymType]      = useState('')
  const [newSymHref,      setNewSymHref]      = useState('b-mir.svg')
  const [newSymDisplayH,  setNewSymDisplayH]  = useState(11)
  const [editingSymType,  setEditingSymType]  = useState(null)

  function set(key, val) { onSettingsChange({ ...settings, [key]: val }) }
  function setNum(key, val) { const v = parseFloat(val); if (!isNaN(v) && v > 0) set(key, v) }
  function setConfig(key, val) {
    const v = parseFloat(val); if (!isNaN(v) && v > 0) onConfigChange({ ...config, [key]: v })
  }

  const pathNames  = Object.keys(beamPaths)
  const allOn      = pathNames.every(n => visiblePaths[n])
  const allOff     = pathNames.every(n => !visiblePaths[n])
  const bgNames    = Object.keys(bgGroups ?? {})
  const allBgOn    = bgNames.every(n => visibleBg?.[n])
  const allBgOff   = bgNames.every(n => !visibleBg?.[n])

  function commitAddPath() {
    const name = newPathName.trim()
    if (!name) return
    onAddPath(name, newPathColor)
    setNewPathName(''); setAddingPath(false)
  }

  function commitAddBg() {
    const name = newBgName.trim()
    if (!name) return
    onAddBgGroup(name, newBgColor, newBgStroke)
    setNewBgName(''); setAddingBg(false)
  }

  function commitAddSymbol() {
    const type = newSymType.trim().toLowerCase()
    if (!type) return
    const href = `/symbols/${newSymHref}`
    // We don't know w/h without loading the SVG — use placeholder aspect ratio 1:1 until user adjusts
    onAddSymbolDef(type, { href, w: newSymDisplayH, h: newSymDisplayH, displayH: newSymDisplayH })
    setNewSymType(''); setAddingSymbol(false)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-tabs">
        <button className={`sidebar-tab ${tab === 'paths'   ? 'active' : ''}`} onClick={() => setTab('paths')}>Paths</button>
        <button className={`sidebar-tab ${tab === 'objects' ? 'active' : ''}`} onClick={() => setTab('objects')}>Objects</button>
        <button className={`sidebar-tab ${tab === 'settings'? 'active' : ''}`} onClick={() => setTab('settings')}>Settings</button>
      </div>

      {/* ── Paths tab ─────────────────────────────────────────────────────── */}
      {tab === 'paths' && (
        <>
          <section className="sidebar-section">
            <div className="sidebar-section-header">
              <span>Beam Paths</span>
              <div className="toggle-all-btns">
                <button onClick={() => onToggleAll(true)}  disabled={allOn}  className="small-btn">All</button>
                <button onClick={() => onToggleAll(false)} disabled={allOff} className="small-btn">None</button>
                <button onClick={() => setAddingPath(p => !p)} className="small-btn">+</button>
              </div>
            </div>

            {addingPath && (
              <div className="add-group-form">
                <input className="snap-input add-name-input" placeholder="Path name"
                  value={newPathName} onChange={e => setNewPathName(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') commitAddPath(); if (e.key === 'Escape') setAddingPath(false) }}
                  autoFocus />
                <ColorSwatch color={newPathColor} onChange={setNewPathColor} size={16} />
                <button className="small-btn" onClick={commitAddPath}>Add</button>
                <button className="small-btn" onClick={() => setAddingPath(false)}>✕</button>
              </div>
            )}

            <ul className="path-list">
              {pathNames.map(name => {
                const { color } = beamPaths[name]
                const on        = visiblePaths[name]
                const isEditing = name === editingPath
                return (
                  <li key={name} className={`path-item ${on ? 'on' : 'off'} ${isEditing ? 'editing' : ''}`}>
                    <ColorSwatch color={color} onChange={c => onSetPathColor(name, c)} />
                    <span className="path-name" onClick={() => onToggle(name)}>{name}</span>
                    <button
                      className={`path-edit-btn ${isEditing ? 'active' : ''}`}
                      title={isEditing ? 'Stop editing' : 'Edit edges'}
                      onClick={() => onSetEditingPath(isEditing ? null : name)}
                    >✎</button>
                    <button className="path-delete-btn" title="Delete path"
                      onClick={() => onDeletePath(name)}>✕</button>
                  </li>
                )
              })}
            </ul>
          </section>

          {/* Beam path edge editor */}
          {editingPath && beamPaths[editingPath] && (
            <section className="sidebar-section path-edit-panel">
              <div className="sidebar-section-header">
                <span style={{ color: beamPaths[editingPath].color }}>● {editingPath}</span>
                <button className="small-btn" onClick={() => onSetEditingPath(null)}>Done</button>
              </div>
              <p className="path-edit-hint">Click src → dest on canvas to add · click edge to delete</p>
              <ul className="edge-list">
                {(beamPaths[editingPath].edges ?? []).map(([src, dest], i) => (
                  <li key={i} className="edge-item">
                    <span className="edge-label">{src} → {dest}</span>
                    <button className="edge-delete" onClick={() => onDeleteEdge(i)}>✕</button>
                  </li>
                ))}
                {!(beamPaths[editingPath].edges ?? []).length && (
                  <li className="edge-empty">No edges yet</li>
                )}
              </ul>
            </section>
          )}

          {/* Selected element detail */}
          {selectedElement && (
            <section className="sidebar-section">
              <div className="sidebar-section-header"><span>Selected</span></div>
              <div className="element-detail">
                <div className="detail-label">{selectedElement.label}</div>
                <table className="detail-table">
                  <tbody>
                    <tr><td>Type</td><td>{selectedElement.type || '—'}</td></tr>
                    <tr><td>X</td><td>{selectedElement.x}</td></tr>
                    <tr><td>Y</td><td>{selectedElement.y}</td></tr>
                    <tr><td>Orientation</td><td>{selectedElement.orientation}°</td></tr>
                    {Object.entries(selectedElement)
                      .filter(([k]) => !['label','type','x','y','orientation','id'].includes(k))
                      .map(([k, v]) => <tr key={k}><td>{k}</td><td>{String(v)}</td></tr>)}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section className="sidebar-section sidebar-hint">
            <p>Scroll to zoom · Drag to pan</p>
            <p>Click element to inspect · ✎ to edit path edges</p>
          </section>
        </>
      )}

      {/* ── Objects tab ───────────────────────────────────────────────────── */}
      {tab === 'objects' && (
        <>
          <section className="sidebar-section">
            <div className="sidebar-section-header">
              <span>Background Objects</span>
              <div className="toggle-all-btns">
                <button onClick={() => onToggleAllBg(true)}  disabled={allBgOn}  className="small-btn">All</button>
                <button onClick={() => onToggleAllBg(false)} disabled={allBgOff} className="small-btn">None</button>
                <button onClick={() => setAddingBg(p => !p)} className="small-btn">+</button>
              </div>
            </div>

            {addingBg && (
              <div className="add-group-form">
                <input className="snap-input add-name-input" placeholder="Group name"
                  value={newBgName} onChange={e => setNewBgName(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') commitAddBg(); if (e.key === 'Escape') setAddingBg(false) }}
                  autoFocus />
                <ColorSwatch color={newBgColor} onChange={setNewBgColor} size={16} />
                <input className="snap-input" type="number" min="0.5" max="20" step="0.5"
                  value={newBgStroke} onChange={e => setNewBgStroke(parseFloat(e.target.value) || 2)}
                  title="Stroke width" style={{ width: 36 }} />
                <button className="small-btn" onClick={commitAddBg}>Add</button>
                <button className="small-btn" onClick={() => setAddingBg(false)}>✕</button>
              </div>
            )}

            <ul className="path-list">
              {bgNames.map(name => {
                const { color, strokeWidth = 2 } = bgGroups[name]
                const on        = visibleBg?.[name]
                const isEditing = name === editingBgGroup
                return (
                  <li key={name} className={`path-item ${on ? 'on' : 'off'} ${isEditing ? 'editing' : ''}`}>
                    <ColorSwatch color={color} onChange={c => onSetBgGroupColor(name, c)} />
                    <span className="path-name" onClick={() => onToggleBg(name)}>{name}</span>
                    <input className="stroke-input" type="number" min="0.5" max="20" step="0.5"
                      value={strokeWidth}
                      onChange={e => onSetBgGroupStroke(name, parseFloat(e.target.value) || 1)}
                      title="Stroke width" />
                    <button
                      className={`path-edit-btn ${isEditing ? 'active' : ''}`}
                      title={isEditing ? 'Stop editing' : 'Edit edges'}
                      onClick={() => onSetEditingBgGroup(isEditing ? null : name)}
                    >✎</button>
                    <button className="path-delete-btn" title="Delete group"
                      onClick={() => onDeleteBgGroup(name)}>✕</button>
                  </li>
                )
              })}
            </ul>
          </section>

          {/* Bg group edge editor */}
          {editingBgGroup && bgGroups?.[editingBgGroup] && (
            <section className="sidebar-section path-edit-panel">
              <div className="sidebar-section-header">
                <span style={{ color: bgGroups[editingBgGroup].color }}>● {editingBgGroup}</span>
                <button className="small-btn" onClick={() => onSetEditingBgGroup(null)}>Done</button>
              </div>
              <p className="path-edit-hint">Click two points on canvas · click edge to delete · edit coords below</p>
              <ul className="edge-list">
                {(bgGroups[editingBgGroup].edges ?? []).map(([x1, y1, x2, y2], i) => (
                  <li key={i} className="edge-item bg-edge-item">
                    <div className="bg-coord-row">
                      <CoordInput label="x1" val={x1} onChange={v => onUpdateBgEdge(editingBgGroup, i, { x1: v })} />
                      <CoordInput label="y1" val={y1} onChange={v => onUpdateBgEdge(editingBgGroup, i, { y1: v })} />
                      <span className="coord-arrow">→</span>
                      <CoordInput label="x2" val={x2} onChange={v => onUpdateBgEdge(editingBgGroup, i, { x2: v })} />
                      <CoordInput label="y2" val={y2} onChange={v => onUpdateBgEdge(editingBgGroup, i, { y2: v })} />
                    </div>
                    <button className="edge-delete" onClick={() => onDeleteBgEdge(editingBgGroup, i)}>✕</button>
                  </li>
                ))}
                {!(bgGroups[editingBgGroup].edges ?? []).length && (
                  <li className="edge-empty">No edges yet</li>
                )}
              </ul>
            </section>
          )}

          <section className="sidebar-section sidebar-hint">
            <p>✎ to enter draw mode</p>
            <p>Click two points to draw a line · click line to delete</p>
          </section>
        </>
      )}

      {/* ── Settings tab ──────────────────────────────────────────────────── */}
      {tab === 'settings' && (
        <>
          <section className="sidebar-section">
            <div className="sidebar-section-header">
              <span>Settings File</span>
              <div className="toggle-all-btns">
                <button className="small-btn" onClick={onLoadSettings}>Load</button>
                <button className="small-btn" onClick={onSaveSettings}>Save</button>
              </div>
            </div>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Appearance</span></div>
            <label className="setting-toggle">
              <input type="checkbox" checked={settings.darkMode}
                onChange={e => set('darkMode', e.target.checked)} />
              <span>Dark mode</span>
            </label>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Canvas Scale (px/in)</span></div>
            <div className="setting-row">
              <span className="setting-label">Scale</span>
              <input className="snap-input" type="number" min="1" max="50" step="1"
                value={settings.scale}
                onChange={e => setNum('scale', e.target.value)} />
            </div>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Table Size (in)</span></div>
            <div className="setting-row">
              <span className="setting-label">Length</span>
              <input className="snap-input" type="number" min="1" step="1"
                value={config.table_length}
                onChange={e => setConfig('table_length', e.target.value)} />
            </div>
            <div className="setting-row">
              <span className="setting-label">Width</span>
              <input className="snap-input" type="number" min="1" step="1"
                value={config.table_width}
                onChange={e => setConfig('table_width', e.target.value)} />
            </div>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Grid</span></div>
            <div className="setting-row">
              <span className="setting-label">Line width</span>
              <input className="snap-input" type="number" min="0.1" max="5" step="0.1"
                value={settings.gridLineWidth}
                onChange={e => setNum('gridLineWidth', e.target.value)} />
            </div>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Move Snap</span></div>
            <div className="setting-row">
              <span className="setting-label">Spacing</span>
              <div className="snap-presets">
                {SNAP_PRESETS.map(v => (
                  <button key={v}
                    className={`snap-btn ${settings.snapSpacing === v ? 'active' : ''}`}
                    onClick={() => set('snapSpacing', v)}>
                    {v}
                  </button>
                ))}
              </div>
            </div>
            <div className="setting-row">
              <span className="setting-label">Custom</span>
              <input className="snap-input" type="number" min="0.1" max="10" step="0.25"
                value={settings.snapSpacing}
                onChange={e => setNum('snapSpacing', e.target.value)} />
              <span className="setting-unit">in</span>
            </div>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Element Labels</span></div>
            <label className="setting-toggle">
              <input type="checkbox" checked={settings.showONumber}
                onChange={e => set('showONumber', e.target.checked)} />
              <span>Show O-number</span>
            </label>
            <label className="setting-toggle">
              <input type="checkbox" checked={settings.showType}
                onChange={e => set('showType', e.target.checked)} />
              <span>Show type label</span>
            </label>
          </section>

          <section className="sidebar-section">
            <div className="sidebar-section-header"><span>Coordinates</span></div>
            <label className="setting-toggle">
              <input type="checkbox" checked={settings.showCoords ?? false}
                onChange={e => set('showCoords', e.target.checked)} />
              <span>Show axis labels</span>
            </label>
          </section>

          {/* Optics Styles */}
          <section className="sidebar-section">
            <div className="sidebar-section-header">
              <span>Optics Styles</span>
              <button className="small-btn" onClick={() => setAddingSymbol(p => !p)}>+</button>
            </div>

            {addingSymbol && (
              <div className="symbol-add-form">
                <div className="setting-row">
                  <span className="setting-label">Type name</span>
                  <input className="snap-input" style={{ flex: 1 }} placeholder="e.g. aom"
                    value={newSymType} onChange={e => setNewSymType(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') commitAddSymbol(); if (e.key === 'Escape') setAddingSymbol(false) }}
                    autoFocus />
                </div>
                <div className="setting-row">
                  <span className="setting-label">SVG file</span>
                  <select className="sym-select" value={newSymHref} onChange={e => setNewSymHref(e.target.value)}>
                    {AVAILABLE_SYMBOLS.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="setting-row">
                  <span className="setting-label">Height (px)</span>
                  <input className="snap-input" type="number" min="1" max="60" step="0.5"
                    value={newSymDisplayH} onChange={e => setNewSymDisplayH(parseFloat(e.target.value) || 11)} />
                </div>
                <div className="setting-row" style={{ justifyContent: 'flex-end', gap: 4 }}>
                  <button className="small-btn" onClick={commitAddSymbol}>Add</button>
                  <button className="small-btn" onClick={() => setAddingSymbol(false)}>Cancel</button>
                </div>
              </div>
            )}

            <div className="sym-list">
              {Object.entries(symbolDefs).map(([type, def]) => (
                <SymbolRow key={type} type={type} def={def}
                  editing={editingSymType === type}
                  onStartEdit={() => setEditingSymType(type)}
                  onStopEdit={() => setEditingSymType(null)}
                  onUpdate={patch => onUpdateSymbolDef(type, patch)}
                  onDelete={() => { onDeleteSymbolDef(type); if (editingSymType === type) setEditingSymType(null) }}
                />
              ))}
            </div>
          </section>
        </>
      )}
    </aside>
  )
}

// ── Coordinate input for bg edges ─────────────────────────────────────────────
function CoordInput({ label, val, onChange }) {
  const [localVal, setLocalVal] = useState(String(val))
  const [focused, setFocused] = useState(false)
  const display = focused ? localVal : String(val)
  return (
    <div className="coord-field">
      <span className="coord-label">{label}</span>
      <input className="coord-input"
        value={display}
        onChange={e => setLocalVal(e.target.value)}
        onFocus={() => { setLocalVal(String(val)); setFocused(true) }}
        onBlur={() => { setFocused(false); const v = parseFloat(localVal); if (!isNaN(v)) onChange(v) }}
        onKeyDown={e => { if (e.key === 'Enter') { e.target.blur() } }}
      />
    </div>
  )
}

// ── Optics style row ──────────────────────────────────────────────────────────
function SymbolRow({ type, def, editing, onStartEdit, onStopEdit, onUpdate, onDelete }) {
  return (
    <div className={`sym-row ${editing ? 'editing' : ''}`}>
      <img className="sym-preview" src={def.href} alt={type} />
      <span className="sym-type" title={type}>{type}</span>
      <button className={`path-edit-btn ${editing ? 'active' : ''}`}
        onClick={() => editing ? onStopEdit() : onStartEdit()}>✎</button>
      <button className="path-delete-btn" onClick={onDelete}>✕</button>
      {editing && (
        <div className="sym-edit-panel">
          <div className="setting-row">
            <span className="setting-label">SVG file</span>
            <select className="sym-select" value={def.href.replace('/symbols/', '')}
              onChange={e => onUpdate({ href: `/symbols/${e.target.value}` })}>
              {AVAILABLE_SYMBOLS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="setting-row">
            <span className="setting-label">Height (px)</span>
            <input className="snap-input" type="number" min="1" max="60" step="0.5"
              value={def.displayH}
              onChange={e => { const v = parseFloat(e.target.value); if (!isNaN(v) && v > 0) onUpdate({ displayH: v }) }} />
          </div>
        </div>
      )}
    </div>
  )
}
