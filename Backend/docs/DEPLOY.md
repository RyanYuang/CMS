# 部署 / 备份 / 回滚 / 上线手册（RYA-22）

## 1. 本地启动

```bash
cd CMS/Backend
bash scripts/run_dev.sh        # 自动建虚拟环境、装依赖、生成 .env、启动
# 浏览器打开 http://localhost:8000/docs
```

默认管理员：`admin / admin123456`（可在 `.env` 修改）。

## 2. 数据库迁移

### 首次新增迁移
```bash
source .venv/bin/activate
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### 升级到最新
```bash
bash scripts/migrate.sh upgrade
```

### 回滚一步
```bash
bash scripts/migrate.sh downgrade -1
```

> 切换 PostgreSQL 时把 `.env` 中 `DATABASE_URL` 改成
> `postgresql+asyncpg://user:password@host:5432/db`，然后重新执行 `upgrade`。

## 3. 备份

```bash
bash scripts/backup_db.sh
# 输出到 var/backups/
```

建议生产环境的定时任务（Linux crontab，每天凌晨 02:00）：

```cron
0 2 * * * /opt/leowong-cms/scripts/backup_db.sh >> /var/log/cms_backup.log 2>&1
```

`var/uploads/` 整目录建议每周做对象存储/异地同步备份。

## 4. 容器化部署

```bash
docker compose up -d --build
docker compose logs -f api
```

容器健康检查：`/health`。Compose 中 `db` 服务健康检查通过后才会启动 `api`。

## 5. 发布流程

1. `git pull` 最新代码 / 拉镜像。
2. 备份数据库（`scripts/backup_db.sh`）。
3. `docker compose pull && docker compose up -d --build`（或 `systemctl restart leowong-cms`）。
4. 访问 `/health` 校验，浏览 `/docs`。
5. 在 CMS 管理端做一次「发布一篇文章 + 公开端访问」E2E 校验（RYA-7）。

## 6. 回滚（5 分钟内）

- 应用回滚：`docker compose down && docker compose up -d <上一个 image tag>`。
- 数据库回滚：`alembic downgrade -1`，或将 SQLite/SQL 备份覆盖 `var/leowong_cms.db`。
- 内容回滚：在 CMS 中通过 `POST /api/v1/articles/{id}/rollback/{version}` 恢复任一版本。

## 7. 故障排查

| 现象 | 排查 |
|---|---|
| `/health` 502 | `docker compose logs api`，检查数据库可达性 |
| 登录 401 | 确认 `.env` 中 `SECRET_KEY` 未被替换；密码使用默认值或自行重置 |
| 上传 413 / 400 | `MAX_UPLOAD_MB` 配额；Nginx `client_max_body_size` |
| CORS 报错 | `.env` 中追加来源到 `CORS_ORIGINS` |
| 速率限制 429 | 调整 `RATE_LIMIT_*` 或加白名单（可在反向代理层做） |

## 8. 反向代理建议

```nginx
server {
    listen 80;
    server_name api.leowong.example.com;

    client_max_body_size 30M;

    location /static/uploads/ {
        proxy_pass http://127.0.0.1:8000/static/uploads/;
    }
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:8000;
    }
}
```
