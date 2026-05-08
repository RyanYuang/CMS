"""调试模式：向指定 NDJSON 文件追加运行时证据。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

DEBUG_LOG_PATH = Path("/Users/ryanyuang/Documents/workspace/Leowong/.cursor/debug-308264.log")
DEBUG_SESSION_ID = "308264"


def debug_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
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
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
