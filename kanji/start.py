import numpy as np
from manimlib import *

import sys

sys.path.insert(0, "./")  # or sys.path.append('/path/to/application/app/folder')
from parse import load_kanjis


class VoteExample(Scene):
    def construct(self):
        axes = Axes(
            # x轴的范围从-1到10，步长为1
            x_range=(0, 11),
            # y轴的范围从-2到2，步长为0.5y-axis ranges from -2 to 10 with a step size of 0.5
            y_range=(0.0, 0.5, 0.05),
            # 坐标系将会伸缩来匹配指定的height和width
            height=6,
            width=10,
            x_axis_config={
                "include_numbers": False,
                "decimal_number_config": {"num_decimal_places": 0},
            },
            y_axis_config={
                "include_numbers": False,
                "decimal_number_config": {"num_decimal_places": 2},
            },
        )
        axes.add_coordinate_labels()
        self.play(Write(axes))


class TextExample(Scene):
    def __init__(self, *args, **kwargs):
        """
        定义字体大小以及排版时的位置
        """
        super().__init__(*args, **kwargs)

        self.kjs = 51  # kanji size
        self.rms = 21  # romaji size
        self.bks = 200  # big kanji size
        self.font = "UD Digi Kyokasho NK"
        self.big_kanji_scale = 0.35
        self.big_kanji_shift_up = np.array([-0.35, 3.45, 0])

        self.kanji_space = np.array([0.65, 0, 0])  # 汉字和汉字之间的间隔
        self.tango_space = np.array([0.35, 0, 0])  # 词和词之间的间隔
        self.romaji_space = np.array([0, 0.5, 0])  # 词和假名之间的距离

        self.left_up = np.array([-6.0, 2.75, 0])  # 左半部分左上角第一个例词
        self.center_up = np.array([1.0, 2.75, 0])  # 右半部分左上角第一个例词
        self.tab_length = np.array([0.75, 0, 0])  # 方括号比例词靠左的缩进
        self.line_height = np.array([0, 1.1, 0])  # 行高
        self.hatsuon_come_up = np.array([0, 0.125, 0])  # 发音行向上移动的高度

        self.time_between_kanji = 2  # 两个汉字间切换时的等待时间
        self.time_display_big_kanji = 0.5  # 大汉字出现后的等待时间
        self.time_between_word = 0.5  # 两个词之间的等待时间

    def write_word(self, word, roma, position):
        # 在指定位置绘制单词
        l = len(word)
        mobs = []
        romas = roma.split("　")
        is_combine = False  # 多个字对一个读音
        total_skip = 0
        for i in range(l):
            kj = Text(word[i], font=self.font, font_size=self.kjs)
            kj.move_to(position)
            mobs.append(kj)

            if not is_combine and romas[i - total_skip].startswith("（"):
                is_combine = True
                if romas[i - total_skip][1] in "123456789":  # 跳过的长度
                    combine_len = int(romas[i - total_skip][1])
                    combine_word = romas[i - total_skip][2:-1]
                else:
                    combine_len = 2
                    combine_word = romas[i - total_skip][1:-1]
                total_skip += combine_len - 1
                end_i = i + combine_len - 1
                start_position = position

            if not is_combine:  # 单字模式
                if len(romas[i - total_skip]) > 0:
                    rm = Text(romas[i - total_skip], font=self.font, font_size=self.rms)
                    rm.move_to(position + self.romaji_space)
                    mobs.append(rm)

            if is_combine and i == end_i:  # 组合模式
                is_combine = False
                rm = Text(combine_word, font=self.font, font_size=self.rms)
                rm.move_to((position + start_position) / 2 + self.romaji_space)
                mobs.append(rm)

            position = position + self.kanji_space
        position = position + self.tango_space
        self.play(*[ShowCreation(mob) for mob in mobs])
        self.wait(self.time_between_word)
        return position, mobs

    def write_kanji(self, kanji):
        # 中心汉字
        kanji = Text(kanji, font=self.font, font_size=self.bks)
        self.play(Write(kanji))
        self.wait(self.time_display_big_kanji)
        self.play(kanji.animate.scale(self.big_kanji_scale))
        self.play(kanji.animate.shift(self.big_kanji_shift_up))
        return kanji

    def write_hatsuon(self, text, position):
        mob = Text(text, font=self.font, font_size=self.kjs)
        mob.move_to(position, aligned_edge=LEFT)
        self.play(ShowCreation(mob))
        return mob

    def write_para(self, raw_text, position):
        all_mob = []
        text_lines = raw_text.splitlines()
        start_position = position  # 每行的开始位置
        for text in text_lines:
            text: str
            if text.startswith("["):
                start_position += self.hatsuon_come_up
                hatsuon = self.write_hatsuon(text, start_position - self.tab_length)
                all_mob.append(hatsuon)
            else:
                kj_part, rm_part = text.split("：")
                kj_part = kj_part.split("/")
                rm_part = rm_part.split("/")
                position = start_position
                for word, roma in zip(kj_part, rm_part):
                    try:
                        position, mobs = self.write_word(word, roma, position)
                    except Exception as e:
                        print(e)
                        print(f"出现了错误 ：writing word {word} with roma {roma}")
                        raise e
                    all_mob += mobs
            start_position -= self.line_height
        return all_mob

    def display_whole_kanji(self, text, need_fade=True):
        parts = text.split("\n\n")
        all_mobs = []
        all_mobs.append(self.write_kanji(parts[0]))  # 中心汉字
        all_mobs += self.write_para(parts[1], self.left_up.copy())  # 左半部分
        all_mobs += self.write_para(parts[2], self.center_up.copy())  # 右半部分
        self.wait(self.time_between_kanji)

        if need_fade:
            self.play(*[FadeOut(mob) for mob in all_mobs])
        else:
            return all_mobs

    def construct(self):
        # 关于Text全部用法，请见https://github.com/3b1b/manim/pull/680
        path = "./raw.md" if os.path.exists("./raw.md") else "./kanji/raw.md"
        self.texts = load_kanjis(path)  # [-1:]
        for text in self.texts:
            self.display_whole_kanji(text)
        # self.embed()
        return

        text1 = Text("[漢]<br>セイ 正義せいぎ　改正かいせい", font=font, font_size=50)
        text2 = Text("[呉]ショウ 正気しょうき　正月しょうがつ", font=font, font_size=50)
        text3 = Text("[訓]ただ(しい)", font="UD Digi Kyokasho NK-R", font_size=50)

        kanji.generate_target()
        text1.generate_target()
        text2.generate_target()
        text3.generate_target()

        kanji.to_edge(LEFT)
        VGroup(text1.target, text2.target).arrange(DOWN, buff=1).to_edge(LEFT)
        text3.to_edge(RIGHT)

        self.play(Write(kanji))
        self.play(MoveToTarget(kanji))
        self.play(Write(text1))
        self.play(MoveToTarget(text1))
        self.play(Write(text2))
        self.play(MoveToTarget(text2))
        self.play(Write(text3))
        self.play(MoveToTarget(text3))
        self.wait(3)


class T(TextExample):
    def construct_by_index(self, index=0):
        path = "./raw.md" if os.path.exists("./raw.md") else "./kanji/raw.md"
        self.texts = load_kanjis(path)
        self.display_whole_kanji(self.texts[index], need_fade=False)


class T0(T):
    def construct(self):
        self.construct_by_index(0)


class T1(T):
    def construct(self):
        self.construct_by_index(1)


class T2(T):
    def construct(self):
        self.construct_by_index(2)


class T3(T):
    def construct(self):
        self.construct_by_index(3)


class T4(T):
    def construct(self):
        self.construct_by_index(4)


class T5(T):
    def construct(self):
        self.construct_by_index(5)


class T6(T):
    def construct(self):
        self.construct_by_index(6)


class T7(T):
    def construct(self):
        self.construct_by_index(7)


class T8(T):
    def construct(self):
        self.construct_by_index(8)


class T9(T):
    def construct(self):
        self.construct_by_index(9)


class T10(T):
    def construct(self):
        self.construct_by_index(10)


class T11(T):
    def construct(self):
        self.construct_by_index(11)


class T12(T):
    def construct(self):
        self.construct_by_index(12)


class T13(T):
    def construct(self):
        self.construct_by_index(13)


class T14(T):
    def construct(self):
        self.construct_by_index(14)


class T15(T):
    def construct(self):
        self.construct_by_index(15)


class T16(T):
    def construct(self):
        self.construct_by_index(16)


class T17(T):
    def construct(self):
        self.construct_by_index(17)


class T18(T):
    def construct(self):
        self.construct_by_index(18)


class T19(T):
    def construct(self):
        self.construct_by_index(19)


class T20(T):
    def construct(self):
        self.construct_by_index(20)


class T21(T):
    def construct(self):
        self.construct_by_index(21)


class T22(T):
    def construct(self):
        self.construct_by_index(22)


class T23(T):
    def construct(self):
        self.construct_by_index(23)


class T24(T):
    def construct(self):
        self.construct_by_index(24)


class T25(T):
    def construct(self):
        self.construct_by_index(25)


class T26(T):

    def construct(self):
        self.construct_by_index(26)


class T27(T):
    def construct(self):
        self.construct_by_index(27)


class T28(T):
    def construct(self):
        self.construct_by_index(28)


class T29(T):
    def construct(self):
        self.construct_by_index(29)


class T30(T):
    def construct(self):
        self.construct_by_index(30)


class T31(T):
    def construct(self):
        self.construct_by_index(31)


class T32(T):
    def construct(self):
        self.construct_by_index(32)

class T33(T):
    def construct(self):
        self.construct_by_index(33)
class T34(T):
    def construct(self):
        self.construct_by_index(34)
class T35(T):
    def construct(self):
        self.construct_by_index(35)
class T36(T):
    def construct(self):
        self.construct_by_index(36)
class T37(T):
    def construct(self):
        self.construct_by_index(37)
class T38(T):
    def construct(self):
        self.construct_by_index(38)
class T39(T):
    def construct(self):
        self.construct_by_index(39)
class T40(T):
    def construct(self):
        self.construct_by_index(40)
class T41(T):
    def construct(self):
        self.construct_by_index(41)
class T42(T):
    def construct(self):
        self.construct_by_index(42)
class T43(T):
    def construct(self):
        self.construct_by_index(43)
class T44(T):
    def construct(self):
        self.construct_by_index(44)
class T45(T):
    def construct(self):
        self.construct_by_index(45)
class T46(T):
    def construct(self):
        self.construct_by_index(46)
class T47(T):
    def construct(self):
        self.construct_by_index(47)
class T48(T):
    def construct(self):
        self.construct_by_index(48)
class T49(T):
    def construct(self):
        self.construct_by_index(49)
class T50(T):
    def construct(self):
        self.construct_by_index(50)
class T51(T):
    def construct(self):
        self.construct_by_index(51)
class T52(T):
    def construct(self):
        self.construct_by_index(52)
class T53(T):
    def construct(self):
        self.construct_by_index(53)
class T54(T):
    def construct(self):
        self.construct_by_index(54)
class T55(T):
    def construct(self):
        self.construct_by_index(55)





if __name__ == "__main__":
    T0().construct()
