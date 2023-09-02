import logging

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


# ! 被动能力
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



# ! modifier期
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

