#!/usr/bin/env bash
set -euo pipefail

# 备份脚本：根据 DATABASE_URL 选择 pg_dump 或 sqlite3 dump
cd "$(dirname "$0")/.."

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="var/backups"
mkdir -p "${BACKUP_DIR}"

if [[ -z "${DATABASE_URL:-}" ]]; then
    if [[ -f .env ]]; then
        export $(grep -E '^DATABASE_URL=' .env | head -n1)
    fi
fi

case "${DATABASE_URL:-}" in
    postgresql*|postgres*)
        OUT="${BACKUP_DIR}/pg_${DATE}.sql.gz"
        pg_dump "${DATABASE_URL/postgresql+asyncpg/postgresql}" | gzip > "${OUT}"
        echo "Postgres 备份已保存到 ${OUT}"
        ;;
    sqlite*)
        DB_FILE="${DATABASE_URL#sqlite+aiosqlite:///}"
        OUT="${BACKUP_DIR}/sqlite_${DATE}.sqlite"
        cp "${DB_FILE}" "${OUT}"
        echo "SQLite 备份已保存到 ${OUT}"
        ;;
    *)
        echo "未识别的 DATABASE_URL: ${DATABASE_URL:-<未设置>}"
        exit 1
        ;;
esac
