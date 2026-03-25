---
name: api-keys
description: Implement and maintain CRMind user API key issuance, verification, revocation, and frontend management flows. Use when working on /auth/api-keys endpoints, middleware auth fallback, key rotation UX, or API key documentation.
---

# API Keys Skill (CRMind)

Use this skill when implementing API key lifecycle in CRMind backend or frontend.

## Goals

- Enable secure programmatic access for users without replacing JWT login.
- Support both auth styles:
  - `Authorization: Bearer <user_api_key>`
  - `X-API-Key: <user_api_key>`
- Ensure keys are never stored or logged in plaintext.
- Keep UX simple: create, copy-once, list, revoke.

## Backend Rules

1. Store only hashed keys in DB (`key_hash`), never raw keys.
2. Persist short searchable prefix (`key_prefix`) for lookup.
3. Verify key by prefix shortlist then hash verify.
4. Update `last_used_at` on successful auth.
5. Reject inactive or expired keys.
6. Accept API keys in Bearer auth path before JWT rejection.
7. Include trace-aware logs, never include full key in logs.

## Endpoint Contract

### `GET /api/v1/auth/api-keys`

- Auth required.
- Return active keys with metadata.

### `POST /api/v1/auth/api-keys`

- Auth required.
- Input: `{ name: string, expires_in_days?: number }`
- Response includes one-time `raw_key`.

### `DELETE /api/v1/auth/api-keys/{key_id}`

- Auth required.
- Soft revoke (`is_active=false`).

## Frontend Rules

1. Show one-time key clearly with copy button.
2. Warn user key cannot be viewed again.
3. Provide usage examples with `Authorization: Bearer`.
4. Encourage rotation and per-environment keys.
5. Support revoke action per key.

## Security Checklist

- Do not expose raw key in logs or telemetry.
- Use high-entropy random generation.
- Prefix format must be validated.
- Rate-limit create/revoke endpoints where possible.
- Keep DB queries parameterized.

## Testing Checklist

- Create key returns raw key once.
- Raw key authenticates via `X-API-Key`.
- Raw key authenticates via `Authorization: Bearer`.
- Revoked key no longer authenticates.
- Expired key no longer authenticates.
- Invalid prefix returns `401`.

## Files Commonly Updated

- `backend/middleware/auth.py`
- `backend/services/user_service.py`
- `backend/routers/auth.py`
- `frontend/app/(app)/settings/api-keys/page.tsx`
- `frontend/lib/api/client.ts`

## Notes

- JWT login remains default for browser sessions.
- API keys are for scripts, integrations, and server-to-server access.
