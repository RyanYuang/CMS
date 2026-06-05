"""演职员表 Excel 解析与上传。"""

from __future__ import annotations

from io import BytesIO

import pytest
from httpx import AsyncClient
from openpyxl import Workbook

from app.services.crew_sheet_parser import parse_crew_sheet_bytes


def _build_sample_xlsx() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["职位", "人员"])
    sheet.append(["导演", "王铃皓", "张三"])
    sheet.append(["摄影指导", "李四"])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_parse_crew_sheet_bytes_matches_sample_format() -> None:
    parsed = parse_crew_sheet_bytes(_build_sample_xlsx(), filename="crew.xlsx")
    assert len(parsed) == 2
    assert parsed[0]["role"]["CN"] == "导演"
    assert parsed[0]["role"]["EN"] == "Director"
    assert parsed[0]["names"] == ["王铃皓", "张三"]
    assert parsed[1]["role"]["CN"] == "摄影指导"
    assert parsed[1]["names"] == ["李四"]


@pytest.mark.asyncio
async def test_movies_parse_and_upload_crew_sheet(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/movies",
        json={"title": "演职员测试片", "work_category": "feature"},
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text
    movie_id = create.json()["id"]

    files = {"file": ("人员表示范.xlsx", _build_sample_xlsx(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    parsed = await client.post("/api/v1/movies/parse-crew-sheet", files=files, headers=auth_headers)
    assert parsed.status_code == 200, parsed.text
    body = parsed.json()
    assert body["row_count"] == 2
    assert body["crew_credits"][0]["role"]["CN"] == "导演"
    assert len(body["crew_credits"][0]["names"]) == 2

    uploaded = await client.post(f"/api/v1/movies/{movie_id}/crew-sheet", files=files, headers=auth_headers)
    assert uploaded.status_code == 200, uploaded.text
    movie = uploaded.json()
    assert len(movie["crew_credits"]) == 2

    public = await client.get("/api/v1/public/movies")
    assert public.status_code == 200
    row = next((item for item in public.json() if item["id"] == movie_id), None)
    assert row is not None
    assert len(row["crew_credits"]) == 2
    assert row["crew_credits"][1]["role"]["JP"]
