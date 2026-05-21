# 读取 Excel 语法表，生成每一句例文对应的学习卡片图片和配音素材。
#
# 当前脚本仍然以 Excel 作为人工编辑入口：
# 1. load_grammars_from_excel() 只负责把 Excel 转成结构化数据。
# 2. build_htmlpacks() 只负责把结构化数据转成 HtmlPack。
# 3. main() 只负责按开关编排“生成图片 / 生成音频 / 补静音”流程。
#
# 这样后续要增加 Markdown/YAML/JSON 中间格式时，不需要改动渲染和配音部分。

import pandas as pd

from htmlpack import HtmlPack
from html_style import (
    extend_all_audio,
    htmlpack_process_pic,
    htmlpack_process_wav,
)
from template_renderer import render_template


# ===== 用户配置区 =====

INPUT_EXCEL_PATH = r"H:\Life\Project\markdown\语言\日本語\蓝宝书.xlsx"
SHEET_NAME = "new2"

# 第一轮建议先只生成图片；确认排版后再打开 GENERATE_WAV。
GENERATE_PICTURES = True
GENERATE_WAV = True
EXTEND_WAV = True

# 如果 EXTEND_WAV=True：
# - is_append=True 表示无论原音频多长，都追加一段静音。
# - is_append=False 表示只把短音频补到目标时长。
EXTEND_TARGET_DURATION_MS = 2000
EXTEND_IS_APPEND = True


COLUMN_CHAPTER = "章节"
COLUMN_POINT = "语法点"
COLUMN_ITEM = "小项"
COLUMN_SENTENCE = "例文"
COLUMN_TRANSLATION = "翻译"
COLUMN_NOTE = "解说"
COLUMN_READING = "读音"


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

        .zh {
            font-family: "思源宋体 CN";
            font-size: 25px;
        }

        p {
            text-indent: -2em;
            margin-left: 2em;
            margin-top: 0;
            margin-bottom: 3px;
        }
"""


def has_value(value):
    """判断 Excel 单元格是否有内容。pandas 会把空单元格读成 NaN。"""
    return str(value) != "nan"


def get_optional_cell(row, column_name, default=None):
    """读取可选列；列不存在或单元格为空时返回 default。"""
    if column_name not in row.index:
        return default
    value = row[column_name]
    if not has_value(value):
        return default
    return value


def load_grammars_from_excel(excel_path=INPUT_EXCEL_PATH, sheet_name=SHEET_NAME):
    """读取语法 Excel，并转成章节/语法点/小项/例文的层级结构。"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    grammars = []
    for i in range(len(df)):
        row = df.iloc[i]
        
        if has_value(row[COLUMN_CHAPTER]):
            grammars.append(
                {
                    "chapter": row[COLUMN_CHAPTER],
                    "content": [],
                }
            )

        if has_value(row[COLUMN_POINT]):
            grammars[-1]["content"].append(
                {
                    "point": row[COLUMN_POINT],
                    "content": [],
                }
            )

        if has_value(row[COLUMN_ITEM]):
            grammars[-1]["content"][-1]["content"].append(
                {
                    "item": row[COLUMN_ITEM],
                    "content": [],
                }
            )

        if has_value(row[COLUMN_SENTENCE]):
            grammars[-1]["content"][-1]["content"][-1]["content"].append(
                {
                    "sentence": row[COLUMN_SENTENCE].replace("/", ""),
                    "chinese": row[COLUMN_TRANSLATION],
                    "ps": row[COLUMN_NOTE],
                    "read": get_optional_cell(row, COLUMN_READING),
                }
            )

    return grammars


def build_htmlpacks(grammars):
    """
    把语法层级结构转成 HtmlPack 列表。

    每个 HtmlPack 对应一个画面和一段配音：
    {
        "word": "要配音的日语例句",
        "read": "假名读音标注；Excel 没有填写读音时为 None",
        "html": "用于截图的 HTML 片段",
    }
    """
    htmlpacks = []

    for chapter in grammars:
        for point in chapter["content"]:
            for item in point["content"]:
                if len(item["content"]) == 0:
                    continue

                examples = item["content"]
                note = examples[0]["ps"] if has_value(examples[0]["ps"]) else None

                for active_index, sentence in enumerate(examples):
                    html = render_template(
                        "grammar_examples.html",
                        {
                            "chapter": chapter["chapter"],
                            "point": point["point"],
                            "item": item["item"],
                            "note": note,
                            "examples": examples,
                            "active_index": active_index,
                        },
                    )

                    htmlpacks.append(
                        HtmlPack(
                            id=f"{len(htmlpacks):04d}",
                            speak=sentence["sentence"],
                            read=sentence["read"],
                            html=html,
                            meta={
                                "source_type": "grammar_examples",
                                "chapter": chapter["chapter"],
                                "point": point["point"],
                                "item": item["item"],
                                "template": "grammar_examples.html",
                            },
                        )
                    )

    return htmlpacks


def main():
    grammars = load_grammars_from_excel()
    htmlpacks = build_htmlpacks(grammars)

    if GENERATE_PICTURES:
        htmlpack_process_pic(htmlpacks, style=STYLE)

    if GENERATE_WAV:
        htmlpack_process_wav(htmlpacks)

    if EXTEND_WAV:
        extend_all_audio(
            target_duration_ms=EXTEND_TARGET_DURATION_MS,
            is_append=EXTEND_IS_APPEND,
        )


if __name__ == "__main__":
    main()
