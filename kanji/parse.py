import re

hiragana = re.compile('[ぁ-ん]')
MAX_KANJI = 8


def parse_word(line: str):
    blocks = line.split('　')
    if len(blocks) <= 2:
        try:
            # 词以假名结尾 放在第一个汉字上
            if hiragana.match(blocks[0][-1]):
                return blocks[0], blocks[1] + ''  # 末尾可以加若干空格
            # 不以假名结尾 放在全体汉字上
            l = len(blocks[0])
            return (blocks[0], ''.join([
                '（', str(l), blocks[1], '）'
            ]))
        except IndexError as e:
            print('I found a IndexError 可能是多余的空行 或 行格式不对: ', line)
            raise e
    # 一般的就老老实实写
    return blocks[0], '　'.join(blocks[1:])  # 这里也可以加空格


def parse_part(lines):
    # 处理若干个发音+词 也就是左半边或右半边
    part = []
    lines.append('[')
    words = []
    now_hatsuon = None
    for line in lines:
        line: str
        if line.startswith('['):
            if len(words) > 0:
                part.append((now_hatsuon, words))
            now_hatsuon = line
            words = []
        else:
            if line.endswith('.'):  # 以句点结束 用None表示换行
                line = line[:-1]  # 去句点
                words.append(parse_word(line))
                words.append(None)
            else:
                words.append(parse_word(line))
    return part


def parse_single_kanji(lines):
    kanji = {}
    kanji["name"] = lines[0][0]
    try:
        index = lines.index('')  # 原先一个空行变成空字符串了
    except ValueError as e:
        print('I found a ValueError 可能是空行中包含空格 或 缺少第二个[] :', lines)
        raise e
    kanji["left"] = parse_part(lines[1:index])
    kanji["right"] = parse_part(lines[index + 1:])
    return kanji


def apply_part(part):
    lines = []
    for subpart in part:
        on = subpart[0] + '\n'
        lines.append(on)
        total_ji = 0
        kjs = []
        rms = []
        subpart[1].append(None)
        for word in subpart[1]:
            if word is None or total_ji + len(word[0]) > MAX_KANJI:
                line = '/'.join(kjs) + '：' + '/'.join(rms) + '\n'
                lines.append(line)
                total_ji = 0
                kjs = []
                rms = []
            if word:
                kjs.append(word[0])
                rms.append(word[1])
                total_ji += len(word[0])
    return ''.join(lines)


def apply_kanji(kanji):
    name = kanji["name"]
    return name + '\n\n' + apply_part(kanji["left"]) + '\n' + apply_part(kanji["right"])


def load_kanjis(path):
    # 从文件里读取文本
    with open(path, 'r', encoding='utf8') as fp:
        txt = fp.readlines()

    # 删掉第一个#之前的所有内容
    for index, line in enumerate(txt):
        if line.startswith('#'):
            break
    txt = txt[index:]

    # 替换部分字符
    l = len(txt)
    for i in range(l):
        txt[i] = txt[i].replace(' ', '　')
        txt[i] = txt[i].replace('(', '（')
        txt[i] = txt[i].replace(')', '）')
        txt[i] = txt[i].replace('［', '[')
        txt[i] = txt[i].replace('］', ']')
        txt[i] = txt[i].replace('\n', '')
        # 下面几行负责把n个-变成n+1个空格
        is_end_with_dash = txt[i].endswith('-')
        txt[i] = txt[i].replace('-', '　-　')
        txt[i] = txt[i].replace('　　', '　')
        txt[i] = txt[i].replace('-', '')
        if is_end_with_dash:
            txt[i] = txt[i][:-1]

    # 末尾加个井号方便截止
    txt.append('# 文件结尾')
    text = []
    temp_text = []
    for line in txt:
        if line.startswith('#'):
            if len(temp_text) > 0:
                text.append(temp_text)
            temp_text = []
            line = line[2:]  # 去掉井号和第一个空格
        temp_text.append(line)

    kanjis = []
    for lines in text:
        while lines[-1] == '':  # 去除末尾的若干空行
            lines = lines[:-1]
        kanjis.append(parse_single_kanji(lines))  # 转换成对象格式
    return [apply_kanji(kanji) for kanji in kanjis]  # 转换成可应用的字符串


def words_display(string):
    """
    把load_kanjis()[0]的结果 转换为只有单词并用/划分的一行
    """
    lines = string.split('\n')
    result = []

    for line in lines:
        if '：' in line:
            parts = line.split('：')
            result.append(parts[0])

    # 使用斜杠进行拼接
    return '/'.join(result)


if __name__ == '__main__':
    for it in load_kanjis('./kanji/raw.md'):
        print(words_display(it))

    # todo: 加载汉字后按自己的顺序排序
