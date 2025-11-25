// Bar Chart for Average Nutrients
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";

export default function AvgChart({ data }: { data: any[] }) {
  const series = data.map((d: any) => ({
    diet: d.diet_type,
    protein: d.avg_protein_g,
    carbs: d.avg_carbs_g,
    fat: d.avg_fat_g,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={series} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
        <XAxis dataKey="diet" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="carbs" name="Carbs (g)" fill="#f59e0b" />
        <Bar dataKey="fat" name="Fat (g)" fill="#ef4444" />
        <Bar dataKey="protein" name="Protein (g)" fill="#0ea5e9" />
      </BarChart>
    </ResponsiveContainer>
  );
}
