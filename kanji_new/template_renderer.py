"""Jinja2 模板渲染工具。

不同输入类型可以使用不同模板：
- 语法例句：templates/grammar_examples.html
- 单词列表：之后可以增加 templates/vocabulary_list.html
- 汉字详解：之后可以增加 templates/kanji_detail.html

这样 Python 只负责组织数据，HTML 结构交给模板文件管理。
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path(__file__).parent / "templates"


_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """用指定模板渲染 HTML 片段。"""
    template = _env.get_template(template_name)
    return template.render(**context)

