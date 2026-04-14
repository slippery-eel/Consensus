import type { StatementStat } from '../api'

interface Props {
  statements: StatementStat[]
}

export default function DivisiveList({ statements }: Props) {
  const divisive = [...statements]
    .filter((s) => s.is_divisive)
    .sort((a, b) => b.cluster_score - a.cluster_score)
    .slice(0, 5)

  if (divisive.length === 0) {
    return (
      <p className="text-muted">
        No divisive statements yet (need 35-65% agree AND 35-65% disagree).
      </p>
    )
  }

  return (
    <ol style={{ paddingLeft: '1.25rem', margin: 0 }}>
      {divisive.map((s) => (
        <li key={s.id} style={{ marginBottom: '0.6rem' }}>
          <span>{s.text}</span>
          <span className="text-muted" style={{ marginLeft: 8 }}>
            ({(s.agree_rate * 100).toFixed(0)}% agree, {(s.disagree_rate * 100).toFixed(0)}% disagree)
          </span>
        </li>
      ))}
    </ol>
  )
}
