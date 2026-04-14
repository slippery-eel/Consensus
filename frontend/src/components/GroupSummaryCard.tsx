import { Link } from 'react-router-dom'
import type { GroupSummary } from '../api'

interface Props {
  summary: GroupSummary
  clusterColor: string
  surveyId: number
}

export default function GroupSummaryCard({ summary, clusterColor, surveyId }: Props) {
  return (
    <div style={{
      background: '#fff',
      border: '1px solid #e5e7eb',
      borderLeft: `4px solid ${clusterColor}`,
      borderRadius: '10px',
      padding: '1.1rem 1.25rem',
      flex: '1 1 260px',
      minWidth: 0,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
        <div>
          <span className="text-muted" style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Group {summary.cluster_idx + 1}
          </span>
          <h3 style={{ margin: '2px 0 0', color: clusterColor, fontSize: '1.05rem' }}>
            {summary.label}
          </h3>
        </div>
        <Link
          to={`/results/${surveyId}/cluster/${summary.cluster_idx}`}
          style={{ fontSize: 13, whiteSpace: 'nowrap', marginLeft: '0.75rem', marginTop: 2 }}
        >
          Detail &rarr;
        </Link>
      </div>

      <p style={{ fontSize: 14, lineHeight: 1.55, color: '#374151', margin: '0.6rem 0' }}>
        {summary.description}
      </p>

      <div style={{ marginTop: '0.75rem' }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Core beliefs
        </span>
        <ul style={{ margin: '0.3rem 0 0', paddingLeft: '1.1rem' }}>
          {summary.core_beliefs.map((b, i) => (
            <li key={i} style={{ fontSize: 13, color: '#374151', marginBottom: 3 }}>{b}</li>
          ))}
        </ul>
      </div>

      <div style={{ marginTop: '0.75rem', background: '#fafafa', borderRadius: 6, padding: '0.5rem 0.65rem' }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Key stance
        </span>
        <p style={{ fontSize: 13, color: '#374151', margin: '0.25rem 0 0', lineHeight: 1.5 }}>
          {summary.key_disagreement}
        </p>
      </div>
    </div>
  )
}
