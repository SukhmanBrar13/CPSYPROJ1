import React, { useEffect, useState } from "react";
import { fetchSecurityStatus } from "../lib/api";
import type { SecurityStatus } from "../lib/api";
import { triggerCloudCleanup } from "../lib/api";

type Props = {
  onCleanUpClick?: () => void;
};

const FRONTEND_REDIRECT_URI = "http://localhost:5173";

function buildGithubAuthUrl() {
  const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID as string;
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: FRONTEND_REDIRECT_URI,
    scope: "user:email",
    state: "github",
  });
  return `https://github.com/login/oauth/authorize?${params.toString()}`;
}

function buildGoogleAuthUrl() {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string;
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: FRONTEND_REDIRECT_URI,
    response_type: "code",
    scope: "openid email profile",
    state: "google",
    access_type: "online",
    include_granted_scopes: "true",
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}

export default function SecurityPanel({ onCleanUpClick }: Props) {
  // ----- Security & Compliance -----
  const [security, setSecurity] = useState<SecurityStatus | null>(null);
  const [secLoading, setSecLoading] = useState(false);
  const [secError, setSecError] = useState<string | null>(null);

  // ----- Cloud Cleanup -----
  const [cleanupLoading, setCleanupLoading] = useState(false);
  const [cleanupMessage, setCleanupMessage] = useState<string | null>(null);
  const [cleanupError, setCleanupError] = useState<string | null>(null);

  // ----- OAuth & 2FA Integration -----
  const [authMessage, setAuthMessage] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);

  function startGoogleLogin() {
    setAuthMessage(null);
    setAuthError(null);
    window.location.href = buildGoogleAuthUrl();
  }

  function startGithubLogin() {
    setAuthMessage(null);
    setAuthError(null);
    window.location.href = buildGithubAuthUrl();
  }

  // Fetch security status on component mount
  useEffect(() => {
    (async () => {
      try {
        setSecLoading(true);
        setSecError(null);
        const status = await fetchSecurityStatus();
        setSecurity(status);
      } catch (e: any) {
        setSecError(e?.message ?? "Failed to load security status");
      } finally {
        setSecLoading(false);
      }
    })();
  }, []);

  // Handle Cloud Cleanup button click
  async function handleCleanUpClick() {
    try {
      setCleanupLoading(true);
      setCleanupMessage(null);
      setCleanupError(null);

      const res = await triggerCloudCleanup();

      const rgName =
        res?.result?.deleted_resource_group ??
        res?.result?.resource_group ??
        "resource group";

      setCleanupMessage(`Cleanup completed for: ${rgName}`);

      if (onCleanUpClick) {
        onCleanUpClick();
      }
    } catch (e: any) {
      console.error("Cleanup error", e);
      setCleanupError(
        e?.message || "Failed to clean up cloud resources. Please try again."
      );
    } finally {
      setCleanupLoading(false);
    }
  }  

    useEffect(() => {
    const url = new URL(window.location.href);
    const code = url.searchParams.get("code");
    const state = url.searchParams.get("state"); // "google" or "github"

    if (!code || !state) return;
    const safeCode = code;

    async function handleOAuthCallback() {
      try {
        setAuthMessage(null);
        setAuthError(null);

        if (state === "github") {
          const res = await fetch(
            `http://127.0.0.1:8000/auth/github/callback?code=${encodeURIComponent(
              safeCode
            )}`
          );
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data.detail || "GitHub login failed");
          }
          setAuthMessage(
            `GitHub login successful: ${data.name || data.login}`
          );
        } else if (state === "google") {
          const res = await fetch(
            `http://127.0.0.1:8000/auth/google/callback?code=${encodeURIComponent(
              safeCode
            )}`
          );
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data.detail || "Google login failed");
          }
          setAuthMessage(
            `Google login successful: ${data.name || data.email}`
          );
        }

        // remove code and state from URL
        url.searchParams.delete("code");
        url.searchParams.delete("state");
        window.history.replaceState({}, "", url.toString());
      } catch (e: any) {
        setAuthError(e?.message || "OAuth callback failed");
      }
    }

    void handleOAuthCallback();
  }, []);


  return (
    <div className="mt-8 space-y-6">
      {/* Security & Compliance */}
      <h2 className="text-xl font-bold mb-4 pl-5">Security &amp; Compliance</h2>
      <section className="bg-white rounded-lg shadow p-6">

        {secLoading && (
          <p className="text-sm text-gray-500">Loading security status...</p>
        )}

        {secError && (
          <p className="text-sm text-red-600">
            Failed to load security status: {secError}
          </p>
        )}

        {security && !secLoading && !secError && (
          <div className="space-y-1 text-sm">
            <div>
              <span style={{ fontWeight: "600", fontSize: "18px" }}>Security Status</span>
            </div>
            <div>
              Encryption:{" "}
              <span className="text-green-600 font-medium">
                {security.encryption}
              </span>
            </div>
            <div>
              Access Control:{" "}
              <span className="text-green-600 font-medium">
                {security.security_status}
              </span>
            </div>
            <div>
              Compliance:{" "}
              <span className="text-green-600 font-medium">
                {security.compliance}
              </span>
            </div>
          </div>
        )}
      </section>

      {/* OAuth & 2FA Integration */}
      <h2 className="text-xl font-bold mb-4 pl-5">OAuth &amp; 2FA Integration</h2>
      <section className="bg-white rounded-lg shadow p-6">

        <div className="space-y-3">
          <div className="text-sm font-medium mb-1">Secure Login</div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={startGoogleLogin}
              className="px-4 py-2 rounded bg-blue-600 text-white text-sm"
            >
              Login with Google
            </button>
            <button
              type="button"
              onClick={startGithubLogin}
              className="px-4 py-2 rounded bg-blue-600 text-white text-sm"
            >
              Login with GitHub
            </button>
          </div>

          {authMessage && (
            <p className="text-sm text-green-700 mt-1">{authMessage}</p>
          )}
          {authError && (
            <p className="text-sm text-red-600 mt-1">{authError}</p>
          )}

          <div className="mt-4 space-y-1 text-sm">
            <label className="block font-medium" htmlFor="twofa">
              Enter 2FA Code
            </label>
            <input
              id="twofa"
              type="text"
              placeholder="Enter your 2FA code"
              className="w-full border rounded px-3 py-2 text-sm"
            />
          </div>
        </div>
      </section>

      {/* Cloud Resource Cleanup */}
      <h2 className="text-xl font-bold mb-4 pl-5">Cloud Resource Cleanup</h2>
      <section className="bg-white rounded-lg shadow p-6">
        <p className="text-sm text-gray-600 mb-4">
          Ensure that cloud resources are efficiently managed and cleaned up
          post-deployment.
        </p>
        <button
          type="button"
          onClick={handleCleanUpClick}
          disabled={cleanupLoading}
          className="px-4 py-2 rounded bg-red-600 text-white text-sm disabled:opacity-60"
        >
          {cleanupLoading ? "Cleaning..." : "Clean Up Resources"}
        </button>

        {cleanupMessage && (
          <p className="mt-2 text-sm text-green-700">{cleanupMessage}</p>
        )}
        {cleanupError && (
          <p className="mt-2 text-sm text-red-600">{cleanupError}</p>
        )}
      </section>
    </div>
  );
}