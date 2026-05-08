"""Pydantic schema 导出。"""

from app.schemas.common import OkResponse, Page, PageMeta
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.schemas.user import (
    RoleBrief,
    UserCreate,
    UserList,
    UserOut,
    UserUpdate,
)
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate, PermissionOut
from app.schemas.article import (
    ArticleCreate,
    ArticleDetail,
    ArticleListItem,
    ArticleStatusUpdate,
    ArticleUpdate,
    ArticleVersionOut,
)
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.tag import TagCreate, TagOut
from app.schemas.asset import AssetOut, AssetListItem
from app.schemas.audit import AuditLogOut
from app.schemas.link import LinkCreate, LinkOut, LinkReorder, LinkUpdate
from app.schemas.movie import MovieCount, MovieCreate, MovieOut, MovieUpdate
from app.schemas.music import (
    MusicTrackCount,
    MusicTrackCreate,
    MusicTrackOut,
    MusicTrackUpdate,
)
from app.schemas.note import NoteCount, NoteCreate, NoteOut, NoteUpdate
from app.schemas.setting import SettingItem

__all__ = [
    "OkResponse",
    "Page",
    "PageMeta",
    "LoginRequest",
    "LoginResponse",
    "MeResponse",
    "RoleBrief",
    "UserCreate",
    "UserList",
    "UserOut",
    "UserUpdate",
    "RoleCreate",
    "RoleOut",
    "RoleUpdate",
    "PermissionOut",
    "ArticleCreate",
    "ArticleDetail",
    "ArticleListItem",
    "ArticleStatusUpdate",
    "ArticleUpdate",
    "ArticleVersionOut",
    "CategoryCreate",
    "CategoryOut",
    "CategoryUpdate",
    "TagCreate",
    "TagOut",
    "AssetOut",
    "AssetListItem",
    "AuditLogOut",
    "LinkCreate",
    "LinkOut",
    "LinkReorder",
    "LinkUpdate",
    "MovieCount",
    "MovieCreate",
    "MovieOut",
    "MovieUpdate",
    "MusicTrackCount",
    "MusicTrackCreate",
    "MusicTrackOut",
    "MusicTrackUpdate",
    "NoteCount",
    "NoteCreate",
    "NoteOut",
    "NoteUpdate",
    "SettingItem",
]
