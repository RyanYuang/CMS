"""公开构建信息接口。"""

from httpx import AsyncClient


async def test_public_build(client: AsyncClient) -> None:
    res = await client.get("/api/v1/public/build")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "build_time" in data
    assert "port" in data
    assert isinstance(data["version"], str)
    assert isinstance(data["build_time"], str)
    assert data["build_time"], "未配置 APP_BUILD_TIME 时应回退为进程启动时间"
    assert isinstance(data["port"], int)
