import type { StatementStat } from '../api'

interface Props {
  statements: StatementStat[]
}

export default function StatementTable({ statements }: Props) {
  const sorted = [...statements].sort((a, b) => b.agree_rate - a.agree_rate)

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th style={{ minWidth: 260 }}>Statement</th>
            <th>Agree %</th>
            <th>Disagree %</th>
            <th>Pass %</th>
            <th>n</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((s) => (
            <tr key={s.id}>
              <td>{s.text}</td>
              <td>
                <span style={{ color: '#065f46', fontWeight: 600 }}>
                  {(s.agree_rate * 100).toFixed(0)}%
                </span>
              </td>
              <td>
                <span style={{ color: '#991b1b', fontWeight: 600 }}>
                  {(s.disagree_rate * 100).toFixed(0)}%
                </span>
              </td>
              <td className="text-muted">{(s.pass_rate * 100).toFixed(0)}%</td>
              <td className="text-muted">{s.agree_count + s.disagree_count + s.pass_count}</td>
              <td>
                {s.is_consensus && <span className="badge badge-green">Consensus</span>}
                {s.is_divisive && <span className="badge badge-red">Divisive</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
