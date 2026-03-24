"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { apiPost } from "@/lib/api/client";

export default function ProfilePage() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  useEffect(() => {
    if (!user) {
      router.replace("/login");
      return;
    }
    setLoading(false);
  }, [user, router]);

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword) {
      alert("Please fill both password fields.");
      return;
    }
    setUpdating(true);
    try {
      await apiPost("/api/v1/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setCurrentPassword("");
      setNewPassword("");
      alert("Password changed successfully");
    } catch (error: any) {
      alert(`Error: ${error?.message || String(error)}`);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-200"></div></main>;
  }

  return (
    <main className="max-w-2xl space-y-8">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-900">Profile</h1>
        <p className="mt-2 text-stone-600">Manage your account settings</p>
      </header>

      {/* Account Info */}
      <section className="rounded-lg border border-stone-200 bg-white/80 p-6 space-y-4">
        <h2 className="font-semibold text-stone-900">Account Information</h2>
        <div className="space-y-2">
          <p className="text-sm text-stone-600">Email</p>
          <p className="font-mono text-stone-900">{user?.email}</p>
        </div>
        <div className="space-y-2">
          <p className="text-sm text-stone-600">User ID</p>
          <p className="font-mono text-xs text-stone-500">{user?.id}</p>
        </div>
      </section>

      {/* Security */}
      <section className="rounded-lg border border-stone-200 bg-white/80 p-6 space-y-4">
        <h2 className="font-semibold text-stone-900">Security</h2>
        <input
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          placeholder="Current password"
          className="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
        />
        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder="New password"
          className="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
        />
        <button
          onClick={handleChangePassword}
          disabled={updating}
          className="rounded-lg border border-stone-300 px-4 py-2 text-sm text-stone-700 hover:border-stone-900"
        >
          {updating ? "Updating..." : "Change Password"}
        </button>
      </section>

      {/* Danger Zone */}
      <section className="rounded-lg border border-red-300 bg-red-50 p-6 space-y-4">
        <h2 className="font-semibold text-red-700">Danger Zone</h2>
        <button
          onClick={async () => {
            await signOut();
            router.push("/login");
          }}
          className="rounded-lg border border-red-300 px-4 py-2 text-sm text-red-700 hover:bg-red-100"
        >
          Sign Out
        </button>
      </section>
    </main>
  );
}
