# 日语学习素材生成工具

这个项目用于把人工整理的日语学习内容生成成一组视频素材：

- 每句例文对应一张学习卡片图片。
- 每句例文对应一段配音音频。
- 程序会生成 `err.txt`，供人工校对 VOICEVOX 的读音。
- 校对和视频对齐目前仍由用户手动完成，之后再逐步考虑自动化。

当前阶段的重点不是“一键生成最终视频”，而是稳定地产出便于人工检查和剪辑的图片、音频、读音校对文件。

## 目录约定

推荐目录结构：

```text
kanji_new/
  in/          人工编辑的输入文件，例如 Excel
  out/         程序输出结果
    png/       学习卡片图片
    wav_raw/   VOICEVOX 直接生成的原始音频
    wav/       补静音后的音频
    err.txt    需要人工检查的读音列表
  assets/      通用资源，例如字典、字体或模板
```

当前代码里还有一些历史硬编码路径，后续会逐步迁移到配置文件中。

## 当前功能

### `grammer_all.py`

主流程脚本。

负责：

- 读取 Excel。
- 转成内部的语法层级结构。
- 生成 `HtmlPack`。
- 调用 Jinja2 模板生成 HTML。
- 调用图片生成流程。
- 调用配音生成流程。
- 调用音频补静音流程。

脚本顶部有用户配置区：

```python
INPUT_EXCEL_PATH = r"H:\Life\Project\markdown\语言\日本語\蓝宝书.xlsx"
SHEET_NAME = "new2"

GENERATE_PICTURES = True
GENERATE_WAV = False
EXTEND_WAV = False
EXTEND_SAFETY_MARGIN_MS = 10
```

建议工作方式：

1. 先保持 `GENERATE_PICTURES = True`，只生成图片并检查排版。
2. 图片无误后，把 `GENERATE_WAV = True`，生成音频和 `err.txt`。
3. 校对 `err.txt` 后，再运行修正读音相关流程。
4. 最后根据需要把 `EXTEND_WAV = True`，生成补静音后的音频。

补静音时默认会额外保留 `EXTEND_SAFETY_MARGIN_MS = 10` 毫秒安全余量。这样导入 PR 或其他视频时间线时，即使发生采样点取整或帧显示误差，也不会把目标 `2000ms` 的音频显示成约 `1970ms`。

### `html_to_pic.py`

用 Selenium 和 Chrome 把 HTML 渲染成 PNG。

核心类：

```python
HtmlToPic
```

### `html_style.py`

提供批处理函数，把 `HtmlPack` 落地成图片、音频和校对文件。

主要函数：

- `htmlpack_process_pic()`：生成图片。
- `htmlpack_process_wav()`：生成原始音频，并记录可能的读音错误。
- `replace_err()`：读取人工校对后的 `err.txt`，重新生成指定音频。
- `extend_all_audio()`：给音频补静音。

### `htmlpack.py`

正式定义 `HtmlPack` 规范。

`HtmlPack` 是当前流程里最核心的中间格式。不同来源的输入最终都应该转换成它：

```text
Excel / JSON / Notebook 数据
  -> HtmlPack
  -> 图片 / 音频 / err.txt
```

当前字段：

```python
{
    "id": "0001",
    "speak": "要送去 TTS 朗读的文本",
    "read": "人工读音标注，可以为 None",
    "html": "用于生成图片的 HTML 片段",
    "meta": {
        "source_type": "grammar_examples",
        "template": "grammar_examples.html"
    }
}
```

为了兼容旧代码，`HtmlPack` 可以转换成旧版 dict：

```python
{
    "word": "要送去 TTS 朗读的文本",
    "read": "人工读音标注，可以为 None",
    "html": "用于生成图片的 HTML 片段",
}
```

### `template_renderer.py`

封装 Jinja2 模板渲染。

Python 负责整理数据，HTML 结构交给模板文件维护。这样不同类型的内容可以使用不同模板：

```text
templates/
  grammar_examples.html   语法例句页面
  katakana_words.html     N3 片假名单词页面
  vocabulary_list.html    之后可增加：单词列表页面
  kanji_detail.html       之后可增加：汉字详解页面
```

当前已迁移：

```text
templates/grammar_examples.html
templates/katakana_words.html
```

### `katakana_words.py`

从 JLPT 单词 JSON 中提取 N3 片假名单词，并生成 HtmlPack。

默认数据源：

```text
../kanji_dict/dict/5mdld/全部JLPT单词.json
```

筛选规则：

```python
level_num == "N3"
read.startswith("(")
```

当前数据中，纯片假名单词的 `read` 字段总是以 `(` 开头，例如：

```text
(英) advice
(法) enquete
```

页面规则：

- 每页显示 5 个单词。
- 最后一页不足 5 个时照常显示。
- 每个单词生成一个高亮版本的 HtmlPack。
- 每个词显示：单词、来源、声调、词性、等级、中文翻译。
- 英语来源只显示来源词，例如 `advice`。
- 非英语来源显示语言标记，例如 `法: enquete`。

对应模板：

```text
templates/katakana_words.html
```

### `voicevox.py`

封装 VOICEVOX 和 GPT-SoVITS 相关调用。

VOICEVOX 默认地址：

```text
http://127.0.0.1:50021
```

当前默认 speaker：

```python
speaker = 61
```

## Excel 格式

Excel 对人工编辑非常友好，因此当前把 Excel 作为主要输入格式。

`grammer_all.py` 默认读取 `new2` 工作表，需要这些列：

```text
章节
语法点
小项
例文
翻译
解说
```

可选列：

```text
读音
```

表格采用“层级式填写”：

- `章节` 非空：创建新章节。
- `语法点` 非空：在当前章节下创建新语法点。
- `小项` 非空：在当前语法点下创建新小项。
- `例文` 非空：加入当前小项的例句列表。
- `翻译`：当前例文的中文翻译。
- `解说`：当前小项说明，目前主要读取该小项第一条例文的解说。
- `读音`：可选。填写假名读音后，程序会用它和 VOICEVOX 推断读音做初步比较，并把可疑项写入 `err.txt`。

示例：

```text
章节    语法点     小项       例文                           翻译                  解说                  读音
第1章   ～て       同时进行   書を見て漢字を覚えます。       看着书背汉字。        表示两个动作同时进行  しょをみてかんじをおぼえます
                              音楽を聞いて勉強します。       听着音乐学习。                              おんがくをきいてべんきょうします
        ～ながら   同时进行   ご飯を食べながらテレビを見る。 一边吃饭一边看电视。  接续动词ます形        ごはんをたべながらテレビをみる
第2章   ～ために   目的       日本へ行くために勉強します。   为了去日本而学习。    表示目的              にほんへいくためにべんきょうします
```

后续可以增加一步：

```text
Excel -> JSON/YAML 中间文件 -> 图片/音频生成
```

这样可以同时保留 Excel 的可编辑性，以及程序处理时的稳定结构。

## `err.txt` 校对流程

生成音频时，如果提供了 `read`，程序会把 VOICEVOX 生成的读音和人工标注读音做初步比较。

可疑项会写入：

```text
out/err.txt
```

自动生成时每行格式是：

```text
index<TAB>word<TAB>read<TAB>voicevox_read
```

人工校对后，`replace_err()` 期望每行格式是：

```text
index<TAB>word<TAB>read<TAB>AquesTalk风记法
```

其中 `AquesTalk风记法` 用来覆盖 VOICEVOX 自动推断出的读音。

## 当前人工步骤

目前这些步骤仍建议人工完成：

- 检查图片排版是否溢出、遮挡或高亮错误。
- 检查 `err.txt` 里的可疑读音。
- 手动对齐图片和音频。
- 在 PR / 剪辑工程中合成最终视频。

这些步骤不急着自动化。先把输入格式、素材生成、人工校对流程稳定下来，会更安全。

## 后续优化方向

优先级从低风险到高收益：

1. 把硬编码路径迁移到 `config.yaml`。
2. 增加 `Excel -> JSON/YAML` 的中间格式导出，方便检查和复用。
3. 用 `dataclass` 继续明确章节、语法点、小项、例文等输入模型。
4. 继续增加模板，例如单词列表、ruby 单词网格、汉字详解。
5. 给 VOICEVOX 请求增加超时、重试和服务未启动提示。
6. 给输出文件生成 `manifest.json`，记录图片、音频和校对状态。
7. 等人工流程稳定后，再考虑自动视频合成。
