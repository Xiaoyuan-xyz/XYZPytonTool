"""从 JLPT 单词 JSON 中提取拟声拟态语候选，并生成 HtmlPack。

这个词典没有直接的“拟声拟态语”标签，所以这里采用“形态规则 + 词性辅助”的方式
提取候选：

- 形态规则：ABAB、AっBり、AんBり、〜っと、〜りと、〜んと。
- 词性辅助：tag_str 中包含 副 / 形動 / 動自サ / 動他サ。
- 字形辅助：词条主体必须基本由假名组成，避免把普通汉字副词大量混进来。

这不是语言学上的绝对判定，而是给人工校对准备一批高质量候选。
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
JLPT_JSON_PATTERN = "*.json"
WORDS_PER_PAGE = 5

# None 表示提取全部等级；也可以改成 "N3"、"N2" 等。
LEVEL_NUM: str | None = None

# 建议先只开图片，检查候选和排版后再生成音频。
GENERATE_PICTURES = True
GENERATE_WAV = False
EXTEND_WAV = False

EXTEND_TARGET_DURATION_MS = 2000
EXTEND_IS_APPEND = False
EXTEND_SAFETY_MARGIN_MS = 50


STYLE = """
        body {
            background-color: black;
            font-family: "Georgia", "UD デジタル 教科書体 N", sans-serif;
            color: white;
            font-size: 44px;
            margin: 0;
            padding: 42px;
        }

        .content {
            width: 1120px;
            height: 640px;
            overflow: hidden;
        }

        .highlight {
            color: lightblue;
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

        .rule {
            color: #9ed7ff;
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
            margin-bottom: 12px;
        }
"""


KANA_RE = re.compile(r"^[ぁ-ゖァ-ヺーっッゃゅょャュョ]+$")


def load_jlpt_words(json_dir=JLPT_JSON_DIR, pattern=JLPT_JSON_PATTERN):
    """读取 JLPT 单词 JSON。用 glob 避免中文文件名在命令行中被转码破坏。"""
    paths = sorted(Path(json_dir).glob(pattern))
    if not paths:
        raise FileNotFoundError(f"找不到 JLPT JSON: {Path(json_dir) / pattern}")

    with open(paths[0], "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_word(row: dict[str, Any]) -> str:
    """清理词条主体，用于显示、匹配和 TTS。"""
    return (
        str(row.get("clean_word") or row.get("word") or row.get("kana") or "")
        .replace("〜", "")
        .replace("～", "")
        .replace(" ", "")
        .strip()
    )


def normalize_read(row: dict[str, Any]) -> str | None:
    """清理人工读音标注；为空时返回 None。"""
    kana = str(row.get("kana") or row.get("read") or "").replace("〜", "").replace("～", "").strip()
    return kana or None


def has_helper_part_of_speech(row: dict[str, Any]) -> bool:
    """用词性辅助减少误判；拟声拟态语常作副词，也常兼形动或サ变。"""
    tag = str(row.get("tag_str", ""))
    return any(part in tag for part in ["副", "形動", "動自サ", "動他サ"])


def detect_form_rules(word: str) -> list[str]:
    """识别常见拟声拟态语形态。返回命中的规则名，便于人工检查。"""
    rules = []
    core = word[:-1] if word.endswith("と") and len(word) > 2 else word

    if len(core) >= 4 and len(core) % 2 == 0:
        half = len(core) // 2
        if core[:half] == core[half:]:
            rules.append("ABAB")

    if re.match(r"^.+[っッ].+り$", core):
        rules.append("AっBり")

    if re.match(r"^.+ん.+り$", core):
        rules.append("AんBり")

    if re.match(r"^.+[っッ]と$", word):
        rules.append("〜っと")

    if re.match(r"^.+りと$", word):
        rules.append("〜りと")

    if re.match(r"^.+んと$", word):
        rules.append("〜んと")

    return rules


def is_giongo_candidate(row: dict[str, Any], level_num: str | None = LEVEL_NUM) -> bool:
    """判断是否是拟声拟态语候选。"""
    if level_num is not None and row.get("level_num") != level_num:
        return False

    word = normalize_word(row)
    if not word or not KANA_RE.match(word):
        return False

    return has_helper_part_of_speech(row) and len(detect_form_rules(word)) > 0


def to_display_word(row: dict[str, Any]) -> dict[str, Any]:
    """把原始 JSON 行转换成模板直接使用的数据。"""
    word = normalize_word(row)
    return {
        "word": word,
        "accent": row.get("accent") or "",
        "tag": row.get("tag_str") or "",
        "meaning": row.get("meaning") or "",
        "level": row.get("level") or "",
        "form_rules": " / ".join(detect_form_rules(word)),
        "speak": word,
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
                "giongo_words.html",
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
                        "source_type": "giongo_words",
                        "level_num": LEVEL_NUM,
                        "page_index": page_index,
                        "template": "giongo_words.html",
                        "meaning": word["meaning"],
                        "form_rules": word["form_rules"],
                    },
                )
            )

    return htmlpacks


def load_target_words():
    """读取并筛选拟声拟态语候选。"""
    words = load_jlpt_words()
    return [row for row in words if is_giongo_candidate(row)]


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
