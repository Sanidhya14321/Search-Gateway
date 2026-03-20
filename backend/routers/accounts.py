from fastapi import APIRouter, Depends

from backend.agents.router import run_agent
from backend.middleware.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/account", tags=["accounts"])


@router.get("/{account_id}/brief")
async def account_brief(
    account_id: str,
    _: AuthenticatedUser = Depends(get_current_user),
):
    result = await run_agent("account_brief", f"Account brief for {account_id}", entity_id=account_id, entity_type="company")
    return {
        "account_id": account_id,
        "status": "completed" if not result.get("error") else "failed",
        "result": result.get("final_response"),
        "steps_log": result.get("steps_log", []),
        "citations": result.get("citations", []),
    }
