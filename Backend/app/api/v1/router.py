"""v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1 import (
    articles,
    assets,
    audit,
    auth,
    categories,
    links,
    notes,
    public,
    roles,
    settings as setting_route,
    tags,
    users,
)


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
api_router.include_router(articles.router)
api_router.include_router(assets.router)
api_router.include_router(audit.router)
api_router.include_router(links.router)
api_router.include_router(notes.router)
api_router.include_router(setting_route.router)
api_router.include_router(public.router)
