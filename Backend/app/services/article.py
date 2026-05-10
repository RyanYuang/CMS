"""文章业务服务：CRUD、状态流转、版本快照（RYA-13/14/9）。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Iterable, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BizError, Conflict, NotFound
from app.models import (
    Article,
    ArticleStatus,
    ArticleVersion,
    Tag,
    User,
)
from app.utils.slug import make_slug, with_suffix


async def _reload(session: AsyncSession, article_id: int) -> Article:
    """重新查询文章以触发 lazy='selectin' 加载关联（异步上下文必须）。"""
    stmt = select(Article).where(Article.id == article_id)
    return (await session.execute(stmt)).scalar_one()


async def _ensure_unique_slug(
    session: AsyncSession,
    desired: str,
    *,
    exclude_id: Optional[int] = None,
) -> str:
    candidate = desired
    for _ in range(5):
        stmt = select(Article.id).where(Article.slug == candidate)
        if exclude_id is not None:
            stmt = stmt.where(Article.id != exclude_id)
        if (await session.execute(stmt)).scalar_one_or_none() is None:
            return candidate
        candidate = with_suffix(desired)
    raise Conflict("slug 冲突，请稍后重试")


async def _resolve_tags(session: AsyncSession, tag_ids: Iterable[int]) -> list[Tag]:
    ids = [tid for tid in tag_ids if tid]
    if not ids:
        return []
    res = await session.execute(select(Tag).where(Tag.id.in_(ids)))
    found = list(res.scalars().all())
    if len(found) != len(set(ids)):
        raise BizError("部分 tag 不存在")
    return found


async def _take_snapshot(
    session: AsyncSession,
    article: Article,
    *,
    operator: Optional[User],
    note: Optional[str],
) -> ArticleVersion:
    snap = ArticleVersion(
        article_id=article.id,
        version=article.current_version,
        title=article.title,
        slug=article.slug,
        summary=article.summary,
        content=article.content,
        status=article.status,
        operator_id=operator.id if operator else None,
        note=note,
    )
    session.add(snap)
    await session.flush()
    return snap


async def create_article(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    summary: Optional[str],
    slug: Optional[str],
    category_id: Optional[int],
    cover_asset_id: Optional[int],
    tag_ids: Sequence[int],
    status: ArticleStatus,
    author: User,
) -> Article:
    base_slug = slug or make_slug(title)
    final_slug = await _ensure_unique_slug(session, base_slug)

    article = Article(
        title=title,
        slug=final_slug,
        summary=summary,
        content=content or "",
        status=status,
        category_id=category_id,
        cover_asset_id=cover_asset_id,
        author_id=author.id,
        published_at=datetime.now(tz=timezone.utc) if status is ArticleStatus.published else None,
        current_version=1,
    )
    article.tags = await _resolve_tags(session, tag_ids)
    session.add(article)
    await session.flush()

    await _take_snapshot(session, article, operator=author, note="create")
    return await _reload(session, article.id)


async def update_article(
    session: AsyncSession,
    *,
    article: Article,
    operator: User,
    title: Optional[str] = None,
    slug: Optional[str] = None,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    category_id: Optional[int] = None,
    cover_asset_id: Optional[int] = None,
    tag_ids: Optional[Sequence[int]] = None,
    note: Optional[str] = None,
) -> Article:
    diff: dict[str, dict[str, object]] = {}

    def _track(field: str, old: object, new: object) -> None:
        if old != new:
            diff[field] = {"from": old, "to": new}

    if title is not None and title != article.title:
        _track("title", article.title, title)
        article.title = title

    if slug is not None and slug != article.slug:
        new_slug = await _ensure_unique_slug(session, slug, exclude_id=article.id)
        _track("slug", article.slug, new_slug)
        article.slug = new_slug

    if summary is not None and summary != article.summary:
        _track("summary", article.summary, summary)
        article.summary = summary

    if content is not None and content != article.content:
        _track("content_len", len(article.content or ""), len(content))
        article.content = content

    if category_id is not None and category_id != article.category_id:
        _track("category_id", article.category_id, category_id)
        article.category_id = category_id

    if cover_asset_id is not None and cover_asset_id != article.cover_asset_id:
        _track("cover_asset_id", article.cover_asset_id, cover_asset_id)
        article.cover_asset_id = cover_asset_id

    if tag_ids is not None:
        new_tags = await _resolve_tags(session, tag_ids)
        old_ids = sorted([t.id for t in article.tags])
        new_ids = sorted([t.id for t in new_tags])
        if old_ids != new_ids:
            _track("tag_ids", old_ids, new_ids)
            article.tags = new_tags

    if diff:
        article.current_version += 1
        await _take_snapshot(session, article, operator=operator, note=note or "update")

    await session.flush()
    return await _reload(session, article.id)


async def transition_status(
    session: AsyncSession,
    *,
    article: Article,
    target: ArticleStatus,
    operator: User,
    note: Optional[str] = None,
) -> Article:
    if article.status == target:
        return article

    valid_transitions = {
        ArticleStatus.draft: {ArticleStatus.published, ArticleStatus.archived},
        ArticleStatus.published: {ArticleStatus.draft, ArticleStatus.archived},
        ArticleStatus.archived: {ArticleStatus.draft},
    }
    if target not in valid_transitions[article.status]:
        raise BizError(f"非法状态流转: {article.status} -> {target}")

    article.status = target
    if target is ArticleStatus.published and not article.published_at:
        article.published_at = datetime.now(tz=timezone.utc)
    if target is ArticleStatus.archived:
        article.published_at = article.published_at  # 保留原发布时间

    article.current_version += 1
    await _take_snapshot(session, article, operator=operator, note=note or f"status:{target.value}")
    await session.flush()
    return await _reload(session, article.id)


async def rollback_to_version(
    session: AsyncSession,
    *,
    article: Article,
    version: int,
    operator: User,
) -> Article:
    stmt = select(ArticleVersion).where(
        ArticleVersion.article_id == article.id,
        ArticleVersion.version == version,
    )
    target = (await session.execute(stmt)).scalar_one_or_none()
    if not target:
        raise NotFound(f"版本 {version} 不存在")

    article.title = target.title
    article.slug = target.slug
    article.summary = target.summary
    article.content = target.content

    article.current_version += 1
    await _take_snapshot(session, article, operator=operator, note=f"rollback:{version}")
    await session.flush()
    return await _reload(session, article.id)


async def list_articles(
    session: AsyncSession,
    *,
    keyword: Optional[str],
    status: Optional[ArticleStatus],
    category_id: Optional[int],
    tag_id: Optional[int],
    author_id: Optional[int],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    offset: int,
    limit: int,
    only_published: bool = False,
) -> tuple[list[Article], int]:
    base = select(Article)
    count_base = select(func.count(Article.id))
    conds = []

    if keyword:
        like = f"%{keyword}%"
        conds.append(or_(Article.title.ilike(like), Article.summary.ilike(like)))
    if status:
        conds.append(Article.status == status)
    if only_published:
        conds.append(Article.status == ArticleStatus.published)
    if category_id:
        conds.append(Article.category_id == category_id)
    if tag_id:
        base = base.join(Article.tags).where(Tag.id == tag_id)
        count_base = count_base.join(Article.tags).where(Tag.id == tag_id)
    if author_id:
        conds.append(Article.author_id == author_id)
    if date_from:
        conds.append(Article.created_at >= date_from)
    if date_to:
        conds.append(Article.created_at <= date_to)

    for c in conds:
        base = base.where(c)
        count_base = count_base.where(c)

    total = (await session.execute(count_base)).scalar_one()
    rows = (
        await session.execute(
            base.order_by(Article.updated_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().unique().all()
    return list(rows), int(total)
