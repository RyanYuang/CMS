"""网易云歌单链接解析单元测试。"""

from __future__ import annotations

import pytest

from app.utils.netease import normalize_netease_playlist_link_field, parse_netease_playlist_id


@pytest.mark.parametrize(
    ("raw", "expected_id"),
    [
        ("https://music.163.com/playlist?id=9345473", "9345473"),
        ("https://music.163.com/#/playlist?id=9345473", "9345473"),
        ("https://y.music.163.com/m/playlist?id=9345473", "9345473"),
        ("https://music.163.com/playlist/9345473", "9345473"),
        ("playlist:9345473", "9345473"),
        ("netease-playlist:9345473", "9345473"),
    ],
)
def test_parse_netease_playlist_id_extracts(raw: str, expected_id: str) -> None:
    assert parse_netease_playlist_id(raw) == expected_id


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "https://music.163.com/song?id=1901371647",
        "https://music.163.com/album?id=86691261",
        "https://163cn.tv/xxxx",
    ],
)
def test_parse_netease_playlist_id_returns_none(raw: str) -> None:
    assert parse_netease_playlist_id(raw) is None


def test_normalize_rewrites_to_canonical_playlist_url() -> None:
    assert normalize_netease_playlist_link_field("https://music.163.com/#/playlist?id=9345473") == (
        '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=330 '
        'height=450 src="//music.163.com/outchain/player?type=0&id=9345473&auto=1&height=430"></iframe>'
    )


def test_normalize_rewrites_album_url_to_iframe() -> None:
    assert normalize_netease_playlist_link_field("https://music.163.com/album?id=373821573") == (
        '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=330 '
        'height=450 src="//music.163.com/outchain/player?type=1&id=373821573&auto=1&height=430"></iframe>'
    )


def test_normalize_preserves_iframe_outchain() -> None:
    raw = (
        '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=330 height=450 '
        'src="//music.163.com/outchain/player?type=0&id=9345473&auto=1&height=430"></iframe>'
    )
    assert normalize_netease_playlist_link_field(raw) == raw


def test_normalize_preserves_non_netease_urls() -> None:
    url = "https://example.com/audio.mp3"
    assert normalize_netease_playlist_link_field(url) == url


def test_normalize_empty_and_none() -> None:
    assert normalize_netease_playlist_link_field(None) is None
    assert normalize_netease_playlist_link_field("") is None
    assert normalize_netease_playlist_link_field("   ") is None
