# CMS

Leowong 内容管理：后台管理界面（Frontend）与对外 API / 管理接口（Backend）。本站前台 **Leowongwebsite** 可通过 Public API（如 `/api/v1/public/...`）读取 CMS 数据；详细联调见各子项目 README。

---

## 顶层目录架构

工作区路径：`CMS/`（本仓库根目录）。

```
CMS/
├── Frontend/          # CMS 后台前端（React + Vite + TS + Ant Design）
├── Backend/           # CMS 后端（FastAPI + SQLAlchemy + Alembic）
├── README.md          # 本文件：仓库总览与目录说明
└── .gitignore
```

不包含：`node_modules/`、Python `.venv/`、构建产物等（见 `.gitignore`）。

---

## Frontend（管理后台）

路径：`CMS/Frontend/`。

```
Frontend/
├── public/                 # 静态公共资源
├── src/
│   ├── assets/             # 图片等静态资源
│   ├── components/         # 复用组件
│   ├── constants/          # 常量
│   ├── hooks/              # React Hooks
│   ├── layouts/            # 后台壳层布局
│   ├── mocks/              # 演示 / Mock 数据
│   ├── pages/              # 业务页面（auth、dashboard、media、users 等）
│   ├── router/             # 路由配置
│   ├── services/           # API 封装
│   ├── styles/             # 全局与主题样式
│   └── utils/              # 工具函数
├── index.html
├── vite.config.ts
├── package.json
└── README.md               # 启动、构建、联调端口说明
```

启动与构建见 `Frontend/README.md`。

---

## Backend（API 服务）

路径：`CMS/Backend/`。

```
Backend/
├── app/
│   ├── main.py             # FastAPI 入口（CORS、限流、静态资源等）
│   ├── config.py           # 配置（pydantic-settings）
│   ├── db.py               # 异步数据库会话
│   ├── deps.py             # 依赖注入（当前用户、RBAC）
│   ├── security.py         # JWT / 密码
│   ├── permissions.py      # 权限与角色
│   ├── rate_limit.py       # 限流
│   ├── seed.py             # 建表与种子数据
│   ├── models/             # ORM 模型
│   ├── schemas/            # Pydantic 模式
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具（分页、slug 等）
│   └── api/v1/             # HTTP 路由（含 Public 与管理端）
├── alembic/                # 数据库迁移
├── alembic.ini
├── docs/                   # 数据模型、部署等文档
├── scripts/                # run_dev、migrate、backup 等脚本
├── tests/                  # pytest
├── Dockerfile
├── docker-compose.yml
├── docker-compose.1panel.yml
├── requirements.txt
├── pyproject.toml
└── README.md               # 环境、命令、与前端联调说明
```

API 约定、部署与数据模型见 `Backend/README.md` 与 `Backend/docs/`。

---

## 与子项目文档的关系

| 需求           | 查阅 |
|----------------|------|
| 后台页面与路由 | `Frontend/README.md` |
| 后端接口与部署 | `Backend/README.md`、`Backend/docs/DEPLOY.md` |
| 内容模型       | `Backend/docs/DATA_MODEL.md` |
