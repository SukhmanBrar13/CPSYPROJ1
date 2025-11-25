import React, { useEffect, useState } from "react";

type Recipe = {
  recipe_name: string;
  cuisine_type: string;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
};

// Table for Top Protein Recipes with simple pagination (10 per page)
export default function TopProteinTable({ recipes }: { recipes: Recipe[] }) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const totalPages = Math.max(1, Math.ceil(recipes.length / pageSize));

  useEffect(() => {
    setCurrentPage(1);
  }, [recipes]);

  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const pageItems = recipes.slice(startIndex, startIndex + pageSize);

  const handlePrev = () => {
    setCurrentPage((p) => Math.max(1, p - 1));
  };

  const handleNext = () => {
    setCurrentPage((p) => Math.min(totalPages, p + 1));
  };

  const showingFrom = recipes.length === 0 ? 0 : startIndex + 1;
  const showingTo =
    recipes.length === 0 ? 0 : Math.min(startIndex + pageSize, recipes.length);

  return (
    <div className="w-full">
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
          {pageItems.map((r, i) => (
            <tr key={startIndex + i}>
              <td className="border p-2">{r.recipe_name}</td>
              <td className="border p-2">{r.cuisine_type}</td>
              <td className="border p-2 text-right">
                {r.protein_g.toFixed(2)}
              </td>
              <td className="border p-2 text-right">
                {r.carbs_g.toFixed(2)}
              </td>
              <td className="border p-2 text-right">{r.fat_g.toFixed(2)}</td>
            </tr>
          ))}

          {pageItems.length === 0 && (
            <tr>
              <td
                colSpan={5}
                className="border p-4 text-center text-gray-500"
              >
                No recipes to show.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Pagination controls */}
      <div className="mt-2 flex items-center justify-between text-xs sm:text-sm">
        <span className="text-gray-600">
          Showing {showingFrom}–{showingTo} of {recipes.length}
        </span>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handlePrev}
            disabled={safePage === 1}
            className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span>
            Page {safePage} / {totalPages}
          </span>
          <button
            type="button"
            onClick={handleNext}
            disabled={safePage === totalPages || recipes.length === 0}
            className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}