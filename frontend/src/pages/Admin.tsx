import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  listSurveys,
  createSurvey,
  getSurvey,
  addStatement,
  updateStatement,
  deleteStatement,
  getResponses,
  getOpenAIKeyStatus,
  saveOpenAIKey,
} from '../api'
import type { SurveyListItem, Survey, Statement, ResponseItem } from '../api'

type View = 'list' | 'editor' | 'responses' | 'settings'

export default function Admin() {
  const [view, setView] = useState<View>('list')
  const [surveys, setSurveys] = useState<SurveyListItem[]>([])
  const [activeSurvey, setActiveSurvey] = useState<Survey | null>(null)
  const [responses, setResponses] = useState<ResponseItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Settings state
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false)
  const [apiKeySaving, setApiKeySaving] = useState(false)
  const [apiKeySaved, setApiKeySaved] = useState(false)

  // Create survey form
  const [newTitle, setNewTitle] = useState('')
  const [newDesc, setNewDesc] = useState('')

  // Add statement form
  const [newStmt, setNewStmt] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editText, setEditText] = useState('')

  useEffect(() => {
    loadSurveys()
    getOpenAIKeyStatus().then((s) => setApiKeyConfigured(s.configured)).catch(() => {})
  }, [])

  async function loadSurveys() {
    try {
      const data = await listSurveys()
      setSurveys(data)
    } catch {
      setError('Failed to load surveys')
    }
  }

  async function handleCreateSurvey(e: React.FormEvent) {
    e.preventDefault()
    if (!newTitle.trim()) return
    setLoading(true)
    try {
      const survey = await createSurvey(newTitle.trim(), newDesc.trim() || undefined)
      setNewTitle('')
      setNewDesc('')
      await openEditor(survey.id)
    } catch {
      setError('Failed to create survey')
    } finally {
      setLoading(false)
    }
  }

  async function openEditor(id: number) {
    setLoading(true)
    try {
      const survey = await getSurvey(id)
      setActiveSurvey(survey)
      setView('editor')
    } catch {
      setError('Failed to load survey')
    } finally {
      setLoading(false)
    }
  }

  async function handleAddStatement(e: React.FormEvent) {
    e.preventDefault()
    if (!activeSurvey || !newStmt.trim()) return
    setLoading(true)
    try {
      await addStatement(activeSurvey.id, newStmt.trim())
      setNewStmt('')
      const updated = await getSurvey(activeSurvey.id)
      setActiveSurvey(updated)
    } catch {
      setError('Failed to add statement')
    } finally {
      setLoading(false)
    }
  }

  async function handleSaveApiKey(e: React.FormEvent) {
    e.preventDefault()
    if (!apiKeyInput.trim()) return
    setApiKeySaving(true)
    try {
      await saveOpenAIKey(apiKeyInput.trim())
      setApiKeyConfigured(true)
      setApiKeyInput('')
      setApiKeySaved(true)
      setTimeout(() => setApiKeySaved(false), 3000)
    } catch {
      setError('Failed to save API key')
    } finally {
      setApiKeySaving(false)
    }
  }

  async function handleDeleteStatement(stmt: Statement) {
    if (!window.confirm(`Delete statement?\n\n"${stmt.text}"\n\nThis also deletes all votes for this statement.`)) return
    try {
      await deleteStatement(stmt.id)
      setActiveSurvey((s) => s ? { ...s, statements: s.statements.filter((x) => x.id !== stmt.id) } : s)
    } catch {
      setError('Failed to delete statement')
    }
  }

  async function handleToggleActive(stmt: Statement) {
    try {
      const updated = await updateStatement(stmt.id, { is_active: !stmt.is_active })
      setActiveSurvey((s) =>
        s ? { ...s, statements: s.statements.map((x) => x.id === stmt.id ? updated : x) } : s
      )
    } catch {
      setError('Failed to update statement')
    }
  }

  async function handleSaveEdit(stmt: Statement) {
    if (!editText.trim()) return
    try {
      const updated = await updateStatement(stmt.id, { text: editText.trim() })
      setActiveSurvey((s) =>
        s ? { ...s, statements: s.statements.map((x) => x.id === stmt.id ? updated : x) } : s
      )
      setEditingId(null)
    } catch {
      setError('Failed to update statement')
    }
  }

  async function openResponses(id: number) {
    setLoading(true)
    try {
      const [survey, resps] = await Promise.all([getSurvey(id), getResponses(id)])
      setActiveSurvey(survey)
      setResponses(resps)
      setView('responses')
    } catch {
      setError('Failed to load responses')
    } finally {
      setLoading(false)
    }
  }

  // ── SETTINGS ────────────────────────────────────────────────────────────────
  if (view === 'settings') {
    return (
      <div>
        <nav className="nav">
          <button className="btn btn-ghost" onClick={() => setView('list')}>Back</button>
          <span className="nav-title">Settings</span>
        </nav>
        <div className="page" style={{ maxWidth: 560 }}>
          {error && <div className="error-msg">{error}</div>}
          <div className="card">
            <h2>AI Settings</h2>
            <p className="text-muted mb-2" style={{ fontSize: 14 }}>
              Enter your OpenAI API key to enable plain-language group summaries on the Results page.
              Your key is stored on your local server and is never sent anywhere other than OpenAI.
            </p>

            <div className="mb-2" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: 13, fontWeight: 500 }}>Status:</span>
              {apiKeyConfigured
                ? <span className="badge badge-green">Key configured</span>
                : <span className="badge badge-gray">No key set</span>
              }
            </div>

            <form onSubmit={handleSaveApiKey}>
              <div className="mb-2">
                <label>OpenAI API Key</label>
                <input
                  type="password"
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  placeholder="sk-..."
                  required
                />
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <button className="btn btn-primary" type="submit" disabled={apiKeySaving}>
                  {apiKeySaving ? 'Saving...' : apiKeyConfigured ? 'Update Key' : 'Save Key'}
                </button>
                {apiKeySaved && <span className="badge badge-green">Saved!</span>}
              </div>
            </form>
          </div>

          <div className="card" style={{ background: '#fafafa', border: '1px solid #e5e7eb' }}>
            <h3 style={{ marginTop: 0 }}>How summaries work</h3>
            <p style={{ fontSize: 14, lineHeight: 1.6, color: '#374151', margin: 0 }}>
              After running a cluster analysis on the Results page, click <strong>"Generate Group Summaries"</strong>.
              The app sends each group's voting patterns to <strong>gpt-4o-mini</strong> and gets back a plain-language
              description: a group name, a 2–3 sentence characterization, core beliefs, and a key stance.
              Summaries are cached — they only call OpenAI once per survey/k combination unless you force-regenerate.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // ── SURVEY LIST ─────────────────────────────────────────────────────────────
  if (view === 'list') {
    return (
      <div>
        <nav className="nav">
          <span className="nav-title">Consensus — Admin</span>
          <button
            className="btn btn-ghost"
            style={{ marginLeft: 'auto' }}
            onClick={() => setView('settings')}
          >
            Settings {apiKeyConfigured ? '✓' : ''}
          </button>
        </nav>
        <div className="page">
          {error && <div className="error-msg">{error}</div>}

          <div className="card">
            <h2>Create Survey</h2>
            <form onSubmit={handleCreateSurvey}>
              <div className="mb-1">
                <label>Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Team Priorities Q3"
                  required
                />
              </div>
              <div className="mb-2">
                <label>Description (optional)</label>
                <input
                  type="text"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Brief description"
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                Create & add statements
              </button>
            </form>
          </div>

          <h2>Surveys</h2>
          {surveys.length === 0 && <p className="text-muted">No surveys yet. Create one above.</p>}
          {surveys.map((s) => (
            <div className="card" key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ flex: 1 }}>
                <strong>{s.title}</strong>
                {s.description && <span className="text-muted" style={{ marginLeft: 8 }}>{s.description}</span>}
              </div>
              <button className="btn btn-secondary" onClick={() => openEditor(s.id)}>Edit</button>
              <button className="btn btn-ghost" onClick={() => openResponses(s.id)}>Responses</button>
              <Link className="btn btn-secondary" to={`/survey/${s.id}`} target="_blank">
                Take Survey
              </Link>
              <Link className="btn btn-primary" to={`/results/${s.id}`}>
                Results
              </Link>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ── RESPONSES VIEW ──────────────────────────────────────────────────────────
  if (view === 'responses' && activeSurvey) {
    const stmtMap = Object.fromEntries(activeSurvey.statements.map((s) => [s.id, s.text]))
    const participantIds = [...new Set(responses.map((r) => r.participant_id))].sort()

    return (
      <div>
        <nav className="nav">
          <button className="btn btn-ghost" onClick={() => setView('list')}>Back</button>
          <span className="nav-title">{activeSurvey.title} — Raw Responses</span>
        </nav>
        <div className="page-wide">
          {error && <div className="error-msg">{error}</div>}
          <p className="text-muted mb-2">
            {participantIds.length} participant(s), {responses.length} vote(s)
          </p>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Participant</th>
                  <th>Statement</th>
                  <th>Vote</th>
                  <th>When</th>
                </tr>
              </thead>
              <tbody>
                {responses.map((r) => (
                  <tr key={r.id}>
                    <td>#{r.participant_id}</td>
                    <td style={{ maxWidth: 400 }}>{stmtMap[r.statement_id] || r.statement_id}</td>
                    <td>
                      <span className={`badge ${r.vote === 'agree' ? 'badge-green' : r.vote === 'disagree' ? 'badge-red' : 'badge-gray'}`}>
                        {r.vote}
                      </span>
                    </td>
                    <td className="text-muted">{new Date(r.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-2">
            <Link className="btn btn-primary" to={`/results/${activeSurvey.id}`}>View Results & Analysis</Link>
          </div>
        </div>
      </div>
    )
  }

  // ── SURVEY EDITOR ───────────────────────────────────────────────────────────
  if (!activeSurvey) return null

  const activeCount = activeSurvey.statements.filter((s) => s.is_active).length

  return (
    <div>
      <nav className="nav">
        <button className="btn btn-ghost" onClick={() => { setView('list'); loadSurveys() }}>Back</button>
        <span className="nav-title">{activeSurvey.title}</span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem' }}>
          <Link className="btn btn-secondary" to={`/survey/${activeSurvey.id}`} target="_blank">
            Take Survey
          </Link>
          <Link className="btn btn-primary" to={`/results/${activeSurvey.id}`}>
            View Results
          </Link>
        </div>
      </nav>
      <div className="page">
        {error && <div className="error-msg">{error}</div>}

        {activeSurvey.description && (
          <p className="text-muted mb-2">{activeSurvey.description}</p>
        )}

        <div className="card">
          <h2>Add Statement</h2>
          <form onSubmit={handleAddStatement} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              value={newStmt}
              onChange={(e) => setNewStmt(e.target.value)}
              placeholder="Enter a statement participants will vote on..."
              required
              style={{ flex: 1 }}
            />
            <button className="btn btn-primary" type="submit" disabled={loading}>Add</button>
          </form>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <h2 style={{ margin: 0 }}>
            Statements
            <span className="text-muted" style={{ marginLeft: 8, fontWeight: 400 }}>
              {activeCount} active / {activeSurvey.statements.length} total
            </span>
          </h2>
        </div>

        {activeSurvey.statements.length === 0 && (
          <p className="text-muted">No statements yet. Add some above.</p>
        )}

        {activeSurvey.statements.map((stmt, i) => (
          <div
            key={stmt.id}
            className="card"
            style={{ opacity: stmt.is_active ? 1 : 0.55, marginBottom: '0.5rem' }}
          >
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <span className="text-muted" style={{ minWidth: 28, paddingTop: 2 }}>
                {i + 1}.
              </span>
              <div style={{ flex: 1 }}>
                {editingId === stmt.id ? (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input
                      type="text"
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      style={{ flex: 1 }}
                      autoFocus
                    />
                    <button className="btn btn-primary" onClick={() => handleSaveEdit(stmt)}>Save</button>
                    <button className="btn btn-secondary" onClick={() => setEditingId(null)}>Cancel</button>
                  </div>
                ) : (
                  <span>{stmt.text}</span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: 12, padding: '4px 10px' }}
                  onClick={() => { setEditingId(stmt.id); setEditText(stmt.text) }}
                >
                  Edit
                </button>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: 12, padding: '4px 10px' }}
                  onClick={() => handleToggleActive(stmt)}
                >
                  {stmt.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button
                  className="btn btn-danger"
                  style={{ fontSize: 12, padding: '4px 10px' }}
                  onClick={() => handleDeleteStatement(stmt)}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
