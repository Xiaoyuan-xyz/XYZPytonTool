"""
优先级

SkillGroup
    一般技能激活 0
    挂破解 -5
    核心是被动技能的技能激活 -10

SKILL
    挂跳过回合 -60
    【回合开始时】 -50
    破解所需值降低 -35
    获得特殊攻击耐性 -30
    骰子表修改 -30
    伤害表修改 -30
    挂被动 -30

    攻击力白值 HP上限乘算 -20
    攻击力白值 HP上限加算 -15
    攻击力乘算 -10
    攻击力增加 HP回复 -5
    攻击力最终结算 -2
    造成伤害 0

PASSIVE 对方技能宣言时 SPELL
    破解 0
PASSIVE 我方技能宣言后 SPELL_SELF
    制造偶像 -10
    发动技能时附加伤害 0
PASSIVE ATTACK
    受到技能伤害减少
INCREASE HURT/ATTACK
    伤害乘算 10
    伤害加算 20
    最终伤害乘算 30
REDUCTION HURT/ATTACK
    伤害乘算 10
    伤害加算 20
    最终伤害乘算 30
    最终伤害加算 40
    护甲 50
    【受到伤害时】 60
DAMAGE
PASSIVE 伤害判定结束后 DAMAGE_OVER
    【伤害结束后】 -50
PASSIVE 大成功或大失败 SOF


DICE
    战斗骰子修改 -10


Message的写法
技能宣言
Message('SPELL', skill) # 宣言完后会给自己发消息变成SPELL_SELF 供宣言者PASSIVE处理
技能宣言后
Message('SPELL_SELF', skill)
伤害
Message('DAMAGE', value) # 直接进DAMAGE阶段的【直接伤害】 value值不会变
受伤
Message('HURT', value) # 走伤害修正的攻击 走完伤害修正后会变成DAMAGE
技能攻击
Message('ATTACK', value, tags={'skill_attack': 1}) # 走PASSIVE MODIFIER DAMAGE 但是一般只吃PASSIVE的减伤效果 因为REDUCTION一般不管这个（除了护甲等）
Message('DAMAGE_OVER', value) # 伤害结束后 供攻击者PASSIVE处理
Message('SOF', value=dice) # 每次伤害骰子后会给对方发 COMPETE期技能会修改message 最后返回后会根据结果决定操作 如果不希望做任何事 可以把值修改为<=0

tags:
角色
    【自动胜利】 auto_win # 每回合重置
    【特殊攻击耐性】 resistance # 每回合重置
    【护甲】 armor
    偶像 haniwa
技能
    【无视减伤】 ignore_damage_reduction
    【无视破解】 uncounterattackable
    【技能伤害】 skill_attack
消息
    【破解】 counterattack
"""

import bisect
import heapq
import logging
import random


class Message:
    def __init__(self, kind, value=0, skill=None):
        self.kind = kind  # 消息类型 包括 SPELL SPELL_SELF ATTACK HURT DAMAGE DAMAGE_OVER
        self.value = value
        self.skill: SkillGroup = skill
        self.tags = {}


class SkillPriority:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


class SkillQueue:
    def __init__(self):
        self.queue: list[SkillPriority] = []

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

    def add_skill(self, skill: SkillPriority):
        bisect.insort(self.queue, skill)

    def remove_expired_functions(self):
        self.queue = [it for it in self.queue if not it.is_expired]

    def turn_stage(self):
        for it in self.queue:
            it: Function
            it.turn_stage()

    def get_highest_priority_skills(self) -> list[SkillPriority]:
        """
        获得最高优先级的所有技能
        """
        if len(self.queue) == 0:
            return []
        highest_priority = self.queue[0].priority
        highest_priority_skills: list[SkillPriority] = []
        for skill in self.queue:
            if skill.priority == highest_priority:
                highest_priority_skills.append(skill)
        return highest_priority_skills

    @staticmethod
    def merge_queue(queue1, queue2):
        """
        合并两个SkillQueue 并打乱同一优先级中的所有技能
        """
        queue = SkillQueue()
        queue.queue = list(heapq.merge(queue1.queue, queue2.queue))
        ret = []
        while True:
            highest_priority_skills = queue.get_highest_priority_skills()
            if len(highest_priority_skills) == 0:
                break
            random.shuffle(highest_priority_skills)
            ret.extend(highest_priority_skills)
            queue.queue = queue.queue[len(highest_priority_skills):]
        queue.queue = ret
        return queue


class SkillGroup(SkillPriority):
    """
    技能组
    在角色的turn_stage被激活 成功激活的技能会把自己的实现放到各技能列表中
    """

    def __init__(self, name, priority, next_turn, cooldown, functions, base_tags=None):
        super().__init__(name, priority)
        if base_tags is None:
            base_tags = {}
        self.next_turn = next_turn
        self.cooldown = cooldown
        self.functions: list[Function] = functions
        self.base_tags = base_tags
        self.tags = self.base_tags.copy()
        self.func_after_counterattack = None
        self.func_allow_activate = None
        self.owner: Character = None

    def activate(self):
        """
        宣言技能 将技能的实现放入相应列表中
        """
        logging.debug(f'{self.owner.name} {self.name} 激活')
        self.next_turn += self.cooldown
        self.tags = self.base_tags.copy()
        if self.func_allow_activate is not None and not self.func_allow_activate():
            return
        message = Message('SPELL', skill=self)
        self.owner.opponent.process_message(message)  # 【宣言时】
        message.kind = 'SPELL_SELF'
        self.owner.process_message(message)  # 【宣言后】
        if 'counterattack' in message.tags:
            if self.func_after_counterattack is not None:
                # ? 应该给有的Function一个标记 在破解后保留它
                self.func_after_counterattack()
        else:
            for it in self.functions:
                it.target.add_skill(it)


class Function(SkillPriority):
    def __init__(self, name, stage, priority, duration, target_is_owner=True, tags=None):
        super().__init__(name, priority)
        if tags is None:
            tags = {}
        self.stage = stage
        self.duration = duration
        self.remaining = duration
        self.lasting = 1
        self.tags = tags
        self.target_is_owner = target_is_owner
        self.is_expired = False
        self.target: Character = None  # 技能的作用对象 也就是技能在谁身上
        self.owner: Character = None  # 技能的发起者
        self.belongs_to: SkillGroup = None

    def turn_stage(self):
        self.remaining -= 1
        self.lasting += 1
        if self.remaining == 0:
            self.is_expired = True


class ActiveFunction(Function):
    def __init__(self, name, stage, priority, duration, apply_func, target_is_owner=True, tags=None):
        super().__init__(name, stage, priority, duration, target_is_owner, tags)
        self.apply_func = apply_func

    def apply(self):
        if self.stage in self.target.skip_stage:
            return
        self.apply_func(self)


class PassiveFunction(Function):
    def __init__(self, name, stage, priority, duration, process_func, target_is_owner=True, tags=None):
        super().__init__(name, stage, priority, duration, target_is_owner, tags)
        self.process_func = process_func

    def process(self, message: Message):
        if self.stage in self.target.skip_stage:
            return
        self.process_func(self, message)


class Character:
    def __init__(self, name, base_atk, base_hp, base_max_hp, base_tags=None):
        if base_tags is None:
            base_tags = {}
        self.name = name
        self.base_atk = base_atk
        self.base_hp = base_hp
        self.base_max_hp = base_max_hp
        self.base_tags = base_tags
        self.base_damage_list = {'回避': 10, '小伤害': 30, '中伤害': 50, '大伤害': 70, '特大伤害': 90, '大失败': 95,
                                 '大成功': 100}

        self.hp = self.base_hp
        self.max_hp = self.base_max_hp
        self.atk = self.base_atk
        self.tags = self.base_tags.copy()
        self.damage_list = self.base_damage_list.copy()
        self.last_dice = 0  # 上回合的战斗出目 每回合清空
        self.skip_stage = []  # 本回合要跳过的阶段 每回合清空
        self.hurt_multiplier = 1  # 基础伤害倍率 每回合清空
        self.turn = 0

        self.skills = SkillQueue()
        self.skill_queue = SkillQueue()
        self.passive_queue = SkillQueue()
        self.dice_queue = SkillQueue()
        self.compete_queue = SkillQueue()
        self.increase_queue = SkillQueue()
        self.reduction_queue = SkillQueue()
        self.pursuit_queue = SkillQueue()
        self.damage_queue = SkillQueue()

        self.opponent: Character = None
        self.game: Game = None
        self.is_dead = False

    def turn_stage(self):
        self.turn = self.game.turn
        self.atk = self.base_atk
        self.last_dice = 0
        self.skip_stage = []
        self.hurt_multiplier = 1
        self.damage_list = self.base_damage_list.copy()

        # ! 只有玩家的这些属性tag会被每回合清空
        self.tags.pop('resistance', None)
        self.tags.pop('auto_win', None)

        self.skill_queue.turn_stage()
        self.passive_queue.turn_stage()
        self.dice_queue.turn_stage()
        self.compete_queue.turn_stage()
        self.increase_queue.turn_stage()
        self.reduction_queue.turn_stage()
        self.pursuit_queue.turn_stage()
        self.damage_queue.turn_stage()

        self.skill_queue.remove_expired_functions()
        self.passive_queue.remove_expired_functions()
        self.dice_queue.remove_expired_functions()
        self.compete_queue.remove_expired_functions()
        self.increase_queue.remove_expired_functions()
        self.reduction_queue.remove_expired_functions()
        self.pursuit_queue.remove_expired_functions()
        self.damage_queue.remove_expired_functions()

        # 要激活的技能
        for skill in self.skills:
            skill: SkillGroup
            if skill.next_turn == self.turn:
                skill.activate()

    def hurt(self):
        """
        生成基础伤害 将基础伤害的出目发给对方 之后根据对方的修正判定 判定当前的最终受伤者 并受伤
        """
        dice = random.randint(1, 100)
        logging.debug(f'{self.name} 受伤骰 {dice}')
        message = Message('SOF', value=dice)
        logging.info(f'{self.name}的受伤骰子：{self.get_damage_name(dice)}')
        self.opponent.process_message(message)
        if dice != message.value:
            dice = message.value
            logging.info(f'{self.name}的受伤骰子：{self.get_damage_name(dice)}')
        damage_name = self.get_damage_name(dice)
        if damage_name == '回避':
            return
        if damage_name == '大成功':
            if self.hurt_multiplier > 1:
                self.hurt_multiplier //= 2
                self.hurt()
            else:
                self.opponent.hurt()
            return
        elif damage_name == '大失败':
            self.hurt_multiplier *= 2
            self.hurt()
            return
        elif damage_name == '无':
            return

        damage = Character.get_damage_from_name(damage_name) * self.hurt_multiplier
        message = Message('HURT', damage)
        self.process_message(message)

    def get_damage_name(self, dice):
        if 0 < dice <= self.damage_list['回避']:
            return '回避'
        elif self.damage_list['回避'] < dice <= self.damage_list['小伤害']:
            return '小伤害'
        elif self.damage_list['小伤害'] < dice <= self.damage_list['中伤害']:
            return '中伤害'
        elif self.damage_list['中伤害'] < dice <= self.damage_list['大伤害']:
            return '大伤害'
        elif self.damage_list['大伤害'] < dice <= self.damage_list['特大伤害']:
            return '特大伤害'
        elif self.damage_list['特大伤害'] < dice <= self.damage_list['大失败']:
            return '大失败'
        elif self.damage_list['大失败'] < dice <= self.damage_list['大成功']:
            return '大成功'
        return '无'

    @staticmethod
    def get_damage_from_name(name):
        if name == '小伤害':
            return 1
        elif name == '中伤害':
            return 2
        elif name == '大伤害':
            return 3
        elif name == '特大伤害':
            return 4
        else:
            return 0

    def register_skill(self, skill: SkillGroup):
        """
        将技能加入自己的基础技能组
        """
        skill.owner = self
        for function in skill.functions:
            function.belongs_to = skill
            function.owner = self
            function.target = self if function.target_is_owner else self.opponent
        self.skills.add_skill(skill)

    def add_skill(self, skill: Function):
        """
        将功能加入角色的技能列表
        """
        if skill.stage == 'SKILL':
            self.skill_queue.add_skill(skill)
        elif skill.stage == 'PASSIVE':
            self.passive_queue.add_skill(skill)
        elif skill.stage == 'DICE':
            self.dice_queue.add_skill(skill)
        elif skill.stage == 'COMPETE':
            self.compete_queue.add_skill(skill)
        elif skill.stage == 'INCREASE':
            self.increase_queue.add_skill(skill)
        elif skill.stage == 'REDUCTION':
            self.reduction_queue.add_skill(skill)
        elif skill.stage == 'PURSUIT':
            self.pursuit_queue.add_skill(skill)
        elif skill.stage == 'DAMAGE':
            self.damage_queue.add_skill(skill)
        else:
            logging.debug(f'未知的技能阶段：{skill.stage}')

    def process_message(self, message):
        """
        调用被动技能处理消息
        SPELL SPELL_SELF -> passive
        ATTACK -> passive, modifier -> DAMAGE
        HURT -> modifier -> DAMAGE
        DAMAGE -> damage -> DAMAGE_OVER
        DAMAGE_OVER -> passive
        SOF -> compete
        """
        if message.kind == 'SPELL' or message.kind == 'SPELL_SELF' or message.kind == 'ATTACK' or message.kind == 'DAMAGE_OVER':
            for function in self.passive_queue:
                function: PassiveFunction
                function.process(message)
        if message.kind == 'ATTACK' or message.kind == 'HURT':
            modifier_queue = SkillQueue.merge_queue(self.reduction_queue, self.opponent.increase_queue)
            for function in modifier_queue:
                function: PassiveFunction
                function.process(message)
            if message.value > 0:
                message.kind = 'DAMAGE'
                self.process_message(message)
            return
        if message.kind == 'DAMAGE':
            if message.value > 0:
                self.hp -= message.value
                logging.info(f'{self.name} 受到伤害 {message.value} 剩余血量 {self.hp}')
                for function in self.damage_queue:
                    function: PassiveFunction
                    function.process(message)
                if self.hp <= 0:
                    self.is_dead = True
                message.kind = 'DAMAGE_OVER'
                self.opponent.process_message(message)
                return
        if message.kind == 'SOF':
            for function in self.compete_queue:
                function: PassiveFunction
                function.process(message)


class Game:
    def __init__(self, cha1: Character, cha2: Character):
        self.cha1 = cha1
        self.cha2 = cha2
        self.cha1.game = self
        self.cha2.game = self
        self.cha1.opponent = self.cha2
        self.cha2.opponent = self.cha1

        self.turn = 0
        self.is_over = False
        self.winner = '平局'

    def check_over(self):
        """
        判断有一方是否已经输了
        用的是cha.is_dead
        """
        if self.cha1.is_dead or self.cha2.is_dead:
            self.is_over = True
            self.winner = '平局'
            if self.cha1.is_dead and not self.cha2.is_dead:
                self.winner = self.cha2.name
                logging.info(f'{self.cha1.name} 战斗不能')
            elif not self.cha1.is_dead and self.cha2.is_dead:
                self.winner = self.cha1.name
                logging.info(f'{self.cha2.name} 战斗不能')

    def start(self):
        while self.next_turn():
            pass

    def next_turn(self):
        self.turn_stage()
        self.skill_stage()
        if self.is_over:
            return False

        # 如果有一方跳过了DICE技能阶段 也认为对方胜利
        if 'DICE' in self.cha1.skip_stage and 'DICE' in self.cha2.skip_stage:
            defender = None
        elif 'DICE' in self.cha1.skip_stage:
            defender = self.cha1
        elif 'DICE' in self.cha2.skip_stage:
            defender = self.cha2
        # 判断是否有自动胜利 SKILL期技能如果有自动胜利会给自己设置turn_win
        elif 'auto_win' in self.cha1.tags and 'auto_win' not in self.cha2.tags:
            defender = self.cha2
        elif 'auto_win' in self.cha2.tags and 'auto_win' not in self.cha1.tags:
            defender = self.cha1
        # 双方都auto_win的场合 或双方都没有auto_win的场合 正常走攻击骰
        else:
            dice1 = random.randint(1, 100)
            dice2 = random.randint(1, 100)
            self.cha1.last_dice = dice1
            self.cha2.last_dice = dice2
            logging.debug(
                f'{self.cha1.name} 出目 {self.cha1.last_dice}+{self.cha1.atk}={self.cha1.last_dice + self.cha1.atk} '
                f'{self.cha2.name} 出目 {self.cha2.last_dice}+{self.cha2.atk}={self.cha2.last_dice + self.cha2.atk}')
            self.dice_stage()
            logging.info(
                f'{self.cha1.name} 出目 {self.cha1.last_dice}+{self.cha1.atk}={self.cha1.last_dice + self.cha1.atk} '
                f'{self.cha2.name} 出目 {self.cha2.last_dice}+{self.cha2.atk}={self.cha2.last_dice + self.cha2.atk}')
            dice1 = self.cha1.last_dice + self.cha1.atk
            dice2 = self.cha2.last_dice + self.cha2.atk

            if dice1 > dice2:
                logging.info(f'{self.cha1.name} 取得攻击机会')
                defender = self.cha2
            elif dice1 < dice2:
                logging.info(f'{self.cha2.name} 取得攻击机会')
                defender = self.cha1
            else:
                logging.info(f'双方平手')
                defender = None

        if defender is not None:
            defender.hurt()
            self.check_over()
            if self.is_over:
                return False

        self.pursuit_stage()
        if self.is_over:
            return False

        logging.info(
            f'{self.cha1.name} hp={self.cha1.hp}/{self.cha1.max_hp} {self.cha2.name} hp={self.cha2.hp}/{self.cha2.max_hp}')
        return True

    def turn_stage(self):
        """
        回合数+1 角色进入TURN STAGE
        """
        self.turn += 1
        logging.info(f'===== 当前回合数 {self.turn} =========================')
        self.cha1.turn_stage()
        self.cha2.turn_stage()

    def skill_stage(self):
        """
        遍历双方的SKILL期技能 如果某个技能结束后有角色死亡 则中断
        """
        skill_queue = SkillQueue.merge_queue(self.cha1.skill_queue, self.cha2.skill_queue)
        for skill in skill_queue:
            skill: ActiveFunction
            skill.apply()
            self.check_over()
            if self.is_over:
                return

    def dice_stage(self):
        """
        遍历双方的DICE期技能
        """
        skill_queue = SkillQueue.merge_queue(self.cha1.dice_queue, self.cha2.dice_queue)
        for skill in skill_queue:
            skill: ActiveFunction
            skill.apply()

    def pursuit_stage(self):
        """
        遍历双方的PURSUIT期技能 如果某个技能结束后有角色死亡 则中断
        """
        skill_queue = SkillQueue.merge_queue(self.cha1.pursuit_queue, self.cha2.pursuit_queue)
        for skill in skill_queue:
            skill: ActiveFunction
            skill.apply()
            self.check_over()
            if self.is_over:
                return
