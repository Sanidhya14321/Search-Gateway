"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    async function loadUser() {
      const supabase = createBrowserSupabaseClient();
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      setLoading(false);
    }

    loadUser();
  }, []);

  const handleUpdateEmail = async (newEmail: string) => {
    setUpdating(true);
    const supabase = createBrowserSupabaseClient();
    const { error } = await supabase.auth.updateUser({ email: newEmail });
    setUpdating(false);

    if (error) {
      alert(`Error: ${error.message}`);
    } else {
      alert("Check your email to confirm the new address");
    }
  };

  const handleChangePassword = async () => {
    const supabase = createBrowserSupabaseClient();
    const { error } = await supabase.auth.resetPasswordForEmail(user?.email);

    if (error) {
      alert(`Error: ${error.message}`);
    } else {
      alert("Check your email for password reset instructions");
    }
  };

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-700"></div></main>;
  }

  return (
    <main className="max-w-2xl space-y-8">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-100">Profile</h1>
        <p className="mt-2 text-stone-400">Manage your account settings</p>
      </header>

      {/* Account Info */}
      <section className="rounded-lg border border-stone-700 bg-stone-900/50 p-6 space-y-4">
        <h2 className="font-semibold text-stone-100">Account Information</h2>
        <div className="space-y-2">
          <p className="text-sm text-stone-400">Email</p>
          <p className="font-mono text-stone-100">{user?.email}</p>
        </div>
        <div className="space-y-2">
          <p className="text-sm text-stone-400">User ID</p>
          <p className="font-mono text-xs text-stone-500">{user?.id}</p>
        </div>
      </section>

      {/* Security */}
      <section className="rounded-lg border border-stone-700 bg-stone-900/50 p-6 space-y-4">
        <h2 className="font-semibold text-stone-100">Security</h2>
        <button
          onClick={handleChangePassword}
          className="rounded-lg border border-stone-600 px-4 py-2 text-sm text-stone-300 hover:bg-stone-800"
        >
          Change Password
        </button>
      </section>

      {/* Danger Zone */}
      <section className="rounded-lg border border-red-700/50 bg-red-900/10 p-6 space-y-4">
        <h2 className="font-semibold text-red-300">Danger Zone</h2>
        <button
          onClick={async () => {
            const supabase = createBrowserSupabaseClient();
            await supabase.auth.signOut();
            router.push("/login");
          }}
          className="rounded-lg border border-red-600 px-4 py-2 text-sm text-red-300 hover:bg-red-900/20"
        >
          Sign Out
        </button>
      </section>
    </main>
  );
}
