"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { buildApiUrl, clearAccessToken, setAccessToken } from "@/lib/api/client";

type AuthUser = {
  id: string;
  email: string;
  display_name?: string | null;
  plan?: string;
};

function setAuthCookie(token: string | null) {
  if (typeof document === "undefined") {
    return;
  }
  if (!token) {
    document.cookie = "crmind_access_token=; Path=/; Max-Age=0; SameSite=Lax";
    return;
  }
  document.cookie = `crmind_access_token=${encodeURIComponent(token)}; Path=/; Max-Age=${60 * 60 * 24 * 7}; SameSite=Lax`;
}

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadCurrentUser = async () => {
      try {
        const token = typeof window !== "undefined" ? window.localStorage.getItem("crmind_access_token") : null;
        if (!token) {
          if (mounted) {
            setUser(null);
            setLoading(false);
          }
          return;
        }

        setAuthCookie(token);

        const response = await fetch(buildApiUrl("/api/v1/auth/me"), {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          cache: "no-store",
        });

        if (!response.ok) {
          clearAccessToken();
          if (mounted) {
            setUser(null);
            setLoading(false);
          }
          return;
        }

        const me = await response.json();
        if (mounted) {
          setUser({
            id: me.id,
            email: me.email,
            display_name: me.display_name,
            plan: me.plan,
          });
          setLoading(false);
        }
      } catch {
        clearAccessToken();
        if (mounted) {
          setUser(null);
          setLoading(false);
        }
      }
    };

    void loadCurrentUser();

    return () => {
      mounted = false;
    };
  }, []);

  async function signIn(email: string, password: string) {
    const response = await fetch(buildApiUrl("/api/v1/auth/login"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data?.detail || "Sign in failed");
    }

    setAccessToken(data.access_token);
    setAuthCookie(data.access_token);
    setUser(data.user);
  }

  async function signUp(email: string, password: string) {
    const response = await fetch(buildApiUrl("/api/v1/auth/signup"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data?.detail || "Sign up failed");
    }

    setAccessToken(data.access_token);
    setAuthCookie(data.access_token);
    setUser(data.user);
  }

  async function signOut() {
    clearAccessToken();
    setAuthCookie(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
