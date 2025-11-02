const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function fetchAvg(diet: string = "all") {
  const r = await fetch(`${BASE}/insights/avg?diet=${encodeURIComponent(diet)}`);
  if (!r.ok) throw new Error("Failed to fetch avg insights");
  return r.json();
}

export async function fetchTopProtein(diet: string = "all", top: number = 5) {
  const r = await fetch(
    `${BASE}/recipes/top_protein?diet=${encodeURIComponent(diet)}&top=${top}`
  );
  if (!r.ok) throw new Error("Failed to fetch recipes");
  return r.json();
}

export async function fetchClusters(k: number = 4, diet: string = "all") {
  const r = await fetch(
    `${BASE}/clusters?k=${encodeURIComponent(k)}&diet=${encodeURIComponent(diet)}`
  );
  if (!r.ok) throw new Error("Failed to fetch clusters");
  return r.json();
}