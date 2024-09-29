import json


with open('./kanji/kanji/kanji_kyoiku/kanji_kyoiku.json', 'r', encoding='utf-8') as f:
    kanji_dict = json.load(f)

kanji = '临'

index = 0
for content in kanji_dict:
    if content['漢字'] == kanji:
        break
    index += 1

print(kanji_dict[index]['漢字'])
print(kanji_dict[index]['音読み（区分あり）'].split(' '))
print(kanji_dict[index]['訓読み（区分あり）'].split(' '))
print('==' + '\n=='.join(kanji_dict[index]['意味（区分あり）'].split(' ')))
print(kanji_dict[index]['難読'])
print(kanji_dict[index]['種別'])