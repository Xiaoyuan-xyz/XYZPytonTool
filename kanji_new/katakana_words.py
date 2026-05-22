"""从 JLPT 单词 JSON 中提取 N3 片假名单词，并生成 HtmlPack。

数据来源仍然是现有词典 JSON；本文件只负责：
1. 读取 JSON。
2. 过滤 N3 片假名单词。
3. 每 5 个词组成一页。
4. 为每个词生成一个高亮页面 HtmlPack。

最终图片、音频、err.txt 仍交给 html_style.py 统一处理。
"""

import json
import re
from pathlib import Path
from typing import Any

from htmlpack import HtmlPack
from html_style import (
    extend_all_audio,
    htmlpack_process_pic,
    htmlpack_process_wav,
)
from template_renderer import render_template


# ===== 用户配置区 =====

JLPT_JSON_DIR = Path(__file__).parent.parent / "kanji_dict" / "dict" / "5mdld"
JLPT_JSON_PATTERN = "*JLPT*.json"
LEVEL_NUM = "N1"
WORDS_PER_PAGE = 5

# 和 grammer_all.py 一样，建议先只开图片，检查排版后再生成音频。
GENERATE_PICTURES = True
GENERATE_WAV = True
EXTEND_WAV = True

EXTEND_TARGET_DURATION_MS = 2000
EXTEND_IS_APPEND = False
EXTEND_SAFETY_MARGIN_MS = 5


STYLE = """
        body {
            background-color: black;
            font-family: "Georgia", "UD デジタル 教科書体 N", sans-serif;
            color: white;
            font-size: 38px;
            margin: 0;
            padding: 38px;
        }

        .content {
            width: 1120px;
            height: 640px;
            overflow: hidden;
        }

        .highlight {
            color: lightblue;
        }

        .source {
            font-size: 30px;
            opacity: 0.86;
        }

        .accent {
            color: #ffd479;
            font-size: 34px;
            margin-left: 0.35em;
        }

        .tag {
            color: #dddddd;
            font-family: "思源宋体 CN";
            font-size: 25px;
            margin-left: 0.45em;
        }

        .level {
            color: #aaaaaa;
            font-family: "思源宋体 CN";
            font-size: 21px;
            margin-left: 0.4em;
        }

        .zh {
            font-family: "思源宋体 CN";
            font-size: 25px;
        }

        p {
            text-indent: -2em;
            margin-left: 2em;
            margin-top: 0;
            margin-bottom: 6px;
        }
"""


def load_jlpt_words(json_dir=JLPT_JSON_DIR, pattern=JLPT_JSON_PATTERN):
    """读取 JLPT 单词 JSON。用 glob 避免中文文件名在命令行中被转码破坏。"""
    paths = sorted(Path(json_dir).glob(pattern))
    if not paths:
        raise FileNotFoundError(f"找不到 JLPT JSON: {Path(json_dir) / pattern}")

    with open(paths[0], "r", encoding="utf-8") as f:
        return json.load(f)


def parse_source(read: str) -> str:
    """
    从 read 字段提取词源。

    数据示例：
    - (英) advice -> advice
    - (法) enquete -> 法: enquete

    英语来源最常见，页面上只显示来源词；非英语来源额外保留语言标记。
    """
    read = str(read).strip()
    match = re.match(r"^\((.*?)\)\s*(.*)$", read)
    if not match:
        return read

    lang, source = match.groups()
    source = source.strip()
    if lang == "英":
        return source
    if source:
        return f"{lang}: {source}"
    return lang


def normalize_speak_text(row: dict[str, Any]) -> str:
    """清理送给 TTS 的文本，去掉波浪号和空格。"""
    return str(row.get("clean_word") or row.get("word") or "").replace("〜", "").replace(" ", "")


def normalize_read(row: dict[str, Any]) -> str | None:
    """清理人工读音标注；为空时返回 None。"""
    kana = str(row.get("kana") or "").replace("〜", "").strip()
    return kana or None


def is_target_katakana_word(row: dict[str, Any], level_num=LEVEL_NUM) -> bool:
    """当前数据中，纯片假名单词的 read 字段总是以 '(' 开头。"""
    return row.get("level_num") == level_num and str(row.get("read", "")).startswith("(")


def to_display_word(row: dict[str, Any]) -> dict[str, Any]:
    """把原始 JSON 行转换成模板直接使用的数据。"""
    return {
        "word": str(row.get("word", "")).replace(" ", ""),
        "source": parse_source(row.get("read", "")),
        "accent": row.get("accent") or "",
        "tag": row.get("tag_str") or "",
        "meaning": row.get("meaning") or "",
        "level": row.get("level") or "",
        "speak": normalize_speak_text(row),
        "read": normalize_read(row),
    }


def chunk_list(items, chunk_size):
    """按固定大小分页；最后一页不足 chunk_size 时照常保留。"""
    for start in range(0, len(items), chunk_size):
        yield items[start : start + chunk_size]


def build_htmlpacks(words):
    """每页显示 5 个词；每个词各生成一个高亮版本的 HtmlPack。"""
    display_words = [to_display_word(row) for row in words]
    htmlpacks = []

    for page_index, page_words in enumerate(chunk_list(display_words, WORDS_PER_PAGE)):
        for active_index, word in enumerate(page_words):
            html = render_template(
                "katakana_words.html",
                {
                    "words": page_words,
                    "active_index": active_index,
                },
            )
            htmlpacks.append(
                HtmlPack(
                    id=f"{len(htmlpacks):04d}",
                    speak=word["speak"],
                    read=word["read"],
                    html=html,
                    meta={
                        "source_type": "katakana_words",
                        "level_num": LEVEL_NUM,
                        "page_index": page_index,
                        "template": "katakana_words.html",
                        "meaning": word["meaning"],
                    },
                )
            )

    return htmlpacks


def load_target_words():
    """读取并筛选目标 N3 片假名单词。"""
    words = load_jlpt_words()
    return [row for row in words if is_target_katakana_word(row)]


def main():
    words = load_target_words()
    htmlpacks = build_htmlpacks(words)

    if GENERATE_PICTURES:
        htmlpack_process_pic(htmlpacks, style=STYLE)

    if GENERATE_WAV:
        htmlpack_process_wav(htmlpacks)

    if EXTEND_WAV:
        extend_all_audio(
            target_duration_ms=EXTEND_TARGET_DURATION_MS,
            is_append=EXTEND_IS_APPEND,
            safety_margin_ms=EXTEND_SAFETY_MARGIN_MS,
        )


if __name__ == "__main__":
    main()
