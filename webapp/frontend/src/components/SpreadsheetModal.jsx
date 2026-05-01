import { useState, useRef, useEffect } from 'react'
import './SpreadsheetModal.css'

function hexColor(color) {
  if (!color) return '#888888'
  if (color.startsWith('#')) return color.length === 4
    ? '#' + [...color.slice(1)].map(c => c + c).join('') : color.slice(0, 7)
  return '#888888'
}

export default function SpreadsheetModal({
  title, columns, rows,
  onCellChange, onDeleteRow, onAddRow,
  onRenameColumn, onDeleteColumn, onAddColumn,
  onClose,
}) {
  // Cell editing
  const [editCell, setEditCell] = useState(null) // { rowKey, colKey }
  const [editVal,  setEditVal]  = useState('')
  const inputRef = useRef(null)

  // Column header editing
  const [editingHeader, setEditingHeader] = useState(null) // colKey
  const [editHeaderVal, setEditHeaderVal] = useState('')
  const headerInputRef  = useRef(null)
  const headerCancelRef = useRef(false) // prevent blur from committing after Escape

  // Add column
  const [addingColumn, setAddingColumn] = useState(false)
  const [newColVal,    setNewColVal]    = useState('')
  const newColInputRef = useRef(null)

  useEffect(() => { if (editCell)       inputRef.current?.select()    }, [editCell])
  useEffect(() => { if (editingHeader)  headerInputRef.current?.select() }, [editingHeader])
  useEffect(() => { if (addingColumn)   newColInputRef.current?.focus()  }, [addingColumn])

  // Global Escape: close modal only when nothing is being edited
  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape' && !editCell && !editingHeader && !addingColumn) onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [editCell, editingHeader, addingColumn, onClose])

  // ── Cell editing ───────────────────────────────────────────────────────────
  function startEdit(rowKey, colKey, value) {
    setEditCell({ rowKey, colKey })
    setEditVal(String(value ?? ''))
  }

  function commitEdit() {
    if (!editCell) return
    const { rowKey, colKey } = editCell
    const row = rows.find(r => r._key === rowKey)
    if (row) onCellChange(row, colKey, editVal)
    setEditCell(null)
  }

  function handleCellKeyDown(e, rowIdx, colKey) {
    if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault()
      const row = rows.find(r => r._key === editCell?.rowKey)
      if (row) onCellChange(row, colKey, editVal)
      setEditCell(null)

      const editableCols = columns.filter(c => c.type !== 'boolean' && c.type !== 'color' && !c.readOnly)
      const curIdx = editableCols.findIndex(c => c.key === colKey)
      let nextColKey = colKey, nextRowIdx = rowIdx
      if (e.key === 'Tab') {
        const nextIdx = (curIdx + 1) % editableCols.length
        nextColKey = editableCols[nextIdx]?.key ?? colKey
        if (nextIdx === 0) nextRowIdx = Math.min(rowIdx + 1, rows.length - 1)
      } else {
        nextRowIdx = Math.min(rowIdx + 1, rows.length - 1)
      }
      const nextRow = rows[nextRowIdx]
      if (nextRow && (nextRowIdx !== rowIdx || nextColKey !== colKey))
        setTimeout(() => startEdit(nextRow._key, nextColKey, nextRow[nextColKey]), 0)
    }
    if (e.key === 'Escape') setEditCell(null)
  }

  // ── Column header editing ──────────────────────────────────────────────────
  function startHeaderEdit(colKey, currentLabel) {
    headerCancelRef.current = false
    setEditingHeader(colKey)
    setEditHeaderVal(currentLabel)
  }

  function commitHeader(colKey) {
    if (!headerCancelRef.current && onRenameColumn) {
      const trimmed = editHeaderVal.trim()
      if (trimmed && trimmed !== colKey) onRenameColumn(colKey, trimmed)
    }
    headerCancelRef.current = false
    setEditingHeader(null)
  }

  function cancelHeader() {
    headerCancelRef.current = true
    setEditingHeader(null)
  }

  // ── Add column ─────────────────────────────────────────────────────────────
  function commitAddColumn() {
    const trimmed = newColVal.trim()
    if (trimmed && onAddColumn) onAddColumn(trimmed)
    setAddingColumn(false)
    setNewColVal('')
  }

  return (
    <div className="ss-overlay" onMouseDown={e => { if (e.target === e.currentTarget) onClose() }}>
      <div className="ss-modal">
        <div className="ss-header">
          <span className="ss-title">{title}</span>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{rows.length} rows</span>
            {onAddColumn && !addingColumn && (
              <button className="small-btn" onClick={() => setAddingColumn(true)}>+ Column</button>
            )}
            {onAddColumn && addingColumn && (
              <>
                <input ref={newColInputRef} className="snap-input" style={{ width: 120 }}
                  placeholder="Column name"
                  value={newColVal}
                  onChange={e => setNewColVal(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') commitAddColumn()
                    if (e.key === 'Escape') { setAddingColumn(false); setNewColVal('') }
                  }} />
                <button className="small-btn" onClick={commitAddColumn}>Add</button>
                <button className="small-btn" onClick={() => { setAddingColumn(false); setNewColVal('') }}>✕</button>
              </>
            )}
            {onAddRow && <button className="small-btn" onClick={onAddRow}>+ Row</button>}
            <button className="small-btn" onClick={onClose}>✕ Close</button>
          </div>
        </div>
        <div className="ss-body">
          <table className="ss-table">
            <thead>
              <tr>
                {columns.map(col => (
                  <th key={col.key} style={{ minWidth: col.width ?? 80 }}>
                    {col.headerEditable && editingHeader === col.key ? (
                      <input
                        ref={headerInputRef}
                        className="ss-header-input"
                        value={editHeaderVal}
                        onChange={e => setEditHeaderVal(e.target.value)}
                        onBlur={() => commitHeader(col.key)}
                        onKeyDown={e => {
                          if (e.key === 'Enter') e.target.blur()
                          if (e.key === 'Escape') { cancelHeader(); e.target.blur() }
                        }}
                      />
                    ) : (
                      <div className={`ss-th-content ${col.headerEditable ? 'ss-th-editable' : ''}`}
                        onDoubleClick={() => col.headerEditable && onRenameColumn && startHeaderEdit(col.key, col.label)}>
                        <span>{col.label}</span>
                        {col.headerEditable && onDeleteColumn && (
                          <button className="ss-col-del-btn" title="Delete column"
                            onClick={() => onDeleteColumn(col.key)}>✕</button>
                        )}
                      </div>
                    )}
                  </th>
                ))}
                {onDeleteRow && <th style={{ width: 28 }} />}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIdx) => (
                <tr key={row._key}>
                  {columns.map((col) => {
                    const value = row[col.key]
                    const isEditing = editCell?.rowKey === row._key && editCell?.colKey === col.key

                    if (col.type === 'boolean') {
                      return (
                        <td key={col.key} className="ss-td-center">
                          <input type="checkbox"
                            checked={value !== false && value !== 'FALSE'}
                            onChange={e => onCellChange(row, col.key, e.target.checked)} />
                        </td>
                      )
                    }
                    if (col.type === 'color') {
                      return (
                        <td key={col.key} className="ss-td-center">
                          {col.readOnly ? (
                            <span className="ss-color-swatch" style={{ background: hexColor(value), opacity: 0.5 }} title={value} />
                          ) : (
                            <label className="ss-color-swatch" style={{ background: hexColor(value) }} title={value}>
                              <input type="color" value={hexColor(value)}
                                onChange={e => onCellChange(row, col.key, e.target.value)} />
                            </label>
                          )}
                        </td>
                      )
                    }
                    return (
                      <td key={col.key}
                        className={`ss-td ${col.readOnly ? 'ss-td-readonly' : 'ss-td-editable'}`}
                        onClick={() => !col.readOnly && !isEditing && startEdit(row._key, col.key, value)}>
                        {isEditing ? (
                          <input ref={inputRef} className="ss-cell-input"
                            type={col.type === 'number' ? 'number' : 'text'}
                            value={editVal}
                            onChange={e => setEditVal(e.target.value)}
                            onBlur={commitEdit}
                            onKeyDown={e => handleCellKeyDown(e, rowIdx, col.key)}
                          />
                        ) : (
                          <span className="ss-cell-value"
                            style={col.dim ? { color: 'var(--text-muted)' } : undefined}>
                            {String(value ?? '')}
                          </span>
                        )}
                      </td>
                    )
                  })}
                  {onDeleteRow && (
                    <td className="ss-td-center">
                      <button className="ss-delete-btn" onClick={() => onDeleteRow(row)}>✕</button>
                    </td>
                  )}
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={columns.length + (onDeleteRow ? 1 : 0)} className="ss-empty">No rows</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
