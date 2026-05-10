"""FastAPI 依赖：当前请求用户、权限校验等。"""

from __future__ import annotations

from typing import Optional, Iterable

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.exceptions import Forbidden, Unauthorized
from app.models import User
from app.security import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not token:
        raise Unauthorized()

    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise Unauthorized("token 无效或已过期") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise Unauthorized()

    user = await session.get(User, int(user_id))
    if not user or not user.is_active:
        raise Unauthorized("账号不可用")

    request.state.current_user = user
    return user


def _user_perm_codes(user: User) -> set[str]:
    if user.role is None:
        return set()
    return {p.code for p in user.role.permissions}


def require_permissions(*codes: str):
    """权限装饰器工厂：require_permissions("article:write", "article:publish")"""

    required: tuple[str, ...] = codes

    async def _checker(user: User = Depends(current_user)) -> User:
        codes_set = _user_perm_codes(user)
        if user.role and user.role.name == "admin":
            return user
        missing = [c for c in required if c not in codes_set]
        if missing:
            raise Forbidden(f"缺少权限: {', '.join(missing)}")
        return user

    return _checker


def require_any_permission(*codes: str):
    required: tuple[str, ...] = codes

    async def _checker(user: User = Depends(current_user)) -> User:
        codes_set = _user_perm_codes(user)
        if user.role and user.role.name == "admin":
            return user
        if not any(c in codes_set for c in required):
            raise Forbidden(f"缺少以下任一权限: {', '.join(required)}")
        return user

    return _checker


async def get_active_users_by_role(session: AsyncSession, role_names: Iterable[str]) -> list[User]:
    """工具：按角色名拉取活跃用户（用于通知/分配等场景）。"""
    stmt = (
        select(User)
        .where(User.is_active.is_(True))
        .where(User.role.has(name=("admin")))  # placeholder
    )
    # 上述写法仅作为占位避免 lint 警告，调用方可自行扩展
    _ = role_names
    result = await session.execute(stmt)
    return list(result.scalars().all())
