import json


with open('./kanji/kanji/kanji_kyoiku/kanji_kyoiku.json', 'r', encoding='utf-8') as f:
    kanji_dict = json.load(f)

# print(kanji_dict[index]['漢字'])
# print(kanji_dict[index]['音読み（区分あり）'].split(' '))
# print(kanji_dict[index]['訓読み（区分あり）'].split(' '))
# print('==' + '\n=='.join(kanji_dict[index]['意味（区分あり）'].split(' ')))
# print(kanji_dict[index]['難読'])
# print(kanji_dict[index]['種別'])

def check_single_onyomi(kanji):
    index = 0
    for content in kanji_dict:
        if content['漢字'] == kanji:
            break
        index += 1
    if index == len(kanji_dict):
        print('not found')
        return
    ret = kanji_dict[index]['音読み（区分あり）'].split(' ')
    
    delete = []
    for i in range(len(ret)// 2):
        if '△' in ret[i*2 + 1]:
            delete.append(i*2)
            delete.append(i*2+1)
    ret = [ret[i] for i in range(len(ret)) if i not in delete]
    
    print(kanji, len(ret) == 2)
    # print(ret)
    
if __name__ == '__main__':
    for kanji in '政治経済':
        check_single_onyomi(kanji)