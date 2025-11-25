import React, { useState } from "react";
import { triggerCloudCleanup } from "../lib/api";

type Props = {
  onCleanUpClick?: () => void;
};

export default function SecurityPanel({ onCleanUpClick }: Props) {
  const [cleanupLoading, setCleanupLoading] = useState(false);
  const [cleanupMessage, setCleanupMessage] = useState<string | null>(null);
  const [cleanupError, setCleanupError] = useState<string | null>(null);

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
      setCleanupError(
        e?.message || "Failed to clean up cloud resources. Please try again."
      );
    } finally {
      setCleanupLoading(false);
    }
  }

  return (
    <div className="mt-8 space-y-6">
      {/* Security & Compliance */}
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Security &amp; Compliance</h2>
        <div className="space-y-1 text-sm">
          <div>
            <span className="font-medium">Security Status</span>
          </div>
          <div>
            Encryption:{" "}
            <span className="text-green-600 font-medium">Enabled</span>
          </div>
          <div>
            Access Control:{" "}
            <span className="text-green-600 font-medium">Secure</span>
          </div>
          <div>
            Compliance:{" "}
            <span className="text-green-600 font-medium">GDPR Compliant</span>
          </div>
        </div>
      </section>

      {/* OAuth & 2FA Integration */}
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">OAuth &amp; 2FA Integration</h2>

        <div className="space-y-3">
          <div className="text-sm font-medium mb-1">Secure Login</div>
          <div className="flex flex-wrap gap-2">
            <button className="px-4 py-2 rounded bg-blue-600 text-white text-sm">
              Login with Google
            </button>
            <button className="px-4 py-2 rounded bg-blue-600 text-white text-sm">
              Login with GitHub
            </button>
          </div>

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
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-3">Cloud Resource Cleanup</h2>
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