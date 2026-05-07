# Leowong CMS Backend (FastAPI)

> 对应 Linear `CMS` 项目里程碑「CMS 后端交付（MVP）」。覆盖文章/媒体/链接/审计/RBAC 全套接口，并提供 Public API 与 Leowongwebsite 联调。

## 技术栈

- **FastAPI 0.115** + **uvicorn**：异步 Web 框架
- **SQLAlchemy 2.0 (async)** + **Alembic**：ORM 与迁移
- **SQLite (aiosqlite)** 默认，**PostgreSQL (asyncpg)** 生产
- **JWT (python-jose) + bcrypt (passlib)**：鉴权
- **slowapi**：限流
- **Pillow**：图片元数据
- **pytest + httpx**：自动化测试

## 目录

```
CMS/Backend
├── app/
│   ├── main.py            # FastAPI 入口、CORS、限流、静态资源
│   ├── config.py          # pydantic-settings
│   ├── db.py              # 异步 engine / Session
│   ├── deps.py            # 当前用户 + RBAC 依赖
│   ├── permissions.py     # 权限码 + 默认角色
│   ├── security.py        # JWT / 密码哈希
│   ├── exceptions.py
│   ├── rate_limit.py
│   ├── seed.py            # 启动建表 + 种子数据
│   ├── models/            # ORM
│   ├── schemas/           # Pydantic 输入/输出
│   ├── services/          # 业务（article / asset / audit）
│   ├── utils/
│   └── api/v1/            # 路由（auth/users/roles/articles/...）
├── alembic/               # 迁移脚本
├── docs/
│   ├── DATA_MODEL.md      # RYA-5 内容模型与字段冻结
│   └── DEPLOY.md          # RYA-22 部署/备份/回滚
├── tests/                 # RYA-21 自动化测试
├── scripts/
│   ├── run_dev.sh
│   ├── migrate.sh
│   └── backup_db.sh
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## 快速开始

```bash
cd CMS/Backend
bash scripts/run_dev.sh     # 创建虚拟环境、安装依赖、生成 .env、启动
```

或者手动：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

启动后：

- 文档：http://localhost:8000/docs
- 健康：http://localhost:8000/health
- 默认管理员：`admin / admin123456`（请改 `.env`）

## 运行测试

```bash
pytest -q
```

## 与前端联调

- CMS 管理端（`CMS/Frontend`）已使用 `axios` 并将 `baseURL` 设为 `/api`。建议在 `vite.config.ts` 中配置代理：

```ts
// CMS/Frontend/vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
})
```

- Leowongwebsite（公网前台）使用 Public 接口：

```
GET /api/v1/public/articles?keyword=...&category_id=...&page=1&page_size=20
GET /api/v1/public/articles/{slug}
GET /api/v1/public/links
GET /api/v1/public/site
```

## Linear 任务覆盖矩阵

| Issue | 内容 | 实现位置 |
|---|---|---|
| RYA-5 | 内容模型与字段规范 | `docs/DATA_MODEL.md`、`app/models/*` |
| RYA-6 | DB 迁移 | `alembic/`、`app/seed.py`、`scripts/migrate.sh` |
| RYA-7 | E2E 验收清单 | `tests/`（CRUD + 发布 + 公开端联通） |
| RYA-8 | 鉴权 + RBAC | `app/security.py`、`app/deps.py`、`app/permissions.py`、`tests/test_auth.py` |
| RYA-9 | 草稿自动保存 / 预览 | `PUT /api/v1/articles/{id}/draft` |
| RYA-10 | 前后端联调 | `app/api/v1/public.py`、Vite 代理建议（README） |
| RYA-11 | 审计日志 | `app/services/audit.py`、`app/api/v1/audit.py` |
| RYA-12 | 文件上传 + 资源访问 | `app/api/v1/assets.py`、`app/services/asset.py`、`/static/uploads` |
| RYA-13 | 版本管理 / 回滚 | `ArticleVersion`、`POST /articles/{id}/rollback/{version}` |
| RYA-14 | 文章 CRUD + 状态流转 | `app/services/article.py`、`app/api/v1/articles.py` |
| RYA-15 | 孤儿文件清理 | `POST /api/v1/assets/cleanup-orphans` |
| RYA-16 | API 限流 | `slowapi`，登录 / 上传 / 默认三档 |
| RYA-20 | 列表分页 / 搜索 / 筛选 | 文章接口支持 keyword / status / category / tag / 时间范围 |
| RYA-21 | 自动化测试 | `tests/` 已覆盖 auth / article / asset / audit |
| RYA-22 | 部署运维手册 | `docs/DEPLOY.md`、`scripts/`、`Dockerfile`、`docker-compose.yml` |

## 主要 API 速览

### 鉴权
- `POST /api/v1/auth/login`
- `GET  /api/v1/auth/me`
- `POST /api/v1/auth/logout`

### 文章
- `GET    /api/v1/articles?keyword=&status=&category_id=&tag_id=&author_id=&date_from=&date_to=&page=&page_size=`
- `POST   /api/v1/articles`
- `GET    /api/v1/articles/{id}`
- `PATCH  /api/v1/articles/{id}`
- `PUT    /api/v1/articles/{id}/draft`        ← 自动保存
- `POST   /api/v1/articles/{id}/status`       ← 发布/下线/归档
- `GET    /api/v1/articles/{id}/versions`
- `POST   /api/v1/articles/{id}/rollback/{version}`
- `DELETE /api/v1/articles/{id}`

### 资源
- `GET    /api/v1/assets`
- `POST   /api/v1/assets/upload`              ← multipart/form-data
- `DELETE /api/v1/assets/{id}`
- `POST   /api/v1/assets/cleanup-orphans?dry_run=true`

### 用户 / 角色 / 权限
- `GET/POST/PATCH/DELETE /api/v1/users[/{id}]`
- `GET/POST/PATCH/DELETE /api/v1/roles[/{id}]`
- `GET    /api/v1/roles/permissions`

### 链接 / 设置 / 审计
- `GET/POST/PATCH/DELETE /api/v1/links[/{id}]` + `POST /api/v1/links/reorder`
- `GET/PUT /api/v1/settings`
- `GET    /api/v1/audit?target_type=&target_id=&actor_id=&action=`

### Public（匿名只读）
- `GET /api/v1/public/articles`
- `GET /api/v1/public/articles/{slug}`
- `GET /api/v1/public/links`
- `GET /api/v1/public/site`

## 安全注意

- 上线前务必替换 `SECRET_KEY` 为 32 字节随机串。
- 修改默认管理员密码，并通过 `/api/v1/users/{id}` 创建独立账号。
- 反向代理层应限制 `client_max_body_size`，并对 `/api/` 启用 TLS。
