"""统一业务异常。"""

from __future__ import annotations

from fastapi import HTTPException, status


class BizError(HTTPException):
    """业务异常基类，统一返回结构。"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "biz_error",
    ) -> None:
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class NotFound(BizError):
    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, code="not_found")


class Forbidden(BizError):
    def __init__(self, message: str = "无权限执行该操作") -> None:
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, code="forbidden")


class Unauthorized(BizError):
    def __init__(self, message: str = "未登录或登录已过期") -> None:
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, code="unauthorized")


class Conflict(BizError):
    def __init__(self, message: str = "数据冲突") -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, code="conflict")
