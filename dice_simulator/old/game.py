"""
游戏阶段：
    回合数变更阶段 TURN STAGE
        回合数+1
        调两个角色的turn_stage()
            角色属性重置
            技能回合数更新
            撤销激活过期的技能
            遍历本回合要使用的技能
                可以释放的激活
                不能释放的调delay() 延迟到下回合或者延迟duration
    准备阶段 SKILL/PASSIVE STAGE
        遍历所有的主动技能 发动它们
        发动一个技能的过程
            判断能否发动
            给对方发消息 获知能否破解
            根据是否破解 发动技能
    拼点阶段 DICE STAGE
        判断是否有自动胜利
        攻击骰
        判断攻守
        DICE期技能
    伤害生成阶段 GENERATE STAGE
        负方伤害生成
        伤害修正
        作用伤害
    追击阶段 PURSUIT/COUNTER STAGE
        作用同准备阶段

    伤害阶段 DAMAGE
        伤害前技能：比如护盾
        伤害结算
        伤害后技能：比如反击

技能分为两部分 外层负责封装 供角色激活和调用 内层负责具体逻辑

外层的功能：
    在合适的时机激活 将自己的内层放置到合适的队列中
内层的功能：
    技能的具体实现


消息的类型：
    技能的激活 ACTIVATE
    技能的宣言 SPELL
    技能的释放 APPLY
    技能的结束 END

    骰子出目
"""
import heapq
# todo: 技能结束是不是也要发消息？
# todo: 一个可以直接显示的buff列表
# todo: 给每个技能的释放自动写logging
# todo: 把技能和技能的功能分开

import logging
import random

class Skill:
    def __init__(self):
        pass

class ActiveSkill(Skill):
    def __init__(self):
        super.__init__()


class PassiveSkill(Skill):
    def __init__(self):
        super().__init__()


class SkillGroup(Skill):
    """
    技能组的主要目标是放在角色下 供角色激活技能
    主要调的函数是activate()


    到回合时判断激活
    激活需要不冲突


    """
    def __init__(self, name, stage, priority, first_turn, duration, cooldown, tags=None):
        super().__init__()
        self.name = name
        self.stage = stage
        self.priority = priority
        self.first_turn = first_turn
        self.duration = duration
        self.cooldown = cooldown
        if tags is None:
            tags = {}
        self.tags = tags

        self.is_active = False # 当前是否激活
        self.is_expired = False # 当前是否该结束

        self.next_turn = first_turn
        self.remains =  duration



class SkillQueue:
    def __init__(self):
        self.queue : list[Skill] = []

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return iter(self.queue)

    def __contains__(self, item):
        return item in self.queue

    def __getitem__(self, key):
        return self.queue[key]

    def __setitem__(self, key, value):
        self.queue[key] = value

    def add_skill(self, skill: Skill):
        heapq.heappush(self.queue, skill)

    def remove_expired_skill(self):
        self.queue = [it for it in self.queue if not it.is_expired]

    def turn_stage(self):
        for it in self.queue:
            it.remains -= 1
            it.lasting += 1
            if it.remains == 0:
                it.is_expired = True

    def deactivate_expired_skill(self):
        for it in self.queue:
            it:SkillGroup
            if it.is_expired:
                it.is_active = False
                it.lasting = 0
                it.remains = it.duration
                it.next_turn += it.cooldown


        pass


class Message:
    def __init__(self):
        pass

class Character:
    def __init__(self, name, init_atk, init_hp, init_max_hp, init_tags=None):
        # 初始值 在正常战斗中都不会改变
        self.name = name
        self.init_atk = init_atk
        self.init_hp = init_hp
        self.init_max_hp = init_max_hp
        if init_tags is None:
            init_tags = {}
        self.init_tags = init_tags
        self.init_damage_list = {'回避':10, '小伤害':30, '中伤害':50, '大伤害':70, '特大伤害':90, '大失败':95, '大成功':100}

        # 白值 每回合初始赋值成这个
        self.base_atk = init_atk
        self.base_hp = init_hp
        self.base_max_hp = init_max_hp

        # 实际值 每回合都变化
        self.atk = self.base_atk
        self.hp = self.base_atk
        self.max_hp = self.base_max_hp

        self.last_dice = 0
        self.counteract_offset = 0
        self.dice_series = []
        self.base_queue = SkillQueue()
        self.passive_queue = SkillQueue() # 这两个要清空吗？
        self.damage_queue = SkillQueue()

        self.tags = self.init_tags.copy()
        self.turn_win = False # 本回合自动获胜
        self.hurt_dice = 0
        self.hurt_type = None # 字符串 小伤害中伤害之类
        self.hurt_multiply = 1
        self.damage_list = self.init_damage_list.copy()

        self.is_over = False
        self.game:Game = None
        self.opponent:Character = None
        self.turn = 0

    def turn_stage(self):
        """
        回合开始 角色属性重置 技能回合数结算 选择本回合要激活的技能
        """
        self.turn = self.game.turn
        self.atk = self.base_atk
        self.hp = self.base_atk
        self.max_hp = self.base_max_hp

        self.tags = self.init_tags.copy()
        self.turn_win = False
        self.hurt_dice = 0
        self.hurt_type = None
        self.hurt_multiply = 1
        self.damage_list = self.init_damage_list.copy()

        self.base_queue.turn_stage()
        self.base_queue.deactivate_expired_skill()


    def hurt(self):
        """
        从基础受伤到调用修正区技能到掉血都有了
        """
        self.hurt_dice = random.randint(1, 100)

    def damage(self, message:Message):
        pass
class Game:
    def __init__(self, cha1: Character, cha2: Character):
        self.cha1 = cha1
        self.cha2 = cha2
        self.cha1.game = self
        self.cha2.game = self
        self.cha1.is_over = False
        self.cha2.is_over = False
        self.cha1.opponent = self.cha2
        self.cha2.opponent = self.cha1

        self.turn = 0
        self.is_over = False
        self.winner = '平局'
        self.attacker:Character = None # 拼点胜利者

        self.skill_queue = SkillQueue()
        self.dice_queue = SkillQueue()
        self.cha1_attack_queue = SkillQueue()
        self.cha2_attack_queue = SkillQueue()
        self.purchase_queue = SkillQueue()


    def check_over(self):
        """
        判断有一方是否已经输了
        用的是cha.is_over
        """
        if self.cha1.is_over or self.cha2.is_over:
            self.is_over = True
            self.winner = '平局'
            if self.cha1.is_over and not self.cha2.is_over:
                self.winner = self.cha2.name
            elif not self.cha1.is_over and self.cha2.is_over:
                self.winner = self.cha1.name
            return True # 胜负已分
        return False



    def start(self):
        while self.next_turn():
            pass
        return self.winner

    def next_turn(self):
        """
        进行一个回合 返回游戏是否应当继续
        当游戏结束时 应该设置self.winner
        """
        # TURN STAGE
        self.turn += 1
        logging.info(f'第{self.turn}回合开始')
        self.attacker = None
        self.cha1.turn_stage()
        self.cha2.turn_stage()

        # SKILL STAGE
        for it in self.skill_queue:
            it.execute()
        if self.check_over():
            return False # 回合中断

        # DICE STAGE
        # 判断是否有自动胜利 SKILL期技能如果有自动胜利会给自己设置turn_win
        if self.cha1.turn_win and not self.cha2.turn_win:
            self.attacker = self.cha1
        elif self.cha2.turn_win and not self.cha1.turn_win:
            self.attacker = self.cha2
        else:
            # 如果没有的话 攻击骰
            self.cha1.last_dice = random.randint(1, 100)
            self.cha2.last_dice = random.randint(1, 100)
            # 执行DICE期技能 修改战斗骰出目
            for it in self.dice_queue:
                it.execute()
            dice1 = self.cha1.last_dice+self.cha1.atk
            dice2 = self.cha2.last_dice+self.cha2.atk
            if dice1>dice2:
                self.attacker = self.cha1
            elif dice2>dice1:
                self.attacker = self.cha2
            else:
                self.attacker = None

        if self.attacker is not None:
            # 暂时的负方生成基础伤害 这一过程会直接走完整个流程 self.attacker也可能会修改
            self.attacker.opponent.hurt()
            if self.check_over():
                return False

        # PURSUIT STAGE
        for it in self.purchase_queue:
            it.execute()
        if self.check_over():
            return False
        return True