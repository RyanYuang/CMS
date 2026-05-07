"""Public API：供 Leowongwebsite 等前台站点匿名访问（RYA-10）。"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.exceptions import NotFound
from app.models import Article, ArticleStatus, LinkItem, LinkStatus, SiteSetting
from app.schemas import ArticleDetail, ArticleListItem, LinkOut
from app.schemas.common import Page
from app.services import article as article_service
from app.utils.pagination import PageParams, build_page_meta, page_params


router = APIRouter(prefix="/public", tags=["public"])


@router.get("/articles", response_model=Page[ArticleListItem])
async def public_articles(
    keyword: str | None = Query(None, max_length=120),
    category_id: int | None = Query(None),
    tag_id: int | None = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[ArticleListItem]:
    rows, total = await article_service.list_articles(
        session,
        keyword=keyword,
        status=ArticleStatus.published,
        category_id=category_id,
        tag_id=tag_id,
        author_id=None,
        date_from=None,
        date_to=None,
        offset=pp.offset,
        limit=pp.page_size,
        only_published=True,
    )
    return Page[ArticleListItem](
        items=[ArticleListItem.model_validate(a) for a in rows],
        meta=build_page_meta(pp, total),
    )


@router.get("/articles/{slug}", response_model=ArticleDetail)
async def public_article_detail(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> ArticleDetail:
    res = await session.execute(
        select(Article).where(Article.slug == slug, Article.status == ArticleStatus.published)
    )
    article = res.scalar_one_or_none()
    if not article:
        raise NotFound("文章不存在或未发布")
    article.view_count += 1
    await session.flush()
    fresh = (
        await session.execute(select(Article).where(Article.id == article.id))
    ).scalar_one()
    return ArticleDetail.model_validate(fresh)


@router.get("/links", response_model=list[LinkOut])
async def public_links(session: AsyncSession = Depends(get_session)) -> list[LinkOut]:
    res = await session.execute(
        select(LinkItem).where(LinkItem.status == LinkStatus.online).order_by(LinkItem.sort_order)
    )
    return [LinkOut.model_validate(i) for i in res.scalars().all()]


@router.get("/site")
async def public_site(session: AsyncSession = Depends(get_session)) -> dict:
    res = await session.execute(select(SiteSetting))
    return {s.key: s.value for s in res.scalars().all()}
