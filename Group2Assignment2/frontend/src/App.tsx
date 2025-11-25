import { useEffect, useMemo, useState } from "react";
import AvgChart from "./components/AvgChart";
import TopProteinTable from "./components/TopProteinTable";
import ClusterChart from "./components/ClusterChart";
import ClusterSummary from "./components/ClusterSummary";
import AvgHeatmap from "./components/AvgHeatmap";
import MacroPie from "./components/MacroPie";
import { fetchAvg, fetchTopProtein, fetchClusters } from "./lib/api";

// ---------- Types ----------
type AvgItem = {
  diet_type: string;
  avg_protein_g: number;
  avg_carbs_g: number;
  avg_fat_g: number;
};
type Recipe = {
  diet_type: string;
  recipe_name: string;
  cuisine_type: string;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
};
type ClusterPoint = { x: number; y: number; label: number };
type DetailView = "recipes" | "clusters" | null;

// ---------- Component ----------
export default function App() {
  // ----- Filters -----
  // Current diet filter (dropdown / search box).
  const [diet, setDiet] = useState<string>("all");
  // Options for the diet dropdown, loaded once from /insights/avg (all).
  const [dietOptions, setDietOptions] = useState<string[]>(["all"]);
  // Text typed in the search box; pressing Enter applies it to "diet".
  const [searchText, setSearchText] = useState<string>("");

  // ----- Data -----
  // Data used by the 4 overview cards (avg and clusters).
  const [avgData, setAvgData] = useState<AvgItem[]>([]);
  const [clusters, setClusters] = useState<ClusterPoint[]>([]);
  // Data for detail “recipes” view.
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  // ----- UI state -----
  // Whether the 4 overview cards are populated (if false, show empty cards).
  const [overviewLoaded, setOverviewLoaded] = useState(false);
  // Which detail view to show below (recipes/clusters), or none.
  const [detailView, setDetailView] = useState<DetailView>(null);
  // Loading + error indicators for user feedback.
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<string>("");

  // ----- Simple pagination sample (2 pages) -----
  const [page, setPage] = useState<number>(1);
  const totalPages = 2;
  function prevPage() {
    setPage((p) => Math.max(1, p - 1));
  }
  function nextPage() {
    setPage((p) => Math.min(totalPages, p + 1));
  }
  function goPage(n: number) {
    setPage(() => Math.min(Math.max(1, n), totalPages));
  }

  function resolveDiet(): string {
    const s = (searchText || "").trim().toLowerCase();
    return s || diet; // when there's searchText, prefer it, else use current diet
 }

  // ----- Constants -----
  const K_FIXED = 4;    // Number of clusters for K-Means (fixed for the UI)
  const TOP_FIXED = 5;  // Top-N recipes (fixed)

  // ----- Apply “searchText” to diet when user presses Enter -----
  function handleSearchKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      const next = (searchText || "").trim().toLowerCase() || "all";
      setDiet(next);
    }
  }

  // ----- Load diet options once (from /insights/avg?diet=all) -----
  useEffect(() => {
    (async () => {
      try {
        const d = await fetchAvg("all");
        const opts = Array.from(new Set<string>(d.items.map((i: AvgItem) => i.diet_type)));
        setDietOptions(["all", ...opts]);
      } catch {
        // ignore; dropdown will still work with ["all"]
      }
    })();
  }, []);

  // ----- Button: fill the 4 overview cards -----
    async function onGetInsights() {
    try {
        setLoading(true);
        setErr(null);
        const resolved = resolveDiet();
        setDiet(resolved);
        const [a, c] = await Promise.all([
        fetchAvg(resolved),
        fetchClusters(K_FIXED, resolved),
        ]);
        setAvgData(a.items ?? []);
        setClusters(c.points ?? []);
        setOverviewLoaded(true);
        setDetailView(null);
        setUpdatedAt(new Date().toLocaleTimeString());
    } catch (e: any) {
        setErr(e?.message ?? "Failed to load insights");
    } finally {
        setLoading(false);
    }
    }

  // ----- Button: show recipes detail table -----
   async function onGetRecipes() {
    try {
        setLoading(true);
        setErr(null);
        const resolved = resolveDiet();
        setDiet(resolved);
        const r = await fetchTopProtein(resolved, TOP_FIXED);
        setRecipes(r.recipes ?? []);
        setDetailView("recipes");
        setUpdatedAt(new Date().toLocaleTimeString());
    } catch (e: any) {
        setErr(e?.message ?? "Failed to load recipes");
    } finally {
        setLoading(false);
    }
    }

  // ----- Button: show clusters detail summary (table) -----
    async function onGetClusters() {
    try {
        setLoading(true);
        setErr(null);
        const resolved = resolveDiet();
        setDiet(resolved);
        const c = await fetchClusters(K_FIXED, resolved);
        setClusters(c.points ?? []);
        setDetailView("clusters");
        setUpdatedAt(new Date().toLocaleTimeString());
    } catch (e: any) {
        setErr(e?.message ?? "Failed to load clusters");
    } finally {
        setLoading(false);
    }
    }

  // ----- Derived table data (kept for symmetry/future filters) -----
  const tableRecipes = useMemo(() => recipes, [recipes]);

  // ---------- Render ----------
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-blue-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-4 text-2xl font-bold">
          Nutritional Insights
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8 space-y-10">
        {/* Explore: always visible. Charts render only after pressing "Get Nutritional Insights" */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Explore Nutritional Insights</h2>
          <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
            {/* Bar Card */}
            <div className="bg-white rounded-lg shadow p-4 overflow-hidden">
              <div className="font-semibold mb-1">Bar Chart</div>
              <p className="text-sm text-gray-600 mb-3">
                Average macronutrient content by diet type.
              </p>
              <div className="h-56 w-full overflow-hidden">
                {overviewLoaded ? <AvgChart data={avgData} /> : null}
              </div>
            </div>

            {/* Scatter Card */}
            <div className="bg-white rounded-lg shadow p-4 overflow-hidden">
              <div className="font-semibold mb-1">Scatter Plot</div>
              <p className="text-sm text-gray-600 mb-3">
                Nutrient relationships (e.g., protein vs carbs).
              </p>
              <div className="h-56 w-full overflow-hidden">
                {overviewLoaded ? <ClusterChart points={clusters} /> : null}
              </div>
            </div>

            {/* Heatmap Card */}
            <div className="bg-white rounded-lg shadow p-4 overflow-hidden">
              <div className="font-semibold mb-1">Heatmap</div>
              <p className="text-sm text-gray-600 mb-3">Nutrient correlations.</p>
              <div className="h-56 w-full">
                {overviewLoaded ? <AvgHeatmap data={avgData} /> : null}
              </div>
            </div>

            {/* Pie Card */}
            <div className="bg-white rounded-lg shadow p-4 overflow-hidden">
              <div className="font-semibold mb-1">Pie Chart</div>
              <p className="text-sm text-gray-600 mb-3">
                Recipe distribution by diet type.
              </p>
              <div className="h-56 w-full overflow-hidden">
                {overviewLoaded ? <MacroPie data={avgData} diet={diet} /> : null}
              </div>
            </div>
          </div>
        </section>

        {/* Filters: dropdown + search box */}
        <section className="space-y-4">
          <h3 className="text-xl font-semibold">Filters and Data Interaction</h3>
          <div className="flex flex-wrap items-center gap-3">
            {/* Search by diet */}
            <input
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onKeyDown={handleSearchKeyDown}
              placeholder="Search by Diet Type"
              className="border rounded-md px-3 py-2 bg-white"
            />
            {/* Diet dropdown */}
            <select
              value={diet}
              onChange={(e) => setDiet(e.target.value)}
              className="border rounded-md px-3 py-2 bg-white"
            >
              {dietOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt === "all" ? "All Diet Types" : opt}
                </option>
              ))}
            </select>

            {/* Lightweight feedback */}
            {loading && <span className="text-sm text-blue-600">Loading…</span>}
            {updatedAt && (
              <span className="text-xs text-gray-500">Updated: {updatedAt}</span>
            )}
            {err && <span className="text-sm text-red-600">{err}</span>}
          </div>
        </section>

        {/* Action Buttons */}
        <section className="space-y-3">
          <h3 className="text-xl font-semibold">API Data Interaction</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={onGetInsights}
              className="px-4 py-2 rounded-md bg-blue-600 text-white"
            >
              Get Nutritional Insights
            </button>
            <button
              onClick={onGetRecipes}
              className="px-4 py-2 rounded-md bg-green-600 text-white"
            >
              Get Recipes
            </button>
            <button
              onClick={onGetClusters}
              className="px-4 py-2 rounded-md bg-purple-600 text-white"
            >
              Get Clusters
            </button>
          </div>
        </section>

        {/* Detail area: shows either Recipes table or Cluster summary */}
        {detailView === "recipes" && (
          <section className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-2">Top Protein Recipes (Top 5)</h3>
            <TopProteinTable recipes={tableRecipes} />
          </section>
        )}

        {detailView === "clusters" && (
          <section className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-2">Cluster Summary</h3>
            <ClusterSummary points={clusters} />
          </section>
        )}

        {/* Pagination: sample two-page control, not wired to any data for now */}
        <section>
          <h3 className="text-xl font-semibold mb-3">Pagination</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={prevPage}
              disabled={page === 1}
              className="px-3 py-1 rounded bg-gray-200 disabled:opacity-50"
            >
              Previous
            </button>
            {[1, 2].map((n) => (
              <button
                key={n}
                onClick={() => goPage(n)}
                className={`px-3 py-1 rounded ${
                  page === n ? "bg-blue-600 text-white" : "bg-gray-200"
                }`}
              >
                {n}
              </button>
            ))}
            <button
              onClick={nextPage}
              disabled={page === totalPages}
              className="px-3 py-1 rounded bg-gray-200 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-blue-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-3 text-sm text-center">
          © 2025 Nutritional Insights. All Rights Reserved.
        </div>
      </footer>
    </div>
  );
}