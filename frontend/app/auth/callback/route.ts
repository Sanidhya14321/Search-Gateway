import { NextResponse } from "next/server";
import { normalizeInternalRedirectPath } from "@/lib/auth/redirect";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const redirect = normalizeInternalRedirectPath(searchParams.get("next"));
  return NextResponse.redirect(`${origin}${redirect}`);
}
