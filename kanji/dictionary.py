import json


with open('./kanji/kanji/kanji_kyoiku/kanji_kyoiku.json', 'r', encoding='utf-8') as f:
    kanji_dict = json.load(f)

# print(kanji_dict[index]['漢字'])
# print(kanji_dict[index]['音読み（区分あり）'].split(' '))
# print(kanji_dict[index]['訓読み（区分あり）'].split(' '))
# print('==' + '\n=='.join(kanji_dict[index]['意味（区分あり）'].split(' ')))
# print(kanji_dict[index]['難読'])
# print(kanji_dict[index]['種別'])

def find_kanji_index(kanji):
    index = 0
    for content in kanji_dict:
        if content['漢字'] == kanji:
            break
        index += 1
    if index == len(kanji_dict):
        print(kanji, 'not found')
    return index

def check_single_onyomi(index):
    onyomi = kanji_dict[index]['音読み（区分あり）']
    if onyomi is None:
        return 0
    ret = onyomi.split(' ')
    
    delete = []
    for i in range(len(ret)// 2):
        if '△' in ret[i*2 + 1]:
            delete.append(i*2)
            delete.append(i*2+1)
    ret = [ret[i] for i in range(len(ret)) if i not in delete]
    
    print(kanji, len(ret) == 2)
    print(ret)
    return len(ret) // 2
    
if __name__ == '__main__':
    for kanji in '日常茶飯日常坐臥':
        index = find_kanji_index(kanji)
        if index != len(kanji_dict):
            check_single_onyomi(index)
    
    # counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # [15, 795, 198, 17, 0, 1, 0, 0, 0, 0]
    # for i in range(len(kanji_dict)):
    #     ret = check_single_onyomi(i)
    #     counts[ret] += 1
    # print(counts)