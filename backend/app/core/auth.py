import json
from typing import Any

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)
_FIREBASE_APP_NAME = "vn101-ai-office"


def _get_firebase_app() -> firebase_admin.App:
    settings = get_settings()
    if not settings.firebase_service_account_json.strip() or not settings.firebase_project_id.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase Authentication is not configured",
        )
    try:
        return firebase_admin.get_app(_FIREBASE_APP_NAME)
    except ValueError:
        try:
            service_account = json.loads(settings.firebase_service_account_json)
            credential = credentials.Certificate(service_account)
            return firebase_admin.initialize_app(
                credential,
                options={"projectId": settings.firebase_project_id},
                name=_FIREBASE_APP_NAME,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase Authentication is unavailable",
            ) from None


def verify_firebase_id_token(token: str) -> dict[str, Any]:
    try:
        decoded = auth.verify_id_token(token, app=_get_firebase_app(), check_revoked=True)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if not decoded.get("uid") or decoded.get("email_verified") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A verified email address is required",
        )
    return decoded


def get_current_user(
    credentials_header: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials_header is None or credentials_header.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_firebase_id_token(credentials_header.credentials)
