import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");

function buildTargetUrl(request: NextRequest, pathSegments: string[]) {
  const path = `/${pathSegments.join("/")}`;
  const target = new URL(`${BACKEND_BASE_URL}${path}`);
  request.nextUrl.searchParams.forEach((value, key) => {
    target.searchParams.set(key, value);
  });
  return target.toString();
}

async function proxyRequest(request: NextRequest, context: { params: { path: string[] } }) {
  const targetUrl = buildTargetUrl(request, context.params.path);

  const requestHeaders = new Headers(request.headers);
  requestHeaders.delete("host");
  requestHeaders.delete("content-length");

  const shouldSendBody = request.method !== "GET" && request.method !== "HEAD";
  const body = shouldSendBody ? await request.arrayBuffer() : undefined;

  const upstream = await fetch(targetUrl, {
    method: request.method,
    headers: requestHeaders,
    body,
    cache: "no-store",
  });

  const responseHeaders = new Headers();
  const contentType = upstream.headers.get("content-type");
  if (contentType) {
    responseHeaders.set("content-type", contentType);
  }
  const traceId = upstream.headers.get("x-trace-id");
  if (traceId) {
    responseHeaders.set("x-trace-id", traceId);
  }

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export async function GET(request: NextRequest, context: { params: { path: string[] } }) {
  return proxyRequest(request, context);
}

export async function POST(request: NextRequest, context: { params: { path: string[] } }) {
  return proxyRequest(request, context);
}

export async function PUT(request: NextRequest, context: { params: { path: string[] } }) {
  return proxyRequest(request, context);
}

export async function PATCH(request: NextRequest, context: { params: { path: string[] } }) {
  return proxyRequest(request, context);
}

export async function DELETE(request: NextRequest, context: { params: { path: string[] } }) {
  return proxyRequest(request, context);
}

export async function OPTIONS(request: NextRequest, context: { params: { path: string[] } }) {
  return proxyRequest(request, context);
}
