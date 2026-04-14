import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import type { ParticipantPoint } from '../api'

interface Props {
  participants: ParticipantPoint[]
  k: number
  varianceExplained: number[]
}

const CLUSTER_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

function cross(O: number[], A: number[], B: number[]) {
  return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])
}

function convexHull(points: { x: number; y: number }[]): { x: number; y: number }[] {
  if (points.length < 3) return points
  const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y)
  const lower: { x: number; y: number }[] = []
  for (const p of sorted) {
    while (lower.length >= 2 && cross(
      [lower[lower.length - 2].x, lower[lower.length - 2].y],
      [lower[lower.length - 1].x, lower[lower.length - 1].y],
      [p.x, p.y]
    ) <= 0) lower.pop()
    lower.push(p)
  }
  const upper: { x: number; y: number }[] = []
  for (const p of [...sorted].reverse()) {
    while (upper.length >= 2 && cross(
      [upper[upper.length - 2].x, upper[upper.length - 2].y],
      [upper[upper.length - 1].x, upper[upper.length - 1].y],
      [p.x, p.y]
    ) <= 0) upper.pop()
    upper.push(p)
  }
  upper.pop()
  lower.pop()
  return lower.concat(upper)
}

export default function ClusterPlot({ participants, k, varianceExplained }: Props) {
  const grouped: Record<number, { x: number; y: number; id: number }[]> = {}
  for (let i = 0; i < k; i++) grouped[i] = []
  for (const p of participants) {
    grouped[p.cluster]?.push({ x: p.pca_x, y: p.pca_y, id: p.id })
  }

  // Build closed hull paths for each group (last point = first point to close the polygon)
  const hulls = Array.from({ length: k }, (_, i) => {
    const pts = grouped[i]
    if (pts.length < 2) return []
    const hull = pts.length < 3 ? pts : convexHull(pts)
    return [...hull, hull[0]] // close the loop
  })

  const xLabel = `PC1 (${(varianceExplained[0] * 100).toFixed(1)}% variance)`
  const yLabel = `PC2 (${(varianceExplained[1] * 100).toFixed(1)}% variance)`

  return (
    <ResponsiveContainer width="100%" height={380}>
      <ScatterChart margin={{ top: 10, right: 20, bottom: 40, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
        <XAxis
          type="number"
          dataKey="x"
          name="PC1"
          label={{ value: xLabel, position: 'insideBottom', offset: -10, fontSize: 12 }}
          tick={{ fontSize: 11 }}
          tickFormatter={(v) => Number(v).toFixed(1)}
        />
        <YAxis
          type="number"
          dataKey="y"
          name="PC2"
          label={{ value: yLabel, angle: -90, position: 'insideLeft', offset: 10, fontSize: 12 }}
          tick={{ fontSize: 11 }}
          tickFormatter={(v) => Number(v).toFixed(1)}
        />
        <Tooltip
          cursor={{ strokeDasharray: '3 3' }}
          content={({ payload }) => {
            if (!payload?.length) return null
            const d = payload[0].payload
            // Skip tooltip for hull outline series (they have no id)
            if (d.id == null) return null
            return (
              <div style={{ background: '#fff', border: '1px solid #e5e7eb', padding: '6px 10px', borderRadius: 6, fontSize: 13 }}>
                <div>Participant #{d.id}</div>
                <div className="text-muted">x: {d.x.toFixed(2)}, y: {d.y.toFixed(2)}</div>
              </div>
            )
          }}
        />
        <Legend
          verticalAlign="top"
          wrapperStyle={{ paddingBottom: 8, fontSize: 13 }}
          formatter={(value) => value}
        />

        {/* Hull outlines — rendered as line-connected Scatter series with invisible dots */}
        {hulls.map((hull, i) =>
          hull.length >= 2 ? (
            <Scatter
              key={`hull-${i}`}
              data={hull}
              fill="transparent"
              line={{ stroke: CLUSTER_COLORS[i % CLUSTER_COLORS.length], strokeWidth: 1.5, strokeDasharray: '6 3', strokeOpacity: 0.5 }}
              shape={() => null as any}
              legendType="none"
              isAnimationActive={false}
            />
          ) : null
        )}

        {/* Data points */}
        {Array.from({ length: k }, (_, i) => (
          <Scatter
            key={i}
            name={`Group ${i + 1}`}
            data={grouped[i]}
            fill={CLUSTER_COLORS[i % CLUSTER_COLORS.length]}
            opacity={0.85}
            r={6}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  )
}
