// Table for Top Protein Recipes
export default function TopProteinTable({ recipes }: { recipes: any[] }) {
  return (
    <table className="w-full text-sm border-collapse border">
      <thead className="bg-gray-100">
        <tr>
          <th className="border p-2">Recipe</th>
          <th className="border p-2">Cuisine</th>
          <th className="border p-2">Protein (g)</th>
          <th className="border p-2">Carbs (g)</th>
          <th className="border p-2">Fat (g)</th>
        </tr>
      </thead>
      <tbody>
        {recipes.map((r, i) => (
          <tr key={i}>
            <td className="border p-2">{r.recipe_name}</td>
            <td className="border p-2">{r.cuisine_type}</td>
            <td className="border p-2 text-right">{r.protein_g.toFixed(2)}</td>
            <td className="border p-2 text-right">{r.carbs_g.toFixed(2)}</td>
            <td className="border p-2 text-right">{r.fat_g.toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}