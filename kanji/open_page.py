# 这个文件打开weblio以供校对

import webbrowser

kanjis = "広鉱荒慌光皇黄狂況壮荘装粧状窓双創爽霜床亡忘望妄網王旺往"
urls = [f'https://www.weblio.jp/content/{it}' for it in kanjis]

for url in urls:
    webbrowser.open(url)