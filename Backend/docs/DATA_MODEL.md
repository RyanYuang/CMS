# CMS 数据模型 v1（对应 Linear RYA-5）

> 字段、约束、状态流转、权限边界。前后端联调以本文档为准。

## 状态流转（Article）

```
draft ──publish──▶ published
  ▲                      │
  └──── unpublish ◀──────┘
draft ──archive──▶ archived
published ──archive──▶ archived
archived ──restore──▶ draft
```

- `draft → published`：写权限 + 发布权限
- `published → draft`：等价于「下线」
- `*  → archived`：归档（停止对外显示，保留数据）
- `archived → draft`：恢复重新编辑

## 实体清单

### `users`

| 字段 | 类型 | 必填 | 默认 | 索引/约束 | 说明 |
|---|---|---|---|---|---|
| id | int (PK) | y | auto | PK | |
| username | varchar(64) | y | | unique, index | 登录名 |
| email | varchar(190) | y | | unique, index | 邮箱 |
| full_name | varchar(120) | n | null | | 显示名 |
| hashed_password | varchar(255) | y | | | bcrypt |
| is_active | bool | y | true | | 停用即不可登录 |
| last_login_at | datetime tz | n | null | | 登录成功更新 |
| avatar_url | varchar(500) | n | null | | |
| role_id | int FK roles.id | n | null | index, on delete set null | RBAC |
| created_at / updated_at | datetime tz | y | now() | | |

### `roles` / `permissions` / `role_permissions`

- `permissions.code` 全局唯一，例如 `article:write`
- `roles.is_builtin=true` 表示内置角色，不可删除（admin/editor/author/viewer）
- 授权关系通过 `role_permissions` 多对多

权限码：

```
article:read   article:write   article:publish   article:delete
asset:read     asset:write     asset:delete
category:write tag:write       link:write
user:read      user:write      role:write
setting:write
audit:read
```

### `articles`

| 字段 | 类型 | 必填 | 默认 | 索引 | 说明 |
|---|---|---|---|---|---|
| id | int PK | y | | | |
| title | varchar(255) | y | | index | |
| slug | varchar(255) | y | | unique, index | 自动生成或手动指定 |
| summary | varchar(500) | n | | | |
| content | text | y | "" | | Markdown / HTML |
| status | enum(draft/published/archived) | y | draft | index, 复合(status, published_at) | |
| published_at | datetime tz | n | null | | 首次 published 时写入 |
| cover_asset_id | FK assets.id | n | null | index | 封面 |
| category_id | FK categories.id | n | null | index | |
| author_id | FK users.id | n | null | index | |
| view_count | int | y | 0 | | 公开端递增 |
| current_version | int | y | 1 | | 每次实质变更 +1 |

约束：`UNIQUE(slug)`；复合索引 `(status, published_at)` 用于公开端查询。

### `article_versions`

每一次写操作（创建、字段变更、发布、回滚）都会生成快照。
唯一键 `(article_id, version)`；保留 `title/slug/summary/content/status/operator_id/note`。

### `categories` / `tags` / `article_tags`

- `categories.parent_id` 自引用（最多两级建议）
- `article_tags` 多对多

### `assets`

| 字段 | 类型 | 说明 |
|---|---|---|
| storage_key | varchar(500) unique | 相对 `UPLOAD_DIR` 的路径 `YYYY/MM/DD/xxx.png` |
| public_url | varchar(500) | 由 `PUBLIC_BASE_URL` + `/static/uploads/<storage_key>` 拼接 |
| kind | enum(image/video/audio/document/other) | 由 mime 自动归类 |
| mime_type, size_bytes, width, height, checksum | | sha256 校验 |
| is_orphan | bool | 默认 true，被引用后置 false；用于清理 |
| uploader_id | FK users.id |  |

### `audit_logs`

记录 `actor_id / actor_username / action / target_type / target_id / summary / diff(JSON) / request_ip`，建立 `(target_type, target_id)` 复合索引以便按文章追踪变更。

### `site_settings`

KV 表，`key` 唯一，`value` 为 JSON。例如：

```json
{ "key": "site.basic", "value": { "siteName": "我的个人网站", "siteDescription": "..." } }
{ "key": "social.links", "value": { "twitter": "...", "github": "..." } }
```

### `links`

链接管理页对应；字段：`title / url / cover / sort_order / status(online|offline)`。

## API 字段冻结（v1）

详见 OpenAPI（启动后访问 `/docs`）。**前后端评审通过后请勿无文档变更字段**。
