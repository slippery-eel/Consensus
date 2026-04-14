import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSurvey, createSession, submitResponses } from '../api'
import type { Statement } from '../api'

type Vote = 'agree' | 'disagree' | 'pass'

export default function Survey() {
  const { id } = useParams<{ id: string }>()
  const surveyId = Number(id)

  const [statements, setStatements] = useState<Statement[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [votes, setVotes] = useState<Record<number, Vote>>({})
  const [currentIndex, setCurrentIndex] = useState(0)
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    init()
  }, [surveyId])

  async function init() {
    setLoading(true)
    try {
      const survey = await getSurvey(surveyId)
      setTitle(survey.title)
      setDescription(survey.description)
      const active = survey.statements.filter((s) => s.is_active)
      setStatements(active)

      // Restore or create session
      const storageKey = `consensus_session_${surveyId}`
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const parsed = JSON.parse(stored)
        setSessionId(parsed.sessionId)
        setVotes(parsed.votes || {})
      } else {
        const participant = await createSession(surveyId)
        localStorage.setItem(storageKey, JSON.stringify({ sessionId: participant.id, votes: {} }))
        setSessionId(participant.id)
      }
    } catch {
      setError('Failed to load survey. Please check the URL.')
    } finally {
      setLoading(false)
    }
  }

  function handleVote(vote: Vote) {
    const stmt = statements[currentIndex]
    const newVotes = { ...votes, [stmt.id]: vote }
    setVotes(newVotes)

    // Persist votes to localStorage
    const storageKey = `consensus_session_${surveyId}`
    const stored = localStorage.getItem(storageKey)
    if (stored) {
      const parsed = JSON.parse(stored)
      localStorage.setItem(storageKey, JSON.stringify({ ...parsed, votes: newVotes }))
    }

    // Auto-advance if not on last statement
    if (currentIndex < statements.length - 1) {
      setTimeout(() => setCurrentIndex((i) => i + 1), 150)
    }
  }

  async function handleSubmit() {
    if (!sessionId) return
    setSubmitting(true)
    try {
      // Include all statements: voted ones + pass for unvoted
      const payload = statements.map((s) => ({
        statement_id: s.id,
        vote: (votes[s.id] || 'pass') as Vote,
      }))
      await submitResponses(sessionId, payload)
      setSubmitted(true)
    } catch {
      setError('Failed to submit responses. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  // ── LOADING ─────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="page text-center" style={{ paddingTop: '4rem' }}>
        <p className="text-muted">Loading survey...</p>
      </div>
    )
  }

  // ── ERROR ───────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="page">
        <div className="error-msg">{error}</div>
        <Link to="/admin" className="btn btn-secondary mt-2">Back to Admin</Link>
      </div>
    )
  }

  // ── SUBMITTED ───────────────────────────────────────────────────────────────
  if (submitted) {
    return (
      <div className="page text-center" style={{ paddingTop: '4rem' }}>
        <div className="card" style={{ maxWidth: 480, margin: '0 auto' }}>
          <h2>Thanks for participating!</h2>
          <p className="text-muted mb-2">Your responses have been recorded.</p>
          <Link className="btn btn-primary" to={`/results/${surveyId}`}>
            View Results
          </Link>
        </div>
      </div>
    )
  }

  // ── EMPTY ───────────────────────────────────────────────────────────────────
  if (statements.length === 0) {
    return (
      <div className="page text-center" style={{ paddingTop: '4rem' }}>
        <div className="card" style={{ maxWidth: 480, margin: '0 auto' }}>
          <h2>{title}</h2>
          <p className="text-muted">This survey has no active statements yet.</p>
        </div>
      </div>
    )
  }

  const stmt = statements[currentIndex]
  const answeredCount = Object.keys(votes).length
  const progressPct = (currentIndex / statements.length) * 100
  const isLast = currentIndex === statements.length - 1

  // ── SURVEY ──────────────────────────────────────────────────────────────────
  return (
    <div>
      <nav className="nav">
        <span className="nav-title">{title}</span>
        <span className="text-muted" style={{ marginLeft: 'auto' }}>
          {currentIndex + 1} / {statements.length}
        </span>
      </nav>

      <div className="page" style={{ maxWidth: 640 }}>
        {description && <p className="text-muted mb-2">{description}</p>}

        <div className="progress-bar mb-2">
          <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
        </div>

        <div className="card" style={{ minHeight: 160, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <p style={{ fontSize: '1.1rem', lineHeight: 1.6, margin: 0, textAlign: 'center' }}>
            {stmt.text}
          </p>
        </div>

        <div className="vote-buttons">
          <button
            className={`vote-btn agree ${votes[stmt.id] === 'agree' ? 'selected' : ''}`}
            onClick={() => handleVote('agree')}
          >
            Agree
          </button>
          <button
            className={`vote-btn disagree ${votes[stmt.id] === 'disagree' ? 'selected' : ''}`}
            onClick={() => handleVote('disagree')}
          >
            Disagree
          </button>
          <button
            className={`vote-btn pass ${votes[stmt.id] === 'pass' ? 'selected' : ''}`}
            onClick={() => handleVote('pass')}
          >
            Pass
          </button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
          <button
            className="btn btn-secondary"
            onClick={() => setCurrentIndex((i) => i - 1)}
            disabled={currentIndex === 0}
          >
            Back
          </button>

          <span className="text-muted" style={{ alignSelf: 'center', fontSize: 13 }}>
            {answeredCount} of {statements.length} answered
          </span>

          {isLast ? (
            <button
              className="btn btn-success"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit'}
            </button>
          ) : (
            <button
              className="btn btn-primary"
              onClick={() => setCurrentIndex((i) => i + 1)}
            >
              Next
            </button>
          )}
        </div>

        {error && <div className="error-msg mt-2">{error}</div>}
      </div>
    </div>
  )
}
