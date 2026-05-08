"""调试模式：向指定 NDJSON 文件追加运行时证据。"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from uuid import uuid4

DEBUG_LOG_ENABLED = os.getenv("DEBUG_LOG_ENABLED", "0") == "1"
DEBUG_LOG_PATH = Path(os.getenv("DEBUG_LOG_PATH", "var/debug.ndjson"))
DEBUG_SESSION_ID = os.getenv("DEBUG_SESSION_ID", "default")


def debug_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    if not DEBUG_LOG_ENABLED:
        return

    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "id": f"log_{int(time.time() * 1000)}_{uuid4().hex[:8]}",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
    }
    DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
