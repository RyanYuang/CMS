"""审计日志服务（RYA-11）。"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditAction, AuditLog, User


def _request_ip(request: Request | None) -> str | None:
    if not request:
        return None
    if request.client and request.client.host:
        return request.client.host
    return request.headers.get("x-forwarded-for") or request.headers.get("x-real-ip")


async def record(
    session: AsyncSession,
    *,
    actor: User | None,
    action: AuditAction,
    target_type: str,
    target_id: str | int | None = None,
    summary: str | None = None,
    diff: dict[str, Any] | None = None,
    request: Request | None = None,
) -> AuditLog:
    log = AuditLog(
        actor_id=actor.id if actor else None,
        actor_username=actor.username if actor else None,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        summary=summary,
        diff=diff,
        request_ip=_request_ip(request),
    )
    session.add(log)
    await session.flush()
    return log
