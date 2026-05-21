"""HtmlPack 规范

HtmlPack 是本项目最核心的中间格式：
上游可以来自语法 Excel、单词 Excel、汉字表、JSON 或 notebook；
下游统一交给图片生成、配音生成和 err.txt 校对流程处理。

为了兼容旧代码，HtmlPack 仍然可以被转换成包含 word/read/html 的 dict。
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class HtmlPack:
    """一张学习卡片图片和一段配音音频所需的最小数据。"""

    # 稳定编号，方便后续 manifest、人工校对和视频对齐。
    id: str

    # 实际送给 TTS 朗读的文本。旧代码中叫 word。
    speak: str

    # 人工读音标注。可为空；为空时只生成音频，不做读音差异校对。
    read: str | None

    # 交给 HtmlToPic 截图的 HTML 片段。
    html: str

    # 额外信息只用于追踪来源，不参与 TTS 和截图核心逻辑。
    meta: dict[str, Any] = field(default_factory=dict)

    def to_legacy_dict(self) -> dict[str, Any]:
        """转换成旧版 html_style.py 期望的 dict 结构。"""
        data = asdict(self)
        data["word"] = self.speak # 旧代码中叫 word
        return data


def ensure_htmlpack_dict(pack: HtmlPack | dict[str, Any]) -> dict[str, Any]:
    """把 HtmlPack 或旧版 dict 统一成可被现有流程消费的 dict。"""
    if isinstance(pack, HtmlPack):
        return pack.to_legacy_dict()
    return pack

