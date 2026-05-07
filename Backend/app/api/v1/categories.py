"""分类接口。"""


from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import Conflict, NotFound
from app.models import Category
from app.permissions import Perm
from app.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    OkResponse,
)
from app.utils.slug import make_slug


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(current_user),
) -> list[CategoryOut]:
    res = await session.execute(select(Category).order_by(Category.sort_order, Category.id))
    return [CategoryOut.model_validate(c) for c in res.scalars().all()]


@router.post(
    "",
    response_model=CategoryOut,
    dependencies=[Depends(require_permissions(Perm.CATEGORY_WRITE))],
)
async def create_category(
    body: CategoryCreate,
    session: AsyncSession = Depends(get_session),
) -> CategoryOut:
    slug = body.slug or make_slug(body.name)
    exists = (await session.execute(select(Category).where(Category.slug == slug))).scalar_one_or_none()
    if exists:
        raise Conflict("slug 已存在")

    cat = Category(
        name=body.name,
        slug=slug,
        description=body.description,
        parent_id=body.parent_id,
        sort_order=body.sort_order,
    )
    session.add(cat)
    await session.flush()
    return CategoryOut.model_validate(cat)


@router.patch(
    "/{cat_id}",
    response_model=CategoryOut,
    dependencies=[Depends(require_permissions(Perm.CATEGORY_WRITE))],
)
async def update_category(
    cat_id: int,
    body: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
) -> CategoryOut:
    cat = await session.get(Category, cat_id)
    if not cat:
        raise NotFound("分类不存在")
    if body.name is not None:
        cat.name = body.name
    if body.slug is not None:
        cat.slug = body.slug
    if body.description is not None:
        cat.description = body.description
    if body.parent_id is not None:
        cat.parent_id = body.parent_id
    if body.sort_order is not None:
        cat.sort_order = body.sort_order
    await session.flush()
    return CategoryOut.model_validate(cat)


@router.delete(
    "/{cat_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.CATEGORY_WRITE))],
)
async def delete_category(
    cat_id: int,
    session: AsyncSession = Depends(get_session),
) -> OkResponse:
    cat = await session.get(Category, cat_id)
    if not cat:
        raise NotFound("分类不存在")
    await session.delete(cat)
    return OkResponse(message="deleted")
