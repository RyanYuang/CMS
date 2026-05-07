"""FastAPI 应用入口。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import IntegrityError

from app.api.v1.router import api_router
from app.config import settings
from app.exceptions import BizError
from app.rate_limit import limiter
from app.seed import init_db_and_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动 {} (env={})", settings.app_name, settings.app_env)
    await init_db_and_seed()
    yield
    logger.info("关闭 {}", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_dir = Path(settings.upload_dir).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    @app.exception_handler(BizError)
    async def _biz_handler(_: Request, exc: BizError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(IntegrityError)
    async def _integrity_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("数据库唯一约束冲突: {}", exc)
        return JSONResponse(
            status_code=409,
            content={"detail": {"code": "conflict", "message": "数据冲突，请检查唯一字段"}},
        )

    app.include_router(api_router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    @app.get("/", tags=["meta"])
    async def index() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "docs": "/docs",
            "openapi": "/openapi.json",
            "version": "0.1.0",
        }

    return app


app = create_app()
