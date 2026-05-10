"""网易云外链播放器字段规范化。

支持以下输入并统一为官方 iframe 代码：
- 网易云分享链接：playlist / album / song
- 标签写法：playlist:<id> / album:<id> / song:<id>
- 已有 outchain/player 链接或 iframe 代码（做最小规范化）
"""

from __future__ import annotations

from typing import Optional, Tuple

import re

_RESOURCE_QUERY = re.compile(r"(playlist|album|song)\?id=(\d+)", re.IGNORECASE)
_RESOURCE_PATH = re.compile(r"(?:^|[/#])(playlist|album|song)/(\d+)(?:[/\?#]|$)", re.IGNORECASE)
_TAG_FORM = re.compile(r"^(?:netease-)?(playlist|album|song):(\d+)$", re.IGNORECASE)
_OUTCHAIN_SRC = re.compile(
    r"https?://music\.163\.com/outchain/player\?[^\"'\s<>]+",
    re.IGNORECASE,
)
_IFRAME_OUTCHAIN = re.compile(
    r"<iframe\b[^>]*\bsrc=(['\"])(https?://music\.163\.com/outchain/player\?[^\"']+)\1[^>]*>\s*</iframe>",
    re.IGNORECASE | re.DOTALL,
)
_TYPE_MAP = {"playlist": 0, "album": 1, "song": 2}


def parse_netease_playlist_id(text: str) -> Optional[str]:
    """从任意字符串中提取网易云歌单数字 id；无法识别时返回 None。"""
    parsed = parse_netease_resource(text)
    if not parsed:
        return None
    resource, resource_id = parsed
    if resource != "playlist":
        return None
    return resource_id


def parse_netease_resource(text: str) -> Optional[Tuple[str, str]]:
    """从任意字符串中提取网易云资源类型与数字 id。"""
    s = text.strip()
    if not s:
        return None
    m = _RESOURCE_QUERY.search(s)
    if m:
        return m.group(1).lower(), m.group(2)
    m = _RESOURCE_PATH.search(s)
    if m:
        return m.group(1).lower(), m.group(2)
    m = _TAG_FORM.match(s)
    if m:
        return m.group(1).lower(), m.group(2)
    return None


def _build_iframe(src: str) -> str:
    normalized_src = re.sub(r"^https?://", "//", src, flags=re.IGNORECASE)
    return (
        '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" '
        f'width=330 height=450 src="{normalized_src}"></iframe>'
    )


def normalize_netease_playlist_link_field(value: Optional[str]) -> Optional[str]:
    """将网易云链接或 iframe 规范化为官方 outchain iframe 代码。"""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None

    iframe_match = _IFRAME_OUTCHAIN.search(stripped)
    if iframe_match:
        return _build_iframe(iframe_match.group(2))

    src_match = _OUTCHAIN_SRC.search(stripped)
    if src_match:
        return _build_iframe(src_match.group(0))

    parsed = parse_netease_resource(stripped)
    if parsed:
        resource, resource_id = parsed
        src = f"//music.163.com/outchain/player?type={_TYPE_MAP[resource]}&id={resource_id}&auto=1&height=430"
        return _build_iframe(src)

    return stripped
