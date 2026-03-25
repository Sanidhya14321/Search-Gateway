# CRMind Deployment Checklist

## 1. Backend Environment (Render)

- `DATABASE_URL` is set to Supabase PgBouncer URL (port `6543`).
- `DATABASE_URL_DIRECT` is set to direct Postgres URL (for Alembic migrations).
- `AUTH_JWT_SECRET` is present and stable across deploys.
- `API_KEY` and `INTERNAL_SERVICE_API_KEY` are set.
- `CORS_ALLOWED_ORIGINS` includes active frontend domains.
- `CORS_ALLOW_ORIGIN_REGEX` includes Vercel preview/production origins.
- `DB_POOL_MAX_SIZE=5` on free tier.
- `EMBEDDING_DIMENSIONS` matches model dimension (`384` in current config).
- `LOG_LEVEL` and `CACHE_TTL_SECONDS` are set as intended.

## 2. Frontend Environment (Vercel)

- `NEXT_PUBLIC_API_BASE_URL=https://crmind-api.onrender.com`.
- `NEXT_PUBLIC_USE_API_PROXY=true` (default) to avoid browser CORS issues.
- Production domain matches expected CORS allowlist.

## 3. Pre-Deploy Validation

- Backend compile sanity:
  - `python -m py_compile backend/main.py backend/middleware/auth.py backend/routers/auth.py`
- Frontend build:
  - `cd frontend && npm run build`
- Optional focused auth tests (requires local Postgres test DB):
  - `pytest tests/e2e/test_auth.py -q`

## 4. Post-Deploy Smoke Checks

- `GET /api/v1/health` returns `200`.
- Signup/login works and `/api/v1/auth/me` resolves user.
- `POST /api/v1/auth/api-keys` returns one-time `raw_key`.
- API key works via:
  - `X-API-Key: <key>`
  - `Authorization: Bearer <key>`
- Revoked key returns `401`.
- `/api/v1/agent/run` works from deployed frontend (no CORS error).

## 5. Rollback Signals

Rollback or pause deploy if any of these occur:

- `OPTIONS` preflight failures for `/api/v1/agent/run`.
- Repeated `401` with valid recently issued API keys.
- Startup migration failures (`migrations_failed` in logs).
- Persistent `500` from auth or agent endpoints.

## 6. Operational Notes

- Keep API keys short-lived for CI/integrations when possible.
- Rotate leaked or shared keys immediately.
- Never log raw API keys in backend or frontend telemetry.
