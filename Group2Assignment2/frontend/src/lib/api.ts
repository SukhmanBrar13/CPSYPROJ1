const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export type SecurityStatus = {
  security_status: string;
  encryption: string;
  access_control: string;
  compliance: string;
  issues: string[];
};

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

export async function fetchRecipesByDiet(diet: string = "all") {
  const r = await fetch(
    `${BASE}/recipes/by_diet?diet=${encodeURIComponent(diet)}`
  );
  if (!r.ok) throw new Error("Failed to fetch recipes");
  return r.json();
}

export async function triggerCloudCleanup() {
  const r = await fetch(`${BASE}/cloud/cleanup`, {
    method: "POST",
  });

  if (!r.ok) {
    const msg = await r.text();
    throw new Error(msg || "Failed to clean up cloud resources");
  }

  return r.json();
}

export async function fetchSecurityStatus(): Promise<SecurityStatus> {
  const r = await fetch(`${BASE}/security/status`);

  if (!r.ok) {
    const msg = await r.text();
    throw new Error(msg || "Failed to fetch security status");
  }

  return r.json();
}

export type TwoFASendResponse = {
  success: boolean;
  message: string;
};

export async function sendTwoFactorCode(): Promise<TwoFASendResponse> {
  const r = await fetch(`${BASE}/auth/2fa/send`, {
    method: "POST",
  });

  if (!r.ok) {
    const msg = await r.text();
    throw new Error(msg || "Failed to send 2FA code");
  }

  return r.json();
}

export type TwoFAResponse = {
  success: boolean;
  message: string;
};

export async function verifyTwoFactor(code: string): Promise<TwoFAResponse> {
  const r = await fetch(`${BASE}/auth/2fa/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!r.ok) {
    const msg = await r.text();
    throw new Error(msg || "Failed to verify 2FA code");
  }

  return r.json();
}