"""鉴权接口（RYA-8）。"""


from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.deps import current_user
from app.exceptions import Unauthorized
from app.models import AuditAction, User
from app.rate_limit import limiter
from app.schemas import LoginRequest, LoginResponse, MeResponse, OkResponse
from app.security import create_access_token, verify_password
from app.services import audit


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_login)
async def login(
    request: Request,
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    stmt = select(User).where((User.username == body.username) | (User.email == body.username))
    user = (await session.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise Unauthorized("用户名或密码错误")
    if not user.is_active:
        raise Unauthorized("账号已停用")

    user.last_login_at = datetime.now(tz=timezone.utc)
    token = create_access_token(user.id, extra={"username": user.username})

    await audit.record(
        session,
        actor=user,
        action=AuditAction.login,
        target_type="user",
        target_id=user.id,
        summary=f"{user.username} 登录",
        request=request,
    )

    return LoginResponse(
        access_token=token,
        expires_in_minutes=settings.access_token_expire_minutes,
    )


@router.post("/logout", response_model=OkResponse)
async def logout(
    request: Request,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> OkResponse:
    await audit.record(
        session,
        actor=user,
        action=AuditAction.logout,
        target_type="user",
        target_id=user.id,
        summary=f"{user.username} 登出",
        request=request,
    )
    return OkResponse(message="logged out")


@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(current_user)) -> MeResponse:
    perms = [p.code for p in user.role.permissions] if user.role else []
    return MeResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role.name if user.role else None,
        permissions=perms,
    )
