# 读html 然后生成成图片

import time
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

html_content_prefix = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080, initial-scale=0.5">
    <title>Japanese Vocabulary</title>
    <style>
"""

default_style = """
        body {
            background-color: black;  /* 背景色为黑色 */
            font-family: "Georgia", "UD デジタル 教科書体 N", sans-serif;  /* 字体 */
            color: white;  /* 字体颜色为白色 */
            font-size: 45px;  /* 设置字体大小 */
            margin: 0;
            padding: 50px;
        }

        .content {
            width: 1000px;
            height: 600px;
            overflow: hidden;
        }

        .highlight {
            color: lightblue;
        }

        .zh {
            font-family: "思源宋体 CN";
            font-size: 45px;
        }

        span {
            white-space: nowrap; // 禁止span内换行
        }

        ruby {
            white-space: nowrap;
        }

        p {
            text-indent: -2em;
            margin-left: 2em;
            margin-top: 0;
            margin-bottom: 3px;
        }
"""

html_content_middle = """
    </style>
</head>
<body>
    <div class="content">
"""
html_content_suffix = """
    </div>
</body>
</html>
<!---->
"""


class HtmlToPic:
    def __init__(self, style=default_style, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.set_window_size(1920, 1080)
        self.style = style

    def set_window_size(self, width, height):
        self.driver.set_window_size((width * 2 + 42) // 3, (height * 2 + 438) // 3)

    def generate_pic(self, html_content, path):
        html_content = html_content_prefix + self.style + html_content_middle + html_content + html_content_suffix

        self.driver.get(
            "data:text/html;charset=utf-8," + urllib.parse.quote(html_content)
        )  # urllib.parse.quote防止某些字符转义上出问题

        time.sleep(1)

        self.driver.save_screenshot(path)

    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":

    style = """
        body {
            background-color: black;  /* 背景色为黑色 */
            font-family: "Georgia", "UD デジタル 教科書体 N", sans-serif;  /* 字体 */
            color: white;  /* 字体颜色为白色 */
            font-size: 40px;  /* 设置字体大小 */
            margin: 0;
            padding: 40px;
        }

        .content {
            width: 1000px;
            height: 640px;
            overflow: hidden;
        }

        .highlight {
            color: lightblue;
        }

        .zh {
            font-family: "思源宋体 CN";
            font-size: 26px;
        }

        p {
            text-indent: -2em;
            margin-left: 2em;
            margin-top: 0;
            margin-bottom: 3px;
        }
"""

    html_to_pic = HtmlToPic(style)
    html = """
<p><span>　　～て</span>
<br/>
<p><span class="zh"><b></b></span></p>
<p><span class="zh"><b>同时进行</b></span></p>
<p><span class="highlight">　　書を見て漢字を覚えます。</span></p>
<p><span class="zh">　　看着词典背汉字。</span></p>
<p><span class="zh"><b>相继发生</b></span></p>
<p><span class="highlight">　　昨日の夜は６時に帰って、ご飯を作りました。</span></p>
<p><span class="zh">　　昨晚六点回家，然后做了饭。</span></p>
<p><span class="zh"><b>方法手段</b></span></p>
<p><span class="highlight">　　バスに乗って海へ行きました。</span></p>
<p><span class="zh">　　坐公共汽车去了海边</span></p>
<p><span class="zh"><b>原因</b></span></p>
<p><span class="highlight">　　財布をなくして困りました。</span></p>
<p><span class="zh">　　钱包没了，很苦恼。</span></p>
"""
    html_to_pic.generate_pic(html, "./kanji_new/test.png")
    time.sleep(5)
