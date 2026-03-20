import pytest


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth(client):
    resp = await client.post(
        "/api/v1/agent/run",
        json={"workflow_name": "lead_finder", "query": "find engineers"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_returns_user(client_authed, seeded_user):
    resp = await client_authed.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_create_and_revoke_api_key(client_authed):
    resp = await client_authed.post("/api/v1/auth/api-keys", params={"name": "Test key"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["raw_key"].startswith("crm_")
    assert "warning" in data

    key_id = data["id"]

    resp = await client_authed.delete(f"/api/v1/auth/api-keys/{key_id}")
    assert resp.status_code == 200
    assert resp.json()["revoked"] is True


@pytest.mark.asyncio
async def test_search_history_recorded(
    client_authed,
    seeded_company,
    seeded_source_and_chunks,
    mock_llm,
    mock_embed,
):
    await client_authed.post(
        "/api/v1/agent/run",
        json={
            "workflow_name": "lead_finder",
            "query": "Find engineers at Test Inc",
        },
    )
    resp = await client_authed.get("/api/v1/user/history")
    assert resp.status_code == 200
    history = resp.json()
    assert history["total"] >= 1
    assert history["items"][0]["query"] == "Find engineers at Test Inc"


@pytest.mark.asyncio
async def test_save_and_remove_entity(client_authed, seeded_company):
    entity_id = str(seeded_company["id"])

    resp = await client_authed.post(
        "/api/v1/user/saved",
        json={
            "entity_id": entity_id,
            "entity_type": "company",
            "entity_name": "Test Inc",
            "tags": ["prospect"],
        },
    )
    assert resp.status_code == 200

    resp = await client_authed.get("/api/v1/user/saved")
    assert resp.status_code == 200
    assert any(str(item["entity_id"]) == entity_id for item in resp.json()["items"])

    resp = await client_authed.delete(f"/api/v1/user/saved/{entity_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_public_search_works_unauthenticated(client):
    resp = await client.post("/api/v1/search", json={"query": "Test Inc"})
    assert resp.status_code != 401
