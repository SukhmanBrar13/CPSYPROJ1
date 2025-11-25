// Scatter Plot for Clustering Results
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, Tooltip } from "recharts";

type Pt = { x: number; y: number; label: number };

const COLORS = ["#0ea5e9", "#22c55e", "#ef4444", "#a855f7", "#f59e0b", "#14b8a6", "#e11d48", "#84cc16"];

export default function ClusterChart({ points }: { points: Pt[] }) {
  const byLabel: Record<number, Pt[]> = {};
  points.forEach((p) => {
    (byLabel[p.label] ??= []).push(p);
  });

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
        <XAxis type="number" dataKey="x" name="Carbs (g)" />
        <YAxis type="number" dataKey="y" name="Protein (g)" />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
        {Object.entries(byLabel).map(([label, pts]) => (
          <Scatter key={label} data={pts} name={`Cluster ${label}`} fill={COLORS[Number(label) % COLORS.length]} />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}