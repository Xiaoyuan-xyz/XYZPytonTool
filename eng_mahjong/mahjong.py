import string
from solver import solver, display_result
from word_list import count_letter
import random

num_pai = [6, 2, 4, 4, 8, 4, 4, 4, 8, 2, 2, 4, 4, 6, 8, 2, 2, 4, 4, 8, 4, 2, 2, 2, 2, 2]
mahjong = ''.join([random.choices(string.ascii_lowercase, num_pai)[0]for i in range(13)])

print('当前手牌', mahjong)

# mahjong = input('请输入当前的手牌')
with open('./wordlist/mix_c2.txt', 'r', encoding='utf8') as file:
    word_list = [line.strip() for line in file]

data = count_letter(word_list)
for letter in string.ascii_lowercase:
    need_check = mahjong + letter
    need_check = count_letter([need_check]).squeeze()

    status, indexes, counts = solver(data, need_check)
    if status == 1:
        print(f'{letter}和牌', ' '.join(display_result(word_list, indexes, counts)))
    else:
        print(f'{letter}无法和牌')
