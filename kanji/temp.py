import numpy as np
from manimlib import *

font = "UD Digi Kyokasho NK-R"

class GammerExample(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def construct(self):

        text1 = Text("Aが→Bを", font=font, font_size=50).to(-1, 1)
        text2 = Text("犬が太郎を噛んだ。", font=font, font_size=50)
        text3 = Text("Bが←Aに", font=font, font_size=50)
        text4 = Text("太郎が犬に噛まれた。", font=font, font_size=50)

        # text1.generate_target()
        # text2.generate_target()
        # text3.generate_target()
        # text4.generate_target()

        # VGroup(text1.target, text2.target).arrange(DOWN, buff=1).to_edge(LEFT)
        # VGroup(text3.target, text4.target).arrange(DOWN, buff=1).to_edge(RIGHT)

        self.play(Write(text1))
        # self.play(MoveToTarget(text1))
        self.play(Write(text2))
        # self.play(MoveToTarget(text2))
        self.play(Write(text3))
        # self.play(MoveToTarget(text3))
        self.play(Write(text4))
        # self.play(MoveToTarget(text4))
        self.wait(3)
