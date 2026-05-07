"""测试夹具：使用独立 SQLite 文件库，启动前清理。"""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

os.environ.setdefault("APP_ENV", "test")

_TEMP_ROOT = Path(tempfile.mkdtemp(prefix="leowong_cms_test_"))
_DB_FILE = _TEMP_ROOT / "test.db"
_UPLOAD_DIR = _TEMP_ROOT / "uploads"
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_DB_FILE}"
os.environ["UPLOAD_DIR"] = str(_UPLOAD_DIR)
os.environ["SECRET_KEY"] = "test-secret-key-please-change"
os.environ["DEFAULT_ADMIN_USERNAME"] = "admin"
os.environ["DEFAULT_ADMIN_PASSWORD"] = "admin123456"
os.environ["DEFAULT_ADMIN_EMAIL"] = "admin@example.com"
os.environ["RATE_LIMIT_DEFAULT"] = "10000/minute"
os.environ["RATE_LIMIT_LOGIN"] = "10000/minute"
os.environ["RATE_LIMIT_UPLOAD"] = "10000/minute"

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()  # 让 settings 重新读取被覆盖的环境变量

from app.db import Base, engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.seed import init_db_and_seed  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_db() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db_and_seed()
    yield
    await engine.dispose()
    if _TEMP_ROOT.exists():
        shutil.rmtree(_TEMP_ROOT, ignore_errors=True)


@pytest_asyncio.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
async def admin_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123456"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
