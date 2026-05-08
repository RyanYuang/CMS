"""网易云歌单链接解析与入库规范化。

支持：
- 查询参数形态 ``playlist?id=<digits>``（含 ``#/playlist?id=`` 分享链接）
- 路径形态 ``.../playlist/<digits>``（PC / 移动端常见）
- 纯文本标签形态 ``playlist:<digits>`` / ``netease-playlist:<digits>``

不支持（需粘贴完整歌单页 URL）：163 短链等正文不含歌单 id 的链接。
"""

from __future__ import annotations

import re

_PLAYLIST_QUERY = re.compile(r"playlist\?id=(\d+)", re.IGNORECASE)
_PLAYLIST_PATH = re.compile(r"(?:^|[/#])playlist/(\d+)(?:[/\?#]|$)", re.IGNORECASE)
_TAG_FORM = re.compile(r"^(?:playlist:|netease-playlist:)(\d+)$", re.IGNORECASE)


def parse_netease_playlist_id(text: str) -> str | None:
    """从任意字符串中提取网易云歌单数字 id；无法识别时返回 None。"""
    s = text.strip()
    if not s:
        return None
    m = _PLAYLIST_QUERY.search(s)
    if m:
        return m.group(1)
    m = _PLAYLIST_PATH.search(s)
    if m:
        return m.group(1)
    m = _TAG_FORM.match(s)
    if m:
        return m.group(1)
    return None


def normalize_netease_playlist_link_field(value: str | None) -> str | None:
    """若可解析出歌单 id，则规范为官方歌单链接；否则返回去首尾空格后的原文。"""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    playlist_id = parse_netease_playlist_id(stripped)
    print(f"playlist_id: {playlist_id}")
    print(f"stripped: {stripped}")
    if playlist_id:
        return f"https://music.163.com/playlist?id={playlist_id}"
    return stripped
