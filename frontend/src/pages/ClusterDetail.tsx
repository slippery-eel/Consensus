import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { runAnalysis, getSurvey, getSummaries } from '../api'
import type { AnalysisResult, StatementStat, GroupSummary } from '../api'

const CLUSTER_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function ClusterDetail() {
  const { id, clusterId } = useParams<{ id: string; clusterId: string }>()
  const surveyId = Number(id)
  const clusterIdx = Number(clusterId)

  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [surveyTitle, setSurveyTitle] = useState('')
  const [summary, setSummary] = useState<GroupSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    load()
  }, [surveyId, clusterIdx])

  async function load() {
    setLoading(true)
    setError('')
    try {
      // We need to know k — infer from URL or default to max cluster index + 1
      // Fetch with k = clusterIdx + 1 minimum, try k=2 first then adjust
      const survey = await getSurvey(surveyId)
      setSurveyTitle(survey.title)

      // Try k=2, then k=3, etc. until the requested cluster exists
      const kGuess = Math.max(2, clusterIdx + 1)
      const [analysis, existingSummaries] = await Promise.all([
        runAnalysis(surveyId, kGuess),
        getSummaries(surveyId, kGuess),
      ])
      setResult(analysis)
      const found = existingSummaries.summaries.find((s) => s.cluster_idx === clusterIdx)
      setSummary(found ?? null)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="page text-center" style={{ paddingTop: '4rem' }}><p className="text-muted">Loading...</p></div>
  if (error) return <div className="page"><div className="error-msg">{error}</div></div>
  if (!result) return null

  const cluster = result.clusters.find((c) => c.k === clusterIdx)
  if (!cluster) {
    return (
      <div className="page">
        <div className="error-msg">Group {clusterIdx + 1} not found in analysis.</div>
        <Link to={`/results/${surveyId}`} className="btn btn-secondary mt-2">Back to Results</Link>
      </div>
    )
  }

  // Sort statements by cluster score (most group-distinguishing first)
  const stmtsSorted: StatementStat[] = [...result.statements].sort(
    (a, b) => b.cluster_score - a.cluster_score
  )

  // Statements this cluster strongly agreed with (mean_vote > 0.3)
  const topAgree = stmtsSorted
    .filter((s) => (cluster.mean_votes[s.id] ?? 0) > 0.3)
    .sort((a, b) => (cluster.mean_votes[b.id] ?? 0) - (cluster.mean_votes[a.id] ?? 0))
    .slice(0, 5)

  // Statements this cluster strongly disagreed with (mean_vote < -0.3)
  const topDisagree = stmtsSorted
    .filter((s) => (cluster.mean_votes[s.id] ?? 0) < -0.3)
    .sort((a, b) => (cluster.mean_votes[a.id] ?? 0) - (cluster.mean_votes[b.id] ?? 0))
    .slice(0, 5)

  const clusterColor = CLUSTER_COLORS[clusterIdx % CLUSTER_COLORS.length]

  return (
    <div>
      <nav className="nav">
        <Link className="btn btn-ghost" to={`/results/${surveyId}`}>Back to Results</Link>
        <span className="nav-title">
          {surveyTitle} — {summary ? `"${summary.label}"` : `Group ${clusterIdx + 1}`}
        </span>
        <span className="text-muted" style={{ marginLeft: 'auto' }}>
          {cluster.size} participant(s)
        </span>
      </nav>

      {summary && (
        <div style={{
          borderLeft: `5px solid ${clusterColor}`,
          background: '#fafafa',
          borderBottom: '1px solid #e5e7eb',
          padding: '0.85rem 1.5rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.6rem', flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 700, fontSize: '1rem', color: clusterColor }}>
              Group {clusterIdx + 1} · {summary.label}
            </span>
          </div>
          <p style={{ margin: '0.25rem 0 0', fontSize: 14, color: '#374151', lineHeight: 1.55 }}>
            {summary.description}
          </p>
          {summary.core_beliefs.length > 0 && (
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
              {summary.core_beliefs.map((b, i) => (
                <span key={i} className="badge badge-purple" style={{ fontSize: 12 }}>{b}</span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="page">
        <div className="text-muted mb-2" style={{ fontSize: 13 }}>
          Showing Group {clusterIdx + 1} of {result.k} groups.
          This group has {cluster.size} participant(s).
        </div>

        {/* Switch groups */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {result.clusters.map((c) => (
            <Link
              key={c.k}
              to={`/results/${surveyId}/cluster/${c.k}`}
              className={`btn ${c.k === clusterIdx ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: 13, padding: '4px 12px' }}
            >
              Group {c.k + 1} ({c.size})
            </Link>
          ))}
        </div>

        <div className="grid-2">
          <div className="card">
            <h2 style={{ color: '#065f46' }}>Most Agreed With</h2>
            <p className="text-muted mb-2" style={{ fontSize: 12 }}>Statements this group leaned agree on</p>
            {topAgree.length === 0 ? (
              <p className="text-muted">No strong agreements in this group.</p>
            ) : (
              <ol style={{ paddingLeft: '1.25rem', margin: 0 }}>
                {topAgree.map((s) => (
                  <li key={s.id} style={{ marginBottom: '0.6rem' }}>
                    {s.text}
                    <span className="text-muted" style={{ marginLeft: 6 }}>
                      (avg {(cluster.mean_votes[s.id] ?? 0).toFixed(2)})
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </div>

          <div className="card">
            <h2 style={{ color: '#991b1b' }}>Most Disagreed With</h2>
            <p className="text-muted mb-2" style={{ fontSize: 12 }}>Statements this group leaned disagree on</p>
            {topDisagree.length === 0 ? (
              <p className="text-muted">No strong disagreements in this group.</p>
            ) : (
              <ol style={{ paddingLeft: '1.25rem', margin: 0 }}>
                {topDisagree.map((s) => (
                  <li key={s.id} style={{ marginBottom: '0.6rem' }}>
                    {s.text}
                    <span className="text-muted" style={{ marginLeft: 6 }}>
                      (avg {(cluster.mean_votes[s.id] ?? 0).toFixed(2)})
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </div>

        {/* All statement scores for this cluster */}
        <div className="card mt-2">
          <h2>All Statement Scores for Group {clusterIdx + 1}</h2>
          <p className="text-muted mb-2" style={{ fontSize: 13 }}>
            Sorted by how much this statement distinguishes groups. avg vote: +1=agree, -1=disagree, 0=pass.
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th style={{ minWidth: 260 }}>Statement</th>
                  <th>This group avg</th>
                  <th>Split score</th>
                </tr>
              </thead>
              <tbody>
                {stmtsSorted.map((s) => {
                  const mean = cluster.mean_votes[s.id] ?? 0
                  const color = mean > 0.3 ? '#065f46' : mean < -0.3 ? '#991b1b' : '#6b7280'
                  return (
                    <tr key={s.id}>
                      <td>{s.text}</td>
                      <td style={{ color, fontWeight: 600 }}>{mean.toFixed(2)}</td>
                      <td className="text-muted">{s.cluster_score.toFixed(2)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
