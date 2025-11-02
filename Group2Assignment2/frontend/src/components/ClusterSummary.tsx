type Pt = { x: number; y: number; label: number };

export default function ClusterSummary({ points }: { points: Pt[] }) {
  const byLabel: Record<number, { n: number; sx: number; sy: number }> = {};
  points.forEach(p => {
    if (!byLabel[p.label]) byLabel[p.label] = { n: 0, sx: 0, sy: 0 };
    byLabel[p.label].n += 1;
    byLabel[p.label].sx += p.x;
    byLabel[p.label].sy += p.y;
  });

  const rows = Object.entries(byLabel)
    .map(([label, v]) => ({
      label: Number(label),
      count: v.n,
      cx: v.sx / v.n, // centroid x (Carbs)
      cy: v.sy / v.n, // centroid y (Protein)
    }))
    .sort((a, b) => a.label - b.label);

  if (!rows.length) return null;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left border-b">
            <th className="py-2 pr-4">Cluster</th>
            <th className="py-2 pr-4">Count</th>
            <th className="py-2 pr-4">Centroid Carbs (x)</th>
            <th className="py-2 pr-4">Centroid Protein (y)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.label} className="border-b last:border-0">
              <td className="py-2 pr-4">#{r.label}</td>
              <td className="py-2 pr-4">{r.count}</td>
              <td className="py-2 pr-4">{r.cx.toFixed(2)}</td>
              <td className="py-2 pr-4">{r.cy.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}