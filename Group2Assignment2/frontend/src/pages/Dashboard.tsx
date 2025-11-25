import { useEffect, useState } from "react";
import { fetchAvg, fetchTopProtein, fetchClusters } from "../lib/api";
import AvgChart from "../components/AvgChart";
import TopProteinTable from "../components/TopProteinTable";
import ClusterChart from "../components/ClusterChart";
import SecurityPanel from "../components/SecurityPanel";

export default function Dashboard() {
  const [diet, setDiet] = useState("all");
  const [avgData, setAvgData] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    fetchAvg(diet).then((data) => setAvgData(data.items));
    fetchTopProtein(diet).then((data) => setRecipes(data.recipes));
    fetchClusters(4, diet).then((data) => setClusters(data.points));
  }, [diet]);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-800">Nutritional Insights Dashboard</h1>

      {/* Diet Selector */}
      <div className="flex gap-2">
        <label className="font-semibold">Select Diet Type:</label>
        <select
          value={diet}
          onChange={(e) => setDiet(e.target.value)}
          className="border rounded p-2"
        >
          <option value="all">All Diets</option>
          <option value="keto">Keto</option>
          <option value="paleo">Paleo</option>
          <option value="vegan">Vegan</option>
          <option value="mediterranean">Mediterranean</option>
        </select>
      </div>

      {/* Average Macros Chart */}
      <section className="bg-white p-4 rounded-lg shadow">
        <h2 className="font-semibold mb-2">Average Macronutrients by Diet</h2>
        <AvgChart data={avgData} />
      </section>

      {/* Top Protein Recipes */}
      <section className="bg-white p-4 rounded-lg shadow">
        <h2 className="font-semibold mb-2">Top Protein-Rich Recipes</h2>
        <TopProteinTable recipes={recipes} />
      </section>

      {/* Clusters */}
      <section className="bg-white p-4 rounded-lg shadow">
        <h2 className="font-semibold mb-2">Nutrient Clusters (K-Means)</h2>
        <ClusterChart points={clusters} />
      </section>

      {/* Security & Cloud Section */}
      <SecurityPanel
        onCleanUpClick={() => {
          console.log("Clean up clicked");
        }}
      />

    </div>
  );
}