"""用户管理接口。"""


from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import BizError, Conflict, NotFound
from app.models import AuditAction, Role, User
from app.permissions import Perm
from app.schemas import (
    OkResponse,
    UserCreate,
    UserList,
    UserOut,
    UserUpdate,
)
from app.schemas.common import PageMeta
from app.security import hash_password
from app.services import audit
from app.utils.pagination import PageParams, page_params


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserList, dependencies=[Depends(require_permissions(Perm.USER_READ))])
async def list_users(
    keyword: str | None = Query(None, max_length=64),
    is_active: bool | None = Query(None),
    role_id: int | None = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> UserList:
    stmt = select(User)
    cnt = select(func.count(User.id))
    conds = []
    if keyword:
        like = f"%{keyword}%"
        conds.append(or_(User.username.ilike(like), User.email.ilike(like), User.full_name.ilike(like)))
    if is_active is not None:
        conds.append(User.is_active.is_(is_active))
    if role_id is not None:
        conds.append(User.role_id == role_id)
    for c in conds:
        stmt = stmt.where(c)
        cnt = cnt.where(c)

    total = (await session.execute(cnt)).scalar_one()
    rows = (
        await session.execute(stmt.order_by(User.id.desc()).offset(pp.offset).limit(pp.page_size))
    ).scalars().unique().all()
    return UserList(
        items=[UserOut.model_validate(u) for u in rows],
        meta=PageMeta(
            page=pp.page,
            page_size=pp.page_size,
            total=int(total),
            total_pages=(int(total) + pp.page_size - 1) // pp.page_size,
        ),
    )


@router.post("", response_model=UserOut, dependencies=[Depends(require_permissions(Perm.USER_WRITE))])
async def create_user(
    request: Request,
    body: UserCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(current_user),
) -> UserOut:
    exists = (
        await session.execute(
            select(User).where((User.username == body.username) | (User.email == body.email))
        )
    ).scalar_one_or_none()
    if exists:
        raise Conflict("用户名或邮箱已被使用")

    if body.role_id is not None:
        role = await session.get(Role, body.role_id)
        if not role:
            raise BizError("角色不存在")

    user = User(
        username=body.username,
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role_id=body.role_id,
        is_active=body.is_active,
    )
    session.add(user)
    await session.flush()

    await audit.record(
        session,
        actor=actor,
        action=AuditAction.create,
        target_type="user",
        target_id=user.id,
        summary=f"创建用户 {user.username}",
        request=request,
    )
    return UserOut.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_permissions(Perm.USER_WRITE))],
)
async def update_user(
    user_id: int,
    request: Request,
    body: UserUpdate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(current_user),
) -> UserOut:
    user = await session.get(User, user_id)
    if not user:
        raise NotFound("用户不存在")

    diff: dict = {}
    if body.email and body.email != user.email:
        diff["email"] = {"from": user.email, "to": body.email}
        user.email = body.email
    if body.password:
        user.hashed_password = hash_password(body.password)
        diff["password"] = "changed"
    if body.full_name is not None:
        diff["full_name"] = {"from": user.full_name, "to": body.full_name}
        user.full_name = body.full_name
    if body.role_id is not None and body.role_id != user.role_id:
        role = await session.get(Role, body.role_id)
        if not role:
            raise BizError("角色不存在")
        diff["role_id"] = {"from": user.role_id, "to": body.role_id}
        user.role_id = body.role_id
    if body.is_active is not None and body.is_active != user.is_active:
        diff["is_active"] = {"from": user.is_active, "to": body.is_active}
        user.is_active = body.is_active
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url

    await session.flush()

    if diff:
        await audit.record(
            session,
            actor=actor,
            action=AuditAction.update,
            target_type="user",
            target_id=user.id,
            summary=f"更新用户 {user.username}",
            diff=diff,
            request=request,
        )
    return UserOut.model_validate(user)


@router.delete(
    "/{user_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.USER_WRITE))],
)
async def delete_user(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(current_user),
) -> OkResponse:
    user = await session.get(User, user_id)
    if not user:
        raise NotFound("用户不存在")
    if user.id == actor.id:
        raise BizError("不能删除自己")

    await session.delete(user)
    await audit.record(
        session,
        actor=actor,
        action=AuditAction.delete,
        target_type="user",
        target_id=user.id,
        summary=f"删除用户 {user.username}",
        request=request,
    )
    return OkResponse(message="deleted")
