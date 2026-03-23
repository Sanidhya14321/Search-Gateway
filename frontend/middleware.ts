import { NextResponse, type NextRequest } from "next/server";
import { normalizeInternalRedirectPath } from "@/lib/auth/redirect";

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
  const pathname = request.nextUrl.pathname;
  const isProtected = PROTECTED_PATHS.some((path) => pathname.startsWith(path));
  const isAuthPage = ["/login", "/signup", "/forgot-password"].includes(pathname);
  const hasAuthToken = Boolean(request.cookies.get("crmind_access_token")?.value);

  if (isProtected && !hasAuthToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    const fullTarget = normalizeInternalRedirectPath(`${pathname}${request.nextUrl.search || ""}`);
    url.searchParams.set("redirect", fullTarget);
    return NextResponse.redirect(url);
  }

  if (isAuthPage && hasAuthToken) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next({ request });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api/).*)"],
};
