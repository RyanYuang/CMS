#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

if [[ ! -f .env ]]; then
    cp .env.example .env
    echo ".env 已生成，请按需修改后再次运行。"
fi

mkdir -p var/uploads

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 18000
