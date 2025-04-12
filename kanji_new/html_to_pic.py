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
            font-size: 57px;  /* 设置字体大小 */
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
<p><span><ruby>自分<rt>じぶん</rt></ruby></span> <span><ruby>問題<rt>もんだい</rt></ruby></span> <span><ruby>準備<rt>じゅんび</rt></ruby></span> <span><ruby>大丈夫<rt>だいじょうぶ</rt></ruby></span> <span><ruby>僕<rt>ぼく</rt></ruby></span> </p>
<p><span><ruby>全部<rt>ぜんぶ</rt></ruby></span> <span><ruby>邪魔<rt>じゃま</rt></ruby></span> <span><ruby>時代<rt>じだい</rt></ruby></span> <span><ruby>残念<rt>ざんねん</rt></ruby></span> <span><ruby>現在<rt>げんざい</rt></ruby></span> </p>
<p><span><ruby>無駄<rt>むだ</rt></ruby></span> <span><ruby>随分<rt>ずいぶん</rt></ruby></span> <span><ruby>技術<rt>ぎじゅつ</rt></ruby></span> <span><ruby>道具<rt>どうぐ</rt></ruby></span> <span><ruby>現場<rt>げんば</rt></ruby></span> </p>
<p><span class="highlight"><span><ruby>大学<rt>だいがく</rt></ruby></span></span> <span><ruby>絶望<rt>ぜつぼう</rt></ruby></span> <span><ruby>堂々<rt>どうどう</rt></ruby></span> <span><ruby>材料<rt>ざいりょう</rt></ruby></span> <span><ruby>同情<rt>どうじょう</rt></ruby></span> </p>
<p><span><ruby>前後<rt>ぜんご</rt></ruby></span> <span><ruby>護衛<rt>ごえい</rt></ruby></span> <span><ruby>旦那<rt>だんな</rt></ruby></span> <span><ruby>矛盾<rt>むじゅん</rt></ruby></span> <span><ruby>番号<rt>ばんごう</rt></ruby></span> </p>
"""
    html_to_pic.generate_pic(html, "./kanji_new/test.png")
    time.sleep(5)
