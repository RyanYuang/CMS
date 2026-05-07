"""角色与权限接口。"""


from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import BizError, Conflict, NotFound
from app.models import AuditAction, Permission, Role, User
from app.permissions import ALL_PERMISSIONS, Perm
from app.schemas import (
    OkResponse,
    PermissionOut,
    RoleCreate,
    RoleOut,
    RoleUpdate,
)
from app.services import audit


router = APIRouter(prefix="/roles", tags=["roles"])


async def _to_role_out(session: AsyncSession, role: Role) -> RoleOut:
    member_count = (
        await session.execute(select(func.count(User.id)).where(User.role_id == role.id))
    ).scalar_one()
    return RoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        is_builtin=role.is_builtin,
        permissions=[PermissionOut.model_validate(p) for p in role.permissions],
        member_count=int(member_count),
    )


async def _resolve_permissions(session: AsyncSession, codes: list[str]) -> list[Permission]:
    if not codes:
        return []
    res = await session.execute(select(Permission).where(Permission.code.in_(codes)))
    found = list(res.scalars().all())
    missing = set(codes) - {p.code for p in found}
    if missing:
        raise BizError(f"未知权限码: {', '.join(sorted(missing))}")
    return found


@router.get("/permissions", response_model=list[PermissionOut])
async def list_permissions(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(current_user),
) -> list[PermissionOut]:
    res = await session.execute(select(Permission).order_by(Permission.code))
    return [PermissionOut.model_validate(p) for p in res.scalars().all()]


@router.get("", response_model=list[RoleOut])
async def list_roles(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(current_user),
) -> list[RoleOut]:
    res = await session.execute(select(Role).order_by(Role.id))
    return [await _to_role_out(session, r) for r in res.scalars().all()]


@router.post(
    "",
    response_model=RoleOut,
    dependencies=[Depends(require_permissions(Perm.ROLE_WRITE))],
)
async def create_role(
    request: Request,
    body: RoleCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(current_user),
) -> RoleOut:
    exists = (await session.execute(select(Role).where(Role.name == body.name))).scalar_one_or_none()
    if exists:
        raise Conflict("角色名已存在")

    invalid = set(body.permission_codes) - set(ALL_PERMISSIONS)
    if invalid:
        raise BizError(f"未知权限: {', '.join(sorted(invalid))}")

    role = Role(name=body.name, description=body.description, is_builtin=False)
    role.permissions = await _resolve_permissions(session, body.permission_codes)
    session.add(role)
    await session.flush()

    await audit.record(
        session,
        actor=actor,
        action=AuditAction.create,
        target_type="role",
        target_id=role.id,
        summary=f"创建角色 {role.name}",
        request=request,
    )
    return await _to_role_out(session, role)


@router.patch(
    "/{role_id}",
    response_model=RoleOut,
    dependencies=[Depends(require_permissions(Perm.ROLE_WRITE))],
)
async def update_role(
    role_id: int,
    request: Request,
    body: RoleUpdate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(current_user),
) -> RoleOut:
    role = await session.get(Role, role_id)
    if not role:
        raise NotFound("角色不存在")

    if body.description is not None:
        role.description = body.description

    if body.permission_codes is not None:
        if role.is_builtin and role.name == "admin":
            raise BizError("内置 admin 角色不可修改权限")
        role.permissions = await _resolve_permissions(session, body.permission_codes)

    await session.flush()
    await audit.record(
        session,
        actor=actor,
        action=AuditAction.update,
        target_type="role",
        target_id=role.id,
        summary=f"更新角色 {role.name}",
        request=request,
    )
    return await _to_role_out(session, role)


@router.delete(
    "/{role_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.ROLE_WRITE))],
)
async def delete_role(
    role_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(current_user),
) -> OkResponse:
    role = await session.get(Role, role_id)
    if not role:
        raise NotFound("角色不存在")
    if role.is_builtin:
        raise BizError("内置角色不可删除")
    members = (await session.execute(select(func.count(User.id)).where(User.role_id == role.id))).scalar_one()
    if int(members) > 0:
        raise Conflict("仍有用户使用该角色，请先转移")

    await session.delete(role)
    await audit.record(
        session,
        actor=actor,
        action=AuditAction.delete,
        target_type="role",
        target_id=role.id,
        summary=f"删除角色 {role.name}",
        request=request,
    )
    return OkResponse(message="deleted")
