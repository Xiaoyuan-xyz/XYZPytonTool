# 读html 然后生成成图片

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import urllib

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
            font-family: "UD デジタル 教科書体 N", sans-serif;  /* 字体 */
            color: white;  /* 字体颜色为白色 */
            font-size: 65px;  /* 设置字体大小 */
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
            margin-bottom: 0;
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
    def __init__(self):
        pass

        # 配置WebDriver（Chrome浏览器
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器界面

        # 初始化WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.set_window_size(1920, 1080)
    def set_window_size(self, width, height):
        self.driver.set_window_size((width*2+42)//3, (height*2+438)//3)

    def generate_pic(self, html_content, path):
        html_content = html_content_prefix + html_content + html_content_suffix

        # 将HTML内容载入到浏览器
        self.driver.get("data:text/html;charset=utf-8," + urllib.parse.quote(html_content))

        # 等待页面渲染完成
        time.sleep(1)

        # 截图并保存
        self.driver.save_screenshot(path)
    
    def __del__(self):
        self.driver.quit()

if __name__ == '__main__':
    html_to_pic = HtmlToPic()
    html = """
<p>眺：<span style="opacity:0.3;"><ruby>眺望<rt>ちょうぼう</rt></ruby></span> </p>
<p>挑：<span><ruby>挑戦<rt>ちょうせん</rt></ruby></span> </p>
<p>跳：<span style="opacity:0.6;"><ruby>跳躍<rt>ちょうやく</rt></ruby></span> </p>
<p>彫：<span class="highlight"><span><ruby>彫刻<rt>ちょうこく</rt></ruby></span></span> </p>
<p>調：<span><ruby>調子<rt>ちょうし</rt></ruby></span> </p>
"""
    html_to_pic.generate_pic(html, "./kanji_new/test.png")
    time.sleep(5)
