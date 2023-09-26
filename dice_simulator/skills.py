import logging
import random
import re

from dice_simulator import ActiveFunction, PassiveFunction, Message


class Priority:
    # ! SkillGroup
    # 被动技能组 例如那些第一回合要破解的
    SG_PASSIVE = -10
    # 破解技能 挂破解的技能都是不可破解的
    SG_COUNTERATTACK = -5
    SG_ACTIVE = 0

    # ! SKILL
    TURN_START = -50  # 回合开始时
    RESISTANCE = -30
    TABLE = -30  # 修改damage_list
    ATK_MULTIPLY = -10  # 攻击力乘算
    ATK_ADDITION = -5  # 攻击力加算
    ATK_FINAL = -2  # 攻击力最终计算 如：对方的最终攻击力不超过己方
    ATTACK = 0  # 一般的攻击

    # ! INCREASE/REDUCTION
    DAMAGE_MULTIPLY = 10  # 伤害乘算
    DAMAGE_ADDITION = 20  # 伤害加算
    FINAL_DAMAGE_MULTIPLY = 30  # 最终伤害乘算 如：最终伤害减半
    SHIELD = 50  # 护甲
    WHEN_DAMAGE = 60  # 受到伤害前

    # ! DICE
    DICE = 0

    # ! PASSIVE SPELL
    COUNTERATTACK = 0 # 破解技能


# ? 攻击力乘
class AtkIncrease(ActiveFunction):
    def __init__(self, times, duration=999):
        self.times = times
        super().__init__(f'攻击力乘{self.times}', 'SKILL', Priority.ATK_MULTIPLY, duration)

    def apply_inner(self):
        target = self.owner
        target.atk = int(target.atk * self.times)

# ? 对手攻击力乘
class AtkDecrease(ActiveFunction):
    def __init__(self, times, duration=999):
        self.times = times
        super().__init__(f'对手攻击力乘{self.times}', 'SKILL', Priority.ATK_MULTIPLY, duration)

    def apply_inner(self):
        opponent = self.owner.opponent
        opponent.atk = int(opponent.atk * self.times)

# ? 攻击力加
class AtkAddition(ActiveFunction):
    def __init__(self, value:int, duration=999):
        self.value = value
        super().__init__(f'攻击力加{self.value}', 'SKILL', Priority.ATK_ADDITION, duration)

    def apply_inner(self):
        target = self.owner
        target.atk = int(target.atk + self.value)

# ? 对手攻击力减
class AtkSubtraction(ActiveFunction):
    def __init__(self, value:int, duration=999):
        self.value = value
        super().__init__(f'对手攻击力减{self.value}', 'SKILL', Priority.ATK_ADDITION, duration)

    def apply_inner(self):
        opponent = self.owner.opponent
        opponent.atk = int(opponent.atk - self.value)

# ? 回避率乘
class AvoidIncrease(ActiveFunction):
    def __init__(self, times, duration):
        self.times = times
        super().__init__(f'回避率乘{self.times}', 'SKILL', Priority.TABLE, duration)

    def apply_inner(self):
        target = self.target
        target.damage_list['回避'] = int(target.damage_list['回避'] * self.times)

# ? 对手回避率乘
class AvoidDecrease(ActiveFunction):
    def __init__(self, times, duration):
        self.times = times
        super().__init__(f'对手回避率乘{self.times}', 'SKILL', Priority.TABLE, duration)

    def apply_inner(self):
        opponent = self.owner.opponent
        opponent.damage_list['回避'] = int(opponent.damage_list['回避'] * self.times)

# ? 获得特殊攻击耐性
class Resistance(ActiveFunction):
    def __init__(self, duration):
        super().__init__('获得特殊攻击耐性', 'SKILL', Priority.RESISTANCE, duration)

    def apply_inner(self):
        logging.debug(f'{self.target.name} 获得【特殊攻击耐性】')
        target = self.target
        target.tags["resistance"] = 1

# ? 修改战斗骰
class FightDice(ActiveFunction):
    def __init__(self, dice_expr, duration):
        self.dice_expr = dice_expr
        super().__init__(f'修改战斗骰为：{dice_expr}', 'DICE', Priority.DICE, duration)

    def apply_inner(self):
        match = re.match(r'(\d+)d(\d+)', self.dice_expr)
        m = int(match.group(1))
        n = int(match.group(2))
        dice = sum(random.randint(1, n) for _ in range(m))
        target = self.target
        target.last_dice = dice
        logging.debug(f'{self.target.name} 修改战斗骰为 {self.dice_expr}={dice}')

# ? 拼点攻击伤害乘
class DamageIncrease(PassiveFunction):
    def __init__(self, times:int, duration:int):
        self.times = times
        super().__init__(f'造成伤害乘{self.times}', 'INCREASE', Priority.DAMAGE_MULTIPLY, duration)

    def process_inner(self, message:Message):
        if message.kind == 'HURT':
            logging.debug(f'{self.belongs_to.name} 使伤害{message.value}×{self.times}={int(message.value * self.times)}')
            message.value = int(message.value * self.times)

# ? 拼点受伤伤害乘
class DamageDecrease(PassiveFunction):
    def __init__(self, times, duration:int):
        self.times = times
        super().__init__(f'受到伤害乘{self.times}', 'REDUCTION', Priority.DAMAGE_MULTIPLY, duration)

    def process_inner(self, message:Message):
        if message.kind == 'HURT' and 'ignore_damage_reduction' not in message.tags:
            logging.debug(f'{self.belongs_to.name} 使伤害{message.value}×{self.times}={int(message.value * self.times)}')
            message.value = int(message.value * self.times)


# ? 拼点造成伤害加
class DamageAddition(PassiveFunction):
    def __init__(self, value, duration:int):
        self.value = value
        super().__init__(f'造成伤害加{self.value}', 'INCREASE', Priority.DAMAGE_ADDITION, duration)

    def process_inner(self, message:Message):
        if message.kind == 'HURT':
            logging.debug(f'{self.belongs_to.name} 使伤害{message.value}+{self.value}={int(message.value + self.value)}')
            message.value = int(message.value + self.value)

# ? 拼点受到伤害减
class DamageSubtraction(PassiveFunction):
    def __init__(self, value, duration:int):
        self.value = value
        super().__init__(f'受到伤害减{self.value}', 'REDUCTION', Priority.DAMAGE_ADDITION, duration)

    def process_inner(self, message:Message):
        if message.kind == 'HURT' and 'ignore_damage_reduction' not in message.tags:
            logging.debug(f'{self.belongs_to.name} 使伤害{message.value}-{self.value}={int(message.value - self.value)}')
            message.value = int(message.value - self.value)

# ? 最终受到伤害乘
class FinalDamageDecrease(PassiveFunction):
    def __init__(self, times, kinds, tags, duration:int):
        self.times = times
        self.check_kinds = kinds
        self.check_tags = tags
        super().__init__(f'受到最终伤害乘{self.times}', 'REDUCTION', Priority.FINAL_DAMAGE_MULTIPLY, duration)

    def process_inner(self, message:Message):
        if 'ignore_damage_reduction' in message.tags:
            return
        if message.kind in self.check_kinds and bool(set(message.tags.keys()) & set(self.check_tags.keys())):
            logging.debug(f'{self.belongs_to.name} 使最终伤害{message.value}×{self.times}={int(message.value * self.times)}')
            message.value = int(message.value * self.times)

# ? 宣言破解
class Counterattack(PassiveFunction):
    def __init__(self, tags_and_verdict, duration, same_verdict:int=None, allow_ultra=False, force_counterattack=False):
        self.allow_ultra = allow_ultra
        self.check_tags = tags_and_verdict
        self.same_verdict = same_verdict
        self.force_counterattack = force_counterattack
        super().__init__(f'破解技能', 'PASSIVE', Priority.FINAL_DAMAGE_MULTIPLY, duration)

    def process_inner(self, message:Message):
        if message.kind != 'SPELL':
            return
        s = message.skill
        if not self.allow_ultra and 'ultra' in s.tags:
            return
        intersection_tags = set(s.tags.keys()) & set(self.check_tags.keys())
        if bool(intersection_tags) or 'all' in self.check_tags:
            if not self.force_counterattack and 'uncounterattackable' in s.tags:
                dice = random.randint(1, 100)
                if self.same_verdict == None:
                    verdict = self.check_tags[next(iter(intersection_tags))]
                else:
                    verdict = self.same_verdict
                target = self.target
                verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
                verdict_offset_from_skill = 0 if 'verdict_offset' not in s.tags else s.tags['verdict_offset']
                verdict += verdict_offset_from_owner + verdict_offset_from_skill
                result = dice > verdict
                if dice > verdict:
                    message.tags['counterattack'] = 1
                logging.info(f"{self.belongs_to.name}发动 出目是{dice}/{verdict} 判定{'成功' if result else '失败'}")

