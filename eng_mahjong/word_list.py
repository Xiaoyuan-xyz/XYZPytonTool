# 用于处理文字生成词表 以及矩阵的生成
import numpy as np
from unidecode import unidecode
import string
from collections import Counter

raw_path = './raw/'
cleanup_path = './cleanup/'
wordlist_path = './wordlist/'
levels = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
ae_names = ['ae_a1.txt', 'ae_a2.txt', 'ae_b1.txt', 'ae_b2.txt', 'ae_c1.txt', 'ae_c2.txt']
be_names = ['be_a1.txt', 'be_a2.txt', 'be_b1.txt', 'be_b2.txt', 'be_c1.txt', 'be_c2.txt']
ae = [571, 1040, 1740, 2349, 1395, 1673]
be = [571, 1040, 1773, 2372, 1413, 1692]
mx = [571, 1040, 1849, 2437, 1463, 1742]
ae = [571, 1424, 2744, 4439, 5419, 6408]
be = [571, 1424, 2782, 4482, 5455, 6444]
mx = [571, 1424, 2838, 4560, 5557, 6556]

def cleanup(input_path, output_path):
    # 去除词组 去除重复词 转换非ascii字符
    with open(input_path, 'r', encoding='utf8') as file:
        # 末尾带\n
        lines_list = file.readlines()

    # cleaned_list2 = [line.lower() for line in lines_list if line.strip().isalpha()]
    cleaned_list = [unidecode(line).lower() for line in lines_list if line.strip().isalpha()]
    cleaned_list = list(set(cleaned_list))
    print(len(cleaned_list))
    with open(output_path, 'w', encoding='utf8') as file:
        for item in cleaned_list:
            file.write(item)
def greate_wordlist(names):
    word_list = []
    for level in range(6):
        with open(cleanup_path + names[level], 'r', encoding='utf8') as file:
            word_list.extend(file.readlines())
        word_list = list(set(word_list))
        print(len(word_list))
        with open(wordlist_path + names[level], 'w', encoding='utf8') as file:
            for item in word_list:
                file.write(item)

def mix(path):
    for i in range(6):
        word_list = []
        with open(path + ae_names[i], 'r', encoding='utf8') as file:
            word_list.extend(file.readlines())
        with open(path + be_names[i], 'r', encoding='utf8') as file:
            word_list.extend(file.readlines())
        word_list = list(set(word_list))
        print(len(word_list))
        with open(path + f'mix_{levels[i]}.txt', 'w', encoding='utf8') as file:
            for item in word_list:
                file.write(item)

def count_letter(wordlist):
    len_wordlist = len(wordlist)
    mat = np.zeros(shape=(len_wordlist, 26), dtype='int')
    for i in range(len_wordlist):
        for letter in wordlist[i].strip():
            if not ord('a')<= ord(letter) <= ord('z'):
                print(wordlist[i])
            mat[i, ord(letter)-97] += 1
    return mat.T

if __name__ == '__main__':
    cleanup(raw_path + 'oxford3000.txt', cleanup_path + 'oxford3000.txt')
    cleanup(raw_path + 'oxford5000.txt', cleanup_path + 'oxford5000.txt')
    wordlist = []
    with open(cleanup_path + 'oxford3000.txt', 'r', encoding='utf8') as file:
        wordlist.extend(file.readlines())
    with open(cleanup_path + 'oxford5000.txt', 'r', encoding='utf8') as file:
        wordlist.extend(file.readlines())
    print(len(wordlist))
    with open(wordlist_path + 'oxford.txt', 'w', encoding='utf8') as file:
        for item in wordlist:
            file.write(item)

    for i in range(6):
        cleanup(raw_path+ae_names[i], cleanup_path+ae_names[i])
        cleanup(raw_path + be_names[i], cleanup_path+be_names[i])
    greate_wordlist(ae_names)
    greate_wordlist(be_names)
    mix(cleanup_path)
    mix(wordlist_path)
