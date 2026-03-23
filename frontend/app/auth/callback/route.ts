import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";
import { getSupabasePublicEnv, normalizeInternalRedirectPath } from "@/lib/supabase/env";

type CookieToSet = {
  name: string;
  value: string;
  options?: {
    domain?: string;
    path?: string;
    expires?: Date;
    httpOnly?: boolean;
    maxAge?: number;
    sameSite?: "lax" | "strict" | "none";
    secure?: boolean;
  };
};

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const redirect = normalizeInternalRedirectPath(searchParams.get("next"));

  const { url, anonKey } = getSupabasePublicEnv();

  if (code) {
    const cookieStore = cookies();
    const supabase = createServerClient(
      url,
      anonKey,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll();
          },
          setAll(cookiesToSet: CookieToSet[]) {
            cookiesToSet.forEach(({ name, value, options }) => {
              cookieStore.set(name, value, options);
            });
          },
        },
      },
    );

    const { error } = await supabase.auth.exchangeCodeForSession(code);
    
    // Return error page if code exchange fails
    if (error) {
      const errorUrl = new URL("/login", origin);
      errorUrl.searchParams.set("error", error.message);
      return NextResponse.redirect(errorUrl);
    }
  }

  // Redirect to the requested location or dashboard
  return NextResponse.redirect(`${origin}${redirect}`);
}
