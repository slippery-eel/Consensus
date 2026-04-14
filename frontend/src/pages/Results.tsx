import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { runAnalysis, getSurvey, getSummaries, generateSummaries, getOpenAIKeyStatus } from '../api'
import type { AnalysisResult, GroupSummary } from '../api'
import StatementTable from '../components/StatementTable'
import ConsensusList from '../components/ConsensusList'
import DivisiveList from '../components/DivisiveList'
import ClusterPlot from '../components/ClusterPlot'
import GroupSummaryCard from '../components/GroupSummaryCard'

const CLUSTER_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function Results() {
  const { id } = useParams<{ id: string }>()
  const surveyId = Number(id)

  const [k, setK] = useState(2)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [surveyTitle, setSurveyTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [summaries, setSummaries] = useState<GroupSummary[]>([])
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryError, setSummaryError] = useState('')
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false)
  const [currentSummaryK, setCurrentSummaryK] = useState<number | null>(null)

  useEffect(() => {
    loadAll(k)
    getOpenAIKeyStatus().then((s) => setApiKeyConfigured(s.configured)).catch(() => {})
  }, [surveyId])

  async function loadAll(kVal: number) {
    setLoading(true)
    setError('')
    try {
      const [survey, analysis, existing] = await Promise.all([
        getSurvey(surveyId),
        runAnalysis(surveyId, kVal),
        getSummaries(surveyId, kVal),
      ])
      setSurveyTitle(survey.title)
      setResult(analysis)
      if (existing.summaries.length > 0) {
        setSummaries(existing.summaries)
        setCurrentSummaryK(kVal)
      } else {
        setSummaries([])
        setCurrentSummaryK(null)
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to load results'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  function handleKChange(newK: number) {
    setK(newK)
    loadAll(newK)
    setSummaryError('')
  }

  async function handleGenerateSummaries(force = false) {
    setSummaryLoading(true)
    setSummaryError('')
    try {
      const res = await generateSummaries(surveyId, k, force)
      setSummaries(res.summaries)
      setCurrentSummaryK(k)
    } catch (err: any) {
      setSummaryError(err?.response?.data?.detail || 'Failed to generate summaries')
    } finally {
      setSummaryLoading(false)
    }
  }

  const summariesForCurrentK = currentSummaryK === k ? summaries : []

  return (
    <div>
      <nav className="nav">
        <Link className="btn btn-ghost" to="/admin">Admin</Link>
        <span className="nav-title">{surveyTitle || `Survey #${surveyId}`} — Results</span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span className="text-muted" style={{ fontSize: 13 }}>Groups (k):</span>
          {[2, 3, 4].map((kOpt) => (
            <button
              key={kOpt}
              className={`btn ${k === kOpt ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '4px 12px' }}
              onClick={() => handleKChange(kOpt)}
            >
              {kOpt}
            </button>
          ))}
        </div>
      </nav>

      <div className="page-wide">
        {error && <div className="error-msg">{error}</div>}

        {loading && <p className="text-muted text-center" style={{ paddingTop: '2rem' }}>Running analysis...</p>}

        {!loading && result && (
          <>
            <div className="text-muted mb-2" style={{ fontSize: 13 }}>
              {result.n_participants} participant(s) &middot; {result.n_statements} statement(s) &middot; {k} group(s)
            </div>

            {/* PCA Scatter Plot */}
            <div className="card mb-2">
              <h2>Participant Groups</h2>
              <p className="text-muted mb-2" style={{ fontSize: 13 }}>
                Each dot is a participant. Colors show groups. Position reflects overall voting pattern (PCA).
                PC1 explains {(result.pca_variance_explained[0] * 100).toFixed(1)}%,
                PC2 explains {(result.pca_variance_explained[1] * 100).toFixed(1)}% of variance.
              </p>
              <ClusterPlot
                participants={result.participants}
                k={result.k}
                varianceExplained={result.pca_variance_explained}
              />
              <div className="mt-2" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {result.clusters.map((c) => (
                  <Link
                    key={c.k}
                    to={`/results/${surveyId}/cluster/${c.k}`}
                    className="btn btn-ghost"
                    style={{ fontSize: 13, padding: '4px 12px' }}
                  >
                    Group {c.k + 1} ({c.size} people) &rarr;
                  </Link>
                ))}
              </div>
            </div>

            {/* Group Summaries */}
            <div className="card mb-2">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div>
                  <h2 style={{ margin: 0 }}>Group Summaries</h2>
                  <p className="text-muted" style={{ fontSize: 13, marginTop: 4 }}>
                    AI-generated plain-language description of each group's political orientation.
                  </p>
                </div>
                {summariesForCurrentK.length > 0 && (
                  <button
                    className="btn btn-ghost"
                    style={{ fontSize: 12, padding: '4px 10px', flexShrink: 0 }}
                    onClick={() => handleGenerateSummaries(true)}
                    disabled={summaryLoading}
                  >
                    Regenerate
                  </button>
                )}
              </div>

              {summaryError && <div className="error-msg mb-2">{summaryError}</div>}

              {summaryLoading && (
                <p className="text-muted" style={{ fontSize: 14 }}>
                  Generating summaries... (this takes a few seconds)
                </p>
              )}

              {!summaryLoading && summariesForCurrentK.length === 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <button
                    className="btn btn-primary"
                    onClick={() => handleGenerateSummaries(false)}
                    disabled={!apiKeyConfigured}
                    title={!apiKeyConfigured ? 'Add an OpenAI API key in Admin → Settings' : undefined}
                  >
                    Generate Group Summaries
                  </button>
                  {!apiKeyConfigured && (
                    <span className="text-muted" style={{ fontSize: 13 }}>
                      Requires an OpenAI API key —{' '}
                      <Link to="/admin" onClick={() => sessionStorage.setItem('adminTab', 'settings')}>
                        add one in Settings
                      </Link>
                    </span>
                  )}
                </div>
              )}

              {!summaryLoading && summariesForCurrentK.length > 0 && (
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {summariesForCurrentK.map((s) => (
                    <GroupSummaryCard
                      key={s.cluster_idx}
                      summary={s}
                      clusterColor={CLUSTER_COLORS[s.cluster_idx % CLUSTER_COLORS.length]}
                      surveyId={surveyId}
                    />
                  ))}
                </div>
              )}
            </div>

            <div className="grid-2">
              {/* Consensus */}
              <div className="card">
                <h2 style={{ color: '#065f46' }}>Broad Consensus</h2>
                <p className="text-muted mb-2" style={{ fontSize: 12 }}>
                  &ge;70% agree, &le;20% disagree
                </p>
                <ConsensusList statements={result.statements} />
              </div>

              {/* Divisive */}
              <div className="card">
                <h2 style={{ color: '#991b1b' }}>Most Divisive</h2>
                <p className="text-muted mb-2" style={{ fontSize: 12 }}>
                  35-65% agree AND 35-65% disagree
                </p>
                <DivisiveList statements={result.statements} />
              </div>
            </div>

            {/* Cluster comparison table */}
            <div className="card mt-2">
              <h2>Group Comparison</h2>
              <p className="text-muted mb-2" style={{ fontSize: 13 }}>
                Average vote per group per statement (agree=+1, disagree=-1, pass=0). Sorted by group disagreement.
              </p>
              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th style={{ minWidth: 240 }}>Statement</th>
                      {result.clusters.map((c) => {
                        const s = summariesForCurrentK.find(x => x.cluster_idx === c.k)
                        return (
                          <th key={c.k}>
                            {s ? s.label : `Group ${c.k + 1}`}
                            <br />
                            <span style={{ fontWeight: 400, fontSize: 12 }}>n={c.size}</span>
                          </th>
                        )
                      })}
                      <th>Split score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...result.statements]
                      .sort((a, b) => b.cluster_score - a.cluster_score)
                      .map((s) => (
                        <tr key={s.id}>
                          <td>{s.text}</td>
                          {result.clusters.map((c) => {
                            const mean = c.mean_votes[s.id] ?? 0
                            const color = mean > 0.3 ? '#065f46' : mean < -0.3 ? '#991b1b' : '#6b7280'
                            return (
                              <td key={c.k} style={{ color, fontWeight: 600 }}>
                                {mean.toFixed(2)}
                              </td>
                            )
                          })}
                          <td className="text-muted">{s.cluster_score.toFixed(2)}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Full statement table */}
            <div className="card mt-2">
              <h2>All Statements</h2>
              <StatementTable statements={result.statements} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
