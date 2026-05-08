"""权限常量与默认角色。"""

from __future__ import annotations


class Perm:
    ARTICLE_READ = "article:read"
    ARTICLE_WRITE = "article:write"
    ARTICLE_PUBLISH = "article:publish"
    ARTICLE_DELETE = "article:delete"

    ASSET_READ = "asset:read"
    ASSET_WRITE = "asset:write"
    ASSET_DELETE = "asset:delete"

    NOTE_READ = "note:read"
    NOTE_WRITE = "note:write"
    NOTE_DELETE = "note:delete"

    CATEGORY_WRITE = "category:write"
    TAG_WRITE = "tag:write"
    LINK_WRITE = "link:write"

    USER_READ = "user:read"
    USER_WRITE = "user:write"
    ROLE_WRITE = "role:write"

    SETTING_WRITE = "setting:write"

    AUDIT_READ = "audit:read"


ALL_PERMISSIONS: list[str] = [
    Perm.ARTICLE_READ,
    Perm.ARTICLE_WRITE,
    Perm.ARTICLE_PUBLISH,
    Perm.ARTICLE_DELETE,
    Perm.ASSET_READ,
    Perm.ASSET_WRITE,
    Perm.ASSET_DELETE,
    Perm.NOTE_READ,
    Perm.NOTE_WRITE,
    Perm.NOTE_DELETE,
    Perm.CATEGORY_WRITE,
    Perm.TAG_WRITE,
    Perm.LINK_WRITE,
    Perm.USER_READ,
    Perm.USER_WRITE,
    Perm.ROLE_WRITE,
    Perm.SETTING_WRITE,
    Perm.AUDIT_READ,
]


DEFAULT_ROLES: dict[str, list[str]] = {
    "admin": ALL_PERMISSIONS,
    "editor": [
        Perm.ARTICLE_READ,
        Perm.ARTICLE_WRITE,
        Perm.ARTICLE_PUBLISH,
        Perm.ASSET_READ,
        Perm.ASSET_WRITE,
        Perm.NOTE_READ,
        Perm.NOTE_WRITE,
        Perm.NOTE_DELETE,
        Perm.CATEGORY_WRITE,
        Perm.TAG_WRITE,
        Perm.LINK_WRITE,
    ],
    "author": [
        Perm.ARTICLE_READ,
        Perm.ARTICLE_WRITE,
        Perm.ASSET_READ,
        Perm.ASSET_WRITE,
        Perm.NOTE_READ,
        Perm.NOTE_WRITE,
    ],
    "viewer": [
        Perm.ARTICLE_READ,
        Perm.ASSET_READ,
        Perm.NOTE_READ,
    ],
}
