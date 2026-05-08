"""首次启动初始化：建表 + 种子数据（默认管理员、权限、角色）。"""

from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models import Permission, Role, User
from app.permissions import ALL_PERMISSIONS, DEFAULT_ROLES
from app.security import hash_password
from app.utils.debug_ndjson import debug_log


async def _ensure_permissions(session: AsyncSession) -> dict[str, Permission]:
    res = await session.execute(select(Permission))
    existing = {p.code: p for p in res.scalars().all()}
    for code in ALL_PERMISSIONS:
        if code not in existing:
            perm = Permission(code=code)
            session.add(perm)
            existing[code] = perm
    await session.flush()
    return existing


async def _ensure_roles(session: AsyncSession, perms: dict[str, Permission]) -> dict[str, Role]:
    res = await session.execute(select(Role))
    existing = {r.name: r for r in res.scalars().all()}
    for name, codes in DEFAULT_ROLES.items():
        role = existing.get(name)
        if not role:
            role = Role(name=name, description=f"内置角色 {name}", is_builtin=True)
            session.add(role)
            existing[name] = role
        role.permissions = [perms[c] for c in codes]
    await session.flush()
    return existing


async def _ensure_admin(session: AsyncSession, roles: dict[str, Role]) -> None:
    admin = (
        await session.execute(
            select(User).where(User.username == settings.default_admin_username)
        )
    ).scalar_one_or_none()
    if admin:
        if admin.role_id is None:
            admin.role_id = roles["admin"].id
        return

    admin_user = User(
        username=settings.default_admin_username,
        email=settings.default_admin_email,
        full_name="Site Admin",
        hashed_password=hash_password(settings.default_admin_password),
        is_active=True,
        role_id=roles["admin"].id,
    )
    session.add(admin_user)
    await session.flush()


async def init_db_and_seed() -> None:
    async with engine.begin() as conn:
        # region agent log
        debug_log(
            run_id="pre-fix",
            hypothesis_id="H1",
            location="app/seed.py:init_db_and_seed",
            message="init strategy and db target",
            data={
                "database_url": settings.database_url,
                "init_strategy": "metadata.create_all",
            },
        )
        # endregion
        await conn.run_sync(Base.metadata.create_all)
        columns = (
            await conn.execute(text("PRAGMA table_info('movies')"))
        ).mappings().all()
        # region agent log
        debug_log(
            run_id="pre-fix",
            hypothesis_id="H2",
            location="app/seed.py:init_db_and_seed",
            message="movies table columns after create_all",
            data={"columns": [str(col.get("name")) for col in columns]},
        )
        # endregion
        column_names = {str(col.get("name")) for col in columns}
        if "stills" not in column_names:
            await conn.execute(
                text("ALTER TABLE movies ADD COLUMN stills JSON NOT NULL DEFAULT '[]'")
            )
            columns_after_fix = (
                await conn.execute(text("PRAGMA table_info('movies')"))
            ).mappings().all()
            # region agent log
            debug_log(
                run_id="post-fix",
                hypothesis_id="H2",
                location="app/seed.py:init_db_and_seed",
                message="patched legacy movies schema by adding stills",
                data={"columns": [str(col.get("name")) for col in columns_after_fix]},
            )
            # endregion

    async with SessionLocal() as session:
        try:
            version_rows = []
            try:
                version_rows = (
                    await session.execute(text("SELECT version_num FROM alembic_version"))
                ).scalars().all()
            except Exception as exc:  # pragma: no cover - debug instrumentation
                version_rows = [f"error:{exc.__class__.__name__}:{exc}"]
            # region agent log
            debug_log(
                run_id="pre-fix",
                hypothesis_id="H3",
                location="app/seed.py:init_db_and_seed",
                message="alembic version state",
                data={"alembic_versions": [str(v) for v in version_rows]},
            )
            # endregion
            perms = await _ensure_permissions(session)
            roles = await _ensure_roles(session, perms)
            await _ensure_admin(session, roles)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
