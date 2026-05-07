"""应用全局配置：从环境变量 / .env 文件加载，统一以 settings 对象访问。"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "dev"
    app_name: str = "Leowong CMS Backend"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 120
    algorithm: str = "HS256"

    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:4173",
            "http://127.0.0.1:5173",
        ]
    )

    database_url: str = "sqlite+aiosqlite:///./var/leowong_cms.db"

    upload_dir: str = "./var/uploads"
    max_upload_mb: int = 20
    public_base_url: str = "http://localhost:8000"

    rate_limit_default: str = "120/minute"
    rate_limit_login: str = "10/minute"
    rate_limit_upload: str = "30/minute"

    default_admin_username: str = "admin"
    default_admin_password: str = "admin123456"
    default_admin_email: str = "admin@leowong.example.com"

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_sqlite:
        db_file = settings.database_url.split("///", 1)[-1]
        Path(db_file).resolve().parent.mkdir(parents=True, exist_ok=True)
    os.makedirs(settings.upload_dir, exist_ok=True)
    return settings


settings = get_settings()
