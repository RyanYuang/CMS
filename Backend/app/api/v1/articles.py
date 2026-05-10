"""文章 CRUD、状态流转、版本管理（RYA-9/13/14/20）。"""


from datetime import datetime
from typing import Optional, Sequence

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import NotFound
from app.models import (
    Article,
    ArticleStatus,
    ArticleVersion,
    AuditAction,
    User,
)
from app.permissions import Perm
from app.schemas import (
    ArticleCreate,
    ArticleDetail,
    ArticleListItem,
    ArticleStatusUpdate,
    ArticleUpdate,
    ArticleVersionOut,
    OkResponse,
)
from app.schemas.common import Page
from app.services import article as article_service
from app.services import asset as asset_service
from app.services import audit
from app.utils.pagination import PageParams, build_page_meta, page_params


router = APIRouter(prefix="/articles", tags=["articles"])


def _used_asset_ids(article: Article) -> Sequence[int]:
    ids: list[int] = []
    if article.cover_asset_id:
        ids.append(article.cover_asset_id)
    return ids


@router.get(
    "",
    response_model=Page[ArticleListItem],
    dependencies=[Depends(require_permissions(Perm.ARTICLE_READ))],
)
async def list_articles(
    keyword: Optional[str] = Query(None, max_length=120),
    status: Optional[ArticleStatus] = Query(None),
    category_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[ArticleListItem]:
    rows, total = await article_service.list_articles(
        session,
        keyword=keyword,
        status=status,
        category_id=category_id,
        tag_id=tag_id,
        author_id=author_id,
        date_from=date_from,
        date_to=date_to,
        offset=pp.offset,
        limit=pp.page_size,
    )
    return Page[ArticleListItem](
        items=[ArticleListItem.model_validate(a) for a in rows],
        meta=build_page_meta(pp, total),
    )


@router.post(
    "",
    response_model=ArticleDetail,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_WRITE))],
)
async def create_article(
    request: Request,
    body: ArticleCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> ArticleDetail:
    article = await article_service.create_article(
        session,
        title=body.title,
        content=body.content,
        summary=body.summary,
        slug=body.slug,
        category_id=body.category_id,
        cover_asset_id=body.cover_asset_id,
        tag_ids=body.tag_ids,
        status=body.status,
        author=user,
    )
    await asset_service.mark_used(session, list(_used_asset_ids(article)))

    await audit.record(
        session,
        actor=user,
        action=AuditAction.create,
        target_type="article",
        target_id=article.id,
        summary=f"创建文章《{article.title}》",
        request=request,
    )
    return ArticleDetail.model_validate(article)


@router.get(
    "/{article_id}",
    response_model=ArticleDetail,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_READ))],
)
async def get_article(
    article_id: int,
    session: AsyncSession = Depends(get_session),
) -> ArticleDetail:
    article = await session.get(Article, article_id)
    if not article:
        raise NotFound("文章不存在")
    return ArticleDetail.model_validate(article)


@router.patch(
    "/{article_id}",
    response_model=ArticleDetail,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_WRITE))],
)
async def update_article(
    article_id: int,
    request: Request,
    body: ArticleUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> ArticleDetail:
    article = await session.get(Article, article_id)
    if not article:
        raise NotFound("文章不存在")

    article = await article_service.update_article(
        session,
        article=article,
        operator=user,
        title=body.title,
        slug=body.slug,
        summary=body.summary,
        content=body.content,
        category_id=body.category_id,
        cover_asset_id=body.cover_asset_id,
        tag_ids=body.tag_ids,
        note=body.note,
    )
    await asset_service.mark_used(session, list(_used_asset_ids(article)))

    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="article",
        target_id=article.id,
        summary=f"更新文章《{article.title}》",
        request=request,
    )
    return ArticleDetail.model_validate(article)


@router.put(
    "/{article_id}/draft",
    response_model=ArticleDetail,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_WRITE))],
)
async def autosave_draft(
    article_id: int,
    body: ArticleUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> ArticleDetail:
    """草稿自动保存（RYA-9）：不写审计、不强制变更版本号。"""
    article = await session.get(Article, article_id)
    if not article:
        raise NotFound("文章不存在")

    if body.title is not None:
        article.title = body.title
    if body.summary is not None:
        article.summary = body.summary
    if body.content is not None:
        article.content = body.content
    if body.category_id is not None:
        article.category_id = body.category_id
    if body.cover_asset_id is not None:
        article.cover_asset_id = body.cover_asset_id

    await session.flush()
    return ArticleDetail.model_validate(article)


@router.post(
    "/{article_id}/status",
    response_model=ArticleDetail,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_PUBLISH))],
)
async def change_status(
    article_id: int,
    request: Request,
    body: ArticleStatusUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> ArticleDetail:
    article = await session.get(Article, article_id)
    if not article:
        raise NotFound("文章不存在")

    target = body.status
    article = await article_service.transition_status(
        session, article=article, target=target, operator=user, note=body.note
    )

    if target is ArticleStatus.published:
        action = AuditAction.publish
        verb = "发布"
    elif target is ArticleStatus.draft:
        action = AuditAction.unpublish
        verb = "下线"
    elif target is ArticleStatus.archived:
        action = AuditAction.archive
        verb = "归档"
    else:
        action = AuditAction.update
        verb = "状态变更"

    await audit.record(
        session,
        actor=user,
        action=action,
        target_type="article",
        target_id=article.id,
        summary=f"{verb}文章《{article.title}》",
        request=request,
    )
    return ArticleDetail.model_validate(article)


@router.get(
    "/{article_id}/versions",
    response_model=list[ArticleVersionOut],
    dependencies=[Depends(require_permissions(Perm.ARTICLE_READ))],
)
async def list_versions(
    article_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[ArticleVersionOut]:
    res = await session.execute(
        select(ArticleVersion)
        .where(ArticleVersion.article_id == article_id)
        .order_by(ArticleVersion.version.desc())
    )
    return [ArticleVersionOut.model_validate(v) for v in res.scalars().all()]


@router.post(
    "/{article_id}/rollback/{version}",
    response_model=ArticleDetail,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_WRITE))],
)
async def rollback_version(
    article_id: int,
    version: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> ArticleDetail:
    article = await session.get(Article, article_id)
    if not article:
        raise NotFound("文章不存在")

    article = await article_service.rollback_to_version(
        session, article=article, version=version, operator=user
    )
    await audit.record(
        session,
        actor=user,
        action=AuditAction.rollback,
        target_type="article",
        target_id=article.id,
        summary=f"回滚到版本 {version}",
        request=request,
    )
    return ArticleDetail.model_validate(article)


@router.delete(
    "/{article_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.ARTICLE_DELETE))],
)
async def delete_article(
    article_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> OkResponse:
    article = await session.get(Article, article_id)
    if not article:
        raise NotFound("文章不存在")
    title = article.title
    await session.delete(article)
    await audit.record(
        session,
        actor=user,
        action=AuditAction.delete,
        target_type="article",
        target_id=article_id,
        summary=f"删除文章《{title}》",
        request=request,
    )
    return OkResponse(message="deleted")
