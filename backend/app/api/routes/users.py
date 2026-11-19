from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_mongo_database

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_my_profile(
    request: Request,
    identity: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    client = getattr(request.app.state, "mongo_client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="MongoDB is not configured")

    settings = get_settings()
    users = get_mongo_database(client)["users"]
    uid = identity["uid"]
    now = datetime.now(timezone.utc)
    update_fields: dict[str, Any] = {
        "firebase_uid": uid,
        "email": identity.get("email"),
        "display_name": identity.get("name"),
        "photo_url": identity.get("picture"),
        "email_verified": True,
        "updated_at": now,
    }
    insert_fields: dict[str, Any] = {"created_at": now}
    if settings.owner_firebase_uid and uid == settings.owner_firebase_uid:
        update_fields["role"] = "owner"
    else:
        insert_fields["role"] = "user"

    try:
        await users.update_one(
            {"firebase_uid": uid},
            {"$set": update_fields, "$setOnInsert": insert_fields},
            upsert=True,
        )
        saved = await users.find_one(
            {"firebase_uid": uid},
            {"_id": 0, "firebase_uid": 1, "email": 1, "display_name": 1,
             "photo_url": 1, "email_verified": 1, "role": 1},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User profile storage is unavailable",
        ) from None

    if saved is None:
        raise HTTPException(status_code=503, detail="User profile could not be loaded")
    return saved
