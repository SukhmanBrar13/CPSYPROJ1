// Pie Chart for Macronutrient Distribution
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

type AvgItem = { diet_type: string; avg_protein_g: number; avg_carbs_g: number; avg_fat_g: number; };

export default function MacroPie({ data, diet }: { data: AvgItem[]; diet: string }) {
  const row =
    diet === "all"
      ? data[0]
      : data.find((d) => d.diet_type === diet);

  const pie = row
    ? [
        { name: "Protein (g)", value: row.avg_protein_g },
        { name: "Carbs (g)", value: row.avg_carbs_g },
        { name: "Fat (g)", value: row.avg_fat_g },
      ]
    : [];

  const COLORS = ["#0ea5e9", "#f59e0b", "#ef4444"];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie data={pie} dataKey="value" nameKey="name" outerRadius={80}>
          {pie.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}