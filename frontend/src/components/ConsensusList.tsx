import type { StatementStat } from '../api'

interface Props {
  statements: StatementStat[]
}

export default function ConsensusList({ statements }: Props) {
  const consensus = [...statements]
    .filter((s) => s.is_consensus)
    .sort((a, b) => b.agree_rate - a.agree_rate)
    .slice(0, 5)

  if (consensus.length === 0) {
    return (
      <p className="text-muted">
        No consensus statements yet (need &ge;70% agree and &le;20% disagree).
      </p>
    )
  }

  return (
    <ol style={{ paddingLeft: '1.25rem', margin: 0 }}>
      {consensus.map((s) => (
        <li key={s.id} style={{ marginBottom: '0.6rem' }}>
          <span>{s.text}</span>
          <span className="text-muted" style={{ marginLeft: 8 }}>
            ({(s.agree_rate * 100).toFixed(0)}% agree)
          </span>
        </li>
      ))}
    </ol>
  )
}
