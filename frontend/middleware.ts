import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { hasSupabasePublicEnv, normalizeInternalRedirectPath } from "@/lib/supabase/env";

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

const PROTECTED_PATHS = [
  "/dashboard",
  "/search",
  "/entity",
  "/account",
  "/agent",
  "/signals",
  "/history",
  "/saved",
  "/enrich",
  "/profile",
  "/settings",
];

export async function middleware(request: NextRequest) {
  if (!hasSupabasePublicEnv()) {
    // Fail open so auth pages remain reachable while env is being configured.
    return NextResponse.next({ request });
  }

  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL as string,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet: CookieToSet[]) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const pathname = request.nextUrl.pathname;
  const isProtected = PROTECTED_PATHS.some((path) => pathname.startsWith(path));
  const isAuthPage = ["/login", "/signup", "/forgot-password"].includes(pathname);

  if (isProtected && !user) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    const fullTarget = normalizeInternalRedirectPath(`${pathname}${request.nextUrl.search || ""}`);
    url.searchParams.set("redirect", fullTarget);
    return NextResponse.redirect(url);
  }

  if (isAuthPage && user) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return supabaseResponse;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api/).*)"],
};
