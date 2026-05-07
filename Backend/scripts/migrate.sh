#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source .venv/bin/activate

case "${1:-upgrade}" in
    init)
        alembic revision --autogenerate -m "${2:-initial}"
        ;;
    new)
        alembic revision --autogenerate -m "${2:-update}"
        ;;
    upgrade)
        alembic upgrade head
        ;;
    downgrade)
        alembic downgrade "${2:-base}"
        ;;
    history)
        alembic history
        ;;
    *)
        echo "用法: $0 {init|new <message>|upgrade|downgrade <rev>|history}"
        exit 1
        ;;
esac
