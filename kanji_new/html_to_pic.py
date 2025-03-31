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
        body {
            background-color: black;  /* 背景色为黑色 */
            font-family: "Georgia", "UD デジタル 教科書体 N", sans-serif;  /* 字体 */
            color: white;  /* 字体颜色为白色 */
            font-size: 40px;  /* 设置字体大小 */
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
            font-size: 36px;
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
    def __init__(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.set_window_size(1920, 1080)

    def set_window_size(self, width, height):
        self.driver.set_window_size((width * 2 + 42) // 3, (height * 2 + 438) // 3)

    def generate_pic(self, html_content, path):
        html_content = html_content_prefix + html_content + html_content_suffix

        self.driver.get(
            "data:text/html;charset=utf-8," + urllib.parse.quote(html_content)
        )  # urllib.parse.quote防止某些字符转义上出问题

        time.sleep(1)

        self.driver.save_screenshot(path)

    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":
    html_to_pic = HtmlToPic()
    html = """
<p><span class="highlight">バイク （bike） ①	</span>《名》<br/><span class="zh">自行车；摩托车</span></p>
<p>バス[bus] （bus） ①	《名》<br/><span class="zh">巴士，公交车</span></p>
<p>バター （butter） ①	《名》<br/><span class="zh">黄油</span></p>
<p>バナナ （banana） ①	《名》<br/><span class="zh">香蕉</span></p>
<p>パン （(葡) pão） ①	《名》<br/><span class="zh">面包</span></p>
"""
    html_to_pic.generate_pic(html, "./kanji_new/test.png")
    time.sleep(5)
