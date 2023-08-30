"""
每一回合要做的事：
1. 回合数变更阶段 TURN STAGE
- 当前回合数+1
- 角色属性重置 技能持续时间计算 调用clean()
    - 攻击力重置
    - 所有技能列表（后述）中的技能调用update_remaining() 使remaining-1
    - 清除所有技能列表中的remaining=0的技能
    - 更新基础技能列表中的技能状态 重置remaining和next_turn
- 激活技能
    - 检查所有已激活的技能是否在对应的技能列表中
    - 遍历所有可以激活的技能 找到不冲突的 可以激活的所有技能
    - 激活它们 设置它们的active=True
    - 将被激活的技能放入相应的列表中
2. 准备阶段 SKILL STAGE
- 释放技能
    - 释放主动技能 两人的技能是混合释放的
    - 向对方发送主动技能释放消息 对方遍历被动技能 这个时期的技能记作spell
    - 根据返回结果 决定是否释放主动技能
3. 拼点阶段 DICE STAGE
- 取得随机数 应用拼点阶段的主动技能
- 应用拼点阶段的被动技能 COMPETE
    - 将自己的出目发送给对方
    - 接收对方的出目 调用COMPETE阶段的SKILL
    - 两者谁先谁后随机决定（或许应该由优先级决定？）
4. 被动技能阶段 MODIFIER
- 令负方产生基础伤害
    - 负方调用base_damage() 产生基础伤害message
- 胜方调用增伤的技能INCREASE 负方调用减伤REDUCTION的技能
    - 从合并技能库里 调用这两阶段的SKILL
5. 伤害阶段 DAMAGE STAGE
- 负方血量下降
    - 调用hp_change() 降低血量
6. 结算阶段 ENDING STAGE
- 调用ENDING阶段技能

下面枚举各个属性
STAGE：
    - SKILL
    - PASSIVE
    - DICE
    - COMPETE
    - INCREASE
    - REDUCTION
    - DAMAGE
    - ENDING

tag
    - normal 默认的 普通攻击
    - danmaku 弹幕攻击
    - melee 近战
    - technique 技巧系
    - ultra 必杀技

优先级
    主动技能：
    -25 白值操作
    -20 攻击力乘算
    -15 攻击力加算
    -10 一般的技能

    MODIFIER被动技能：
    -20 增伤乘算
    -15 增伤加算
    10 减伤乘算
    15 减伤加算
    20 最终伤害乘算

技能持续时间类型
    首发回合1 持续时间999 冷却时间0 这是默认值
        这种一般是常态的buff 比如攻击力*2之类的
        也有可能是第一回合注册的被动技能
        这是默认的配置
    首发回合5 持续时间1 冷却时间5 one_turn_skill(turn=-99)
        这种一般是当回合生效的主动技能 一般是攻击类的
    首发回合5 持续时间3 冷却时间5
        一般的带buff的主动技能
    首发回合2 持续时间1 冷却时间999 one_off_skill(turn)
        一次性技能
    首发回合-99 持续时间1 冷却时间-99 one_turn_skill(turn=-99)
        一般是主动技能附带的被动技能 从持续时间里看不出技能持续时间 每个新回合都会由主动技能赋予
        也可以在主动技能第一回合里生成持续时间等于技能持续时间的技能 这只是写法的不同

下面举一些技能的例子
烈 海 王：海王是中华武术的巅峰，烈海王又是其中佼佼者，凭借高超的技术使战斗力X1.8
阶段SKILL 优先级-20 首发回合1 持续时间999 冷却时间0 标签无：攻击力=攻击力白值*1.8
阶段SKILL 优先级-20 首发回合1 持续时间1 冷却时间999 标签无：攻击力白值*1.8 （或者）

消力：传自郭海皇的绝学，普通攻击以及近战系技能所造成的的最终伤害/2
阶段REDUCTION 优先级20 首发回合1 持续时间999 冷却时间0 标签无：normal/melee 伤害/2

假腿断裂：肢体缺失导致HP-2，Atk-10（吃到了美味的晚餐，断裂后的伤害减轻了）
阶段SKILL 优先级-15 首发回合1 持续时间1 冷却时间999 标签无：攻击力白值-10 生命值-2

四千年的传承：不会陷入异常状态，面对近战系、技术系的技能可以进行【1d100】的破解判定，75以上成功
阶段PASSIVE 优先级-10 首发回合1 持续时间999 冷却时间0 标签无：对melee spell和technique spell 无效化其技能

武之怀（CT5）：3T内Atk+60。3T内可对所有攻击进行【1d100】的破解判定，普通攻击与近战系、技巧系技能30以上成功，其余技能50以上成功，必杀技75以上成功。
阶段SKILL 优先级-10 首发回合5 持续时间3 冷却时间5 标签无： 攻击力白值+60 添加如下技能
阶段REDUCTION 优先级10 持续时间1 标签无： 对normal melee technique 其他技能 分别以70% 70% 25% 50% 使之伤害归0

极光「华严明星」（CT4）：（弹幕系）将七色的巨大气弹精炼后，向敌人打出，对对手造成【1d4】的伤害
阶段SKILL 优先级-10 首发回合4 持续时间1 冷却时间4 标签无： 调用对方的hp_change()方法 减少1d4的生命值

Flower Shooting（CT3）：（弹幕类）同时发出五个方向的大范围花弹，对对手造成必中的【1+1d4】点伤害。由于对幽香来说只是随手放出的小技能，因此CT较低
阶段SKILL 优先级-10 首发回合3 持续时间1 冷却时间3 标签无： 调用对方的hp_change()方法 减少1+1d4的生命值



"""
import heapq
import logging
import random

import tqdm


class Skill:
    def __init__(self, name, stage, priority, turn=1, duration=999, cooldown=0, tag='normal', exclusive=False,
                 active=False, owner=None, apply_func=None, trigger_func=None, process_func=None):
        self.name = name  # 技能名
        self.stage = stage  # 阶段
        self.priority = priority  # 优先级
        self.turn = turn  # 首发回合
        self.next_turn = turn  # 下次触发回合
        self.duration = duration  # 持续时间
        self.remaining = duration  # 技能的剩余时间
        self.cooldown = cooldown  # 冷却时间
        self.tag = tag  # 类型
        self.exclusive = exclusive  # 它激活时是否其他技能不能激活
        self.active = active  # 是否激活
        self.owner: Character = owner
        self.apply_func = apply_func  # 主动技能 ! 无返回
        self.trigger_func = trigger_func  # 被动技能触发条件 ! 返回是否触发
        self.process_func = process_func  # 被动技能 ! 返回是否使产生信息的来源主动技能无效 返回True也意味着更低优先级的技能不再使用 一般只有PASSIVE期技能会返回True

    def __lt__(self, other):
        return self.priority < other.priority

    def update_remaining(self):
        self.remaining -= 1

    def apply(self):
        if self.apply_func is None:
            return
        logging.debug(f'{self.owner.name} 调用了主动技能 {self.name}')
        self.apply_func(self)

    def process_message(self, message):
        if self.trigger(message):
            if self.process_func is None:
                return False
            logging.info(f'{self.owner.name} 触发了被动技能 {self.name}')
            return self.process_func(self, message)

    def trigger(self, message) -> bool:
        if self.trigger_func is None:
            return False
        return self.trigger_func(self, message)

    def one_turn_skill(self, turn=-99):
        self.turn = turn
        self.next_turn = turn
        self.duration = 1
        self.remaining = 1
        self.cooldown = turn
        return self

    def one_off_skill(self, turn):
        self.turn = turn
        self.next_turn = turn
        self.duration = 1
        self.remaining = 1
        self.cooldown = 999
        return self

    def ultra(self):
        self.tag = 'ultra'
        return self

    def exclusive_skill(self):
        self.exclusive = True
        return self

    def technique(self):
        self.tag = 'technique'
        return self


class SkillQueue:
    def __init__(self, owner=None):
        self.queue: list[Skill] = []
        self.owner: Character = owner

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
        if self.owner is not None:
            skill.owner = self.owner
        heapq.heappush(self.queue, skill)

    def remove_expired_skills(self):
        """
        移除队列中remaining==0的技能
        """
        self.queue = [it for it in self.queue if it.remaining != 0]

    def deactivate_expired_skills(self):
        """
        将队列中remaining==0的技能撤销激活 并重置remaining和next_turn
        """
        for it in self.queue:
            if it.remaining == 0:
                it.active = False
                it.remaining = it.duration
                it.next_turn += it.cooldown

    def update_remaining(self):
        for it in self.queue:
            if it.active:
                it.update_remaining()

    def get_highest_priority_skills(self) -> list[Skill]:
        """
        获得最高优先级的所有技能
        """
        if len(self.queue) == 0:
            return []
        highest_priority = self.queue[0].priority
        highest_priority_skills: list[Skill] = []
        for skill in self.queue:
            if skill.priority == highest_priority:
                highest_priority_skills.append(skill)
        return highest_priority_skills

    def find_skill_to_activate(self, now_turn):
        """
        寻找所有本回合该激活的技能 在所有独占技能中随机选择一个激活 其余技能激活 并把激活了的技能放到技能列表中
        """
        for skill in self.queue:
            # 已激活的技能 但不在该列表中 则重新放入
            if skill.active and skill not in self.owner.stage_to_queue(skill.stage):
                self.owner.stage_to_queue(skill.stage).add_skill(skill)

        skills_could_activate: list[Skill] = []
        for skill in self.queue:
            # 本回合可能要激活的技能
            if not skill.active and skill.next_turn == now_turn:
                skills_could_activate.append(skill)

        if len(skills_could_activate) == 0:
            return
        exclusive_skills = SkillQueue(self.owner)
        for skill in skills_could_activate:
            # 要激活技能里的独占技能
            if skill.exclusive:
                exclusive_skills.add_skill(skill)
        if len(exclusive_skills) != 0:
            for skill in exclusive_skills:
                skills_could_activate.remove(skill)
            # 随机挑选一个最优先技能
            highest_priority_skills = exclusive_skills.get_highest_priority_skills()
            exclusive_skill: Skill = random.choice(highest_priority_skills)
            exclusive_skills.queue.remove(exclusive_skill)
            self.owner.activate_skill(exclusive_skill)
            logging.debug(f'{self.owner.name} 激活了技能 {exclusive_skill.name}')
            # 其余技能延迟到下一回合
            for skill in exclusive_skills:
                skill.next_turn += 1
            if len(exclusive_skills) > 0:
                logging.debug(f'{"、".join([it.name for it in exclusive_skills])} 延迟到下一回合')
        # 激活非独占技能 一般是在第一回合激活的被动技能
        for skill in skills_could_activate:
            self.owner.activate_skill(skill)
            logging.debug(f'{self.owner.name} 激活了技能 {skill.name}')


class Message:
    def __init__(self, stage, tag, value, src, dest, skill=None):
        self.stage = stage
        self.tag = tag
        self.value = value
        self.src = src
        self.dest = dest
        self.skill = skill


class Character:
    def __init__(self, name, base_atk, base_hp, base_skill=None):
        self.name = name
        self.base_atk = base_atk  # 攻击力白值
        self.base_hp = base_hp  # 最大生命值
        if base_skill is None:  # 基础技能组
            base_skill = SkillQueue(self)
        self.base_skill = base_skill
        self.atk = base_atk
        self.hp = base_hp
        self.game = None
        self.rival: Character | None = None
        self.last_dice = 0  # 上次攻击出目
        self.tag = 'normal'  # 攻击类型 用于MODIFIER阶段

        self.skill_queue = SkillQueue(self)
        self.passive_queue = SkillQueue(self)
        self.dice_queue = SkillQueue(self)
        self.compete_queue = SkillQueue(self)
        self.increase_queue = SkillQueue(self)
        self.reduction_queue = SkillQueue(self)
        self.damage_queue = SkillQueue(self)
        self.ending_queue = SkillQueue(self)

        self._queue_map = {"SKILL": self.skill_queue, "PASSIVE": self.passive_queue, "DICE": self.dice_queue,
                           "COMPETE": self.compete_queue, "INCREASE": self.increase_queue,
                           "REDUCTION": self.reduction_queue,
                           "DAMAGE": self.damage_queue, "ENDING": self.ending_queue, }
        self.queues = self._queue_map.values()

        self.base_dice_to_name = {1: "回避", 2: "小伤害", 3: "小伤害", 4: "中伤害", 5: "中伤害", 6: "中伤害",
                                  7: "大伤害", 8: "大伤害", 9: "特大伤害", 10: "大成功/大失败", }
        self.base_name_to_damage = {"回避": 0, "小伤害": 1, "中伤害": 2, "大伤害": 3, "特大伤害": 4, }
        self.dice_to_name = self.base_dice_to_name
        self.name_to_damage = self.base_name_to_damage

    def refresh(self):
        """
        回满血 清空所有技能
        """
        self.hp = self.base_hp
        self.skill_queue = SkillQueue(self)
        self.passive_queue = SkillQueue(self)
        self.dice_queue = SkillQueue(self)
        self.compete_queue = SkillQueue(self)
        self.increase_queue = SkillQueue(self)
        self.reduction_queue = SkillQueue(self)
        self.damage_queue = SkillQueue(self)
        self.ending_queue = SkillQueue(self)
        self._queue_map = {"SKILL": self.skill_queue, "PASSIVE": self.passive_queue, "DICE": self.dice_queue,
                           "COMPETE": self.compete_queue, "INCREASE": self.increase_queue,
                           "REDUCTION": self.reduction_queue,
                           "DAMAGE": self.damage_queue, "ENDING": self.ending_queue, }
        self.queues = self._queue_map.values()

    def stage_to_queue(self, stage: str):
        """
        输入阶段字符串 返回对应的技能列表
        """
        queue = self._queue_map[stage]
        queue: SkillQueue
        return queue

    def clean(self):
        """
        基础攻击重置 各技能列表更新 基础技能组更新
        """
        self.atk = self.base_atk
        self.dice_to_name = self.base_dice_to_name
        self.name_to_damage = self.base_name_to_damage
        self.tag = 'normal'
        for queue in self.queues:
            queue.update_remaining()
            queue.remove_expired_skills()
        # self.base_skill.update_remaining()
        self.base_skill.deactivate_expired_skills()

    def add_skill(self, skill):
        """
        给基本技能组追加技能
        """
        skill.owner = self
        self.base_skill.add_skill(skill)

    def activate_skill(self, skill: Skill):
        """
        激活技能 将它加入对应的技能列表
        """
        assert skill.owner == self
        skill.active = True
        self.stage_to_queue(skill.stage).add_skill(skill)

    def process_message(self, message: Message):
        """
        根据消息的类型让对应的技能列表处理消息
        """
        stage = message.stage
        ret = False
        for skill in self.stage_to_queue(stage):
            ret = skill.process_message(message)
            if ret:
                break
        return ret

    def dice_stage(self):
        """
        获取攻击出目 并调用自身的DICE技能 返回出目和攻击力
        """
        self.last_dice = random.randint(1, 100)
        for skill in self.dice_queue:
            skill.apply()
        return self.last_dice, self.atk

    def base_damage(self):
        """
        被攻击时 基础出目 返回是否正常伤害和MODIFIER期消息
        """
        damage_multiplier = 1
        while True:
            dice = random.randint(1, 10)
            if dice < 10:
                break
            if random.randint(0, 1):
                logging.info(f'{self.name} 大失败 基础伤害翻倍')
                damage_multiplier *= 2
            elif damage_multiplier >= 2:
                logging.info(f'{self.name} 大成功 基础伤害减半')
                damage_multiplier //= 2
            else:
                logging.info(f'{self.name} 大成功 取得反击机会')
                return False, None  # 表示攻守交换
        name = self.dice_to_name[dice]
        damage = self.name_to_damage[name]
        damage *= damage_multiplier
        logging.info(f'{self.name} 受到攻击 出目{dice} {name}x{damage_multiplier}={damage}')
        message = Message('MODIFIER', self.tag, damage, self, self.rival)
        return True, message

    def hp_change(self, message):
        """
        减少生命值 并调用damage期技能
        """
        self.hp -= message.value
        self.process_message(message)
        if message.value != 0:
            logging.info(f'{self.name} 受到伤害{self.hp + message.value}-{message.value}={self.hp}')


class Game:
    def __init__(self, cha1, cha2):
        self.cha1: Character = cha1
        self.cha2: Character = cha2
        self.cha1.game = self
        self.cha2.game = self
        self.cha1.rival = cha2
        self.cha2.rival = cha1
        self.turn = 0
        self.winner = "平局"

    @staticmethod
    def merge_queue(queue1, queue2):
        """
        合并对战双方的某一阶段技能 并打乱同一优先级中的所有技能
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
        return ret

    def next_turn(self):
        # TURN STAGE
        self.turn += 1
        logging.info(f'第{self.turn}回合开始')
        self.cha1.clean()
        self.cha2.clean()
        self.cha1.base_skill.find_skill_to_activate(now_turn=self.turn)
        self.cha2.base_skill.find_skill_to_activate(now_turn=self.turn)

        # SKILL STAGE
        skill_queue = self.merge_queue(self.cha1.skill_queue, self.cha2.skill_queue)
        for skill in skill_queue:
            logging.debug(f'{skill.owner.name} 宣言 {skill.name}')
            message = Message('PASSIVE', skill.tag, 0, skill.owner, skill.owner.rival)
            ret = skill.owner.rival.process_message(message)
            if not ret:
                skill.apply()

        if self.cha1.hp <= 0 or self.cha2.hp <= 0:
            if self.cha1.hp > 0:
                self.winner = self.cha1.name
            if self.cha2.hp > 0:
                self.winner = self.cha2.name
            return False

        # DICE STAGE
        self.cha1.dice_stage()
        self.cha2.dice_stage()
        message1 = Message("COMPETE", None, (self.cha1.last_dice, self.cha1.atk), self.cha1, self.cha2)
        message2 = Message("COMPETE", None, (self.cha2.last_dice, self.cha2.atk), self.cha2, self.cha1)
        if random.randint(0, 1):
            self.cha2.process_message(message1)
            self.cha1.process_message(message2)
        else:
            self.cha1.process_message(message2)
            self.cha2.process_message(message1)

        final_atk1 = sum(message1.value)
        final_atk2 = sum(message2.value)
        logging.info(f'{self.cha1.name} 出目 {message1.value[1]}+{message1.value[0]}={final_atk1}, '
                     f'{self.cha2.name} 出目 {message2.value[1]}+{message2.value[0]}={final_atk2}')
        if final_atk1 == final_atk2:
            logging.info(f'旗鼓相当的出目')
        else:
            attacker = self.cha1 if final_atk1 > final_atk2 else self.cha2
            defender = self.cha2 if final_atk1 > final_atk2 else self.cha1
            while True:
                logging.info(f'{attacker.name} 取得攻击机会')
                flag, message = defender.base_damage()
                if flag:
                    modifier_queue = self.merge_queue(attacker.increase_queue, defender.reduction_queue)
                    for skill in modifier_queue:
                        ret = skill.process_message(message)
                        if ret:
                            break
                    break
                attacker, defender = defender, attacker

            # DAMAGE_STAGE
            message.stage = 'DAMAGE'
            defender.hp_change(message)

        if self.cha1.hp <= 0 or self.cha2.hp <= 0:
            if self.cha1.hp > 0:
                self.winner = self.cha1.name
            if self.cha2.hp > 0:
                self.winner = self.cha2.name
            return False

        # ENDING STAGE
        skill_queue = self.merge_queue(self.cha1.ending_queue, self.cha2.ending_queue)
        for skill in skill_queue:
            skill.apply()

        logging.debug(f'{self.cha1.name} 的 hp：{self.cha1.hp}/{self.cha1.base_hp} '
                      f'{self.cha2.name} 的 hp：{self.cha2.hp}/{self.cha2.base_hp}')

        return True

    def start_game(self):
        self.turn = 0
        self.winner = None
        while self.next_turn():
            pass
        logging.info(f'{self.winner} 胜利')


if __name__ == '__main__':

    random.seed(42)

    logging.basicConfig(level=logging.WARN)
    result = {"烈海王": 0, "红美铃": 0, None: 0}
    for i in tqdm.tqdm(range(10000)):
        r = Character('烈海王', 80, 15)
        m = Character('红美铃', 100, 15)


        # ! 烈 海 王：海王是中华武术的巅峰，烈海王又是其中佼佼者，凭借高超的技术使战斗力X1.8
        # ? 阶段SKILL 优先级-25 首发回合1 持续时间1 冷却时间999 标签无：攻击力白值*1.8 one_off_skill(1)
        def skill_func_lhw(skill: Skill):
            skill.owner.base_atk = int(skill.owner.base_atk * 1.8)
            skill.owner.atk = skill.owner.base_atk


        r.add_skill(
            Skill('烈 海 王', 'SKILL', priority=-25, apply_func=skill_func_lhw).one_off_skill(1))


        # ! 消力：传自郭海皇的绝学，普通攻击以及近战系技能所造成的的最终伤害/2
        # ? 阶段REDUCTION 优先级20 首发回合1 持续时间999 冷却时间0 标签无：normal/melee 伤害/2
        def process_func_xl(skill: Skill, message: Message):
            logging.debug(f'伤害减半{message.value}//2={message.value // 2}')
            message.value //= 2
            return False


        def trigger_func_xl(skill: Skill, message: Message):
            return message.tag == 'normal' or message.tag == 'melee'


        r.add_skill(
            Skill('消力', 'REDUCTION', priority=20, turn=1, process_func=process_func_xl, trigger_func=trigger_func_xl))


        # ! 四千年的传承：不会陷入异常状态，面对近战系、技术系的技能可以进行【1d100】的破解判定，75以上成功
        # ? 阶段PASSIVE 优先级-10 首发回合1 持续时间999 冷却时间0 标签无：对melee spell和technique spell 25%概率无效化其技能
        def process_func_sqndcc(skill: Skill, message: Message):
            dice = random.randint(1, 100)
            ret = dice > 75
            logging.debug(f"{skill.owner.name}发动技能 {skill.name} 出目是{dice} "
                          f"应对技能类型{message.tag} 判定{'成功' if ret else '失败'}")
            return ret


        def trigger_func_sqndcc(skill: Skill, message: Message):
            return message.tag == 'melee' or message.tag == 'technique'


        r.add_skill(
            Skill('四千年的传承', 'PASSIVE', priority=-10, turn=1, process_func=process_func_sqndcc,
                  trigger_func=trigger_func_sqndcc))


        # ! 假腿断裂：肢体缺失导致HP-2，Atk-10（吃到了美味的晚餐，断裂后的伤害减轻了）
        # ? 阶段SKILL 优先级-24 首发回合1 持续时间1 冷却时间999
        def skill_func_jtdl(skill: Skill):
            skill.owner.base_atk -= 10
            skill.owner.atk = skill.owner.base_atk
            skill.owner.hp -= 2


        r.add_skill(Skill('假腿断裂', 'SKILL', -24, apply_func=skill_func_jtdl).one_off_skill(1))


        # ! 武之怀（CT5）：3T内Atk+60。3T内可对所有攻击进行【1d100】的破解判定，普通攻击与近战系、技巧系技能30以上成功，其余技能50以上成功，必杀技75以上成功。
        # ? 阶段SKILL 优先级-10 首发回合5 持续时间3 冷却时间5 标签ultra 独占： 攻击力+60 添加如下技能
        # ? 阶段REDUCTION 优先级10 持续时间1 标签无： 对normal/melee technique 其他技能 分别以70% 25% 50% 使之伤害归0

        def skill_func_wzh(skill: Skill):
            owner: Character = skill.owner
            owner.atk += 60

            def process_func_wzh_inner(skill: Skill, message: Message):
                dice = random.randint(1, 100)
                if message.tag == 'melee' or message.tag == 'normal':
                    ret = dice > 30
                elif message.tag == 'ultra':
                    ret = dice > 75
                else:
                    ret = dice > 50
                logging.debug(f"{skill.owner.name}发动技能 {skill.name} 出目是{dice} "
                              f"应对技能类型{message.tag} 判定{'成功 伤害归零' if ret else '失败 伤害不变'}")
                if ret:
                    message.value = 0
                return False

            def trigger_func_wzh_inner(skill: Skill, message: Message):
                return True

            skill_wzh_inner = Skill(
                '武之怀inner',
                'REDUCTION',
                10,
                active=True,
                owner=skill.owner,
                process_func=process_func_wzh_inner,
                trigger_func=trigger_func_wzh_inner).one_turn_skill()
            skill.owner.reduction_queue.add_skill(skill_wzh_inner)


        r.add_skill(Skill('武之怀', 'SKILL', -10, 5, 3, 5, tag='ultra',
                          apply_func=skill_func_wzh, exclusive=True))


        # ! 超人烈海王（CT6）：Atk+600，给予伤害X3，之后2T回避概率翻倍
        # ? 阶段SKILL 优先级-15 首发回合6 持续时间1 冷却时间6 标签ultra 独占：攻击力+600
        # ? 阶段INCREASE 优先级-20 持续时间1 标签无：伤害*3

        def skill_func_crlhw(skill: Skill):
            skill.owner.atk += 600

            def process_func_crlhw(skill: Skill, message: Message):
                logging.debug(f'伤害{message.value}*3={message.value * 3}')
                message.value *= 3
                return False

            def trigger_func_crlhw(skill: Skill, message: Message):
                return True

            skill.owner.increase_queue.add_skill(
                Skill('超人烈海王inner', 'INCREASE', priority=-20, active=True, process_func=process_func_crlhw,
                      trigger_func=trigger_func_crlhw).one_turn_skill())


        r.add_skill(
            Skill('超人烈海王', 'SKILL', -15, 6, 1, 6, tag='ultra', exclusive=True, apply_func=skill_func_crlhw))


        # ! 无冠的武艺：纵使不出全力仍是极强的武者，AtkX1.6
        # ? 阶段SKILL 优先级-25 首发回合1 持续时间1 冷却时间999 标签无：攻击力白值*1.6 one_off_skill(1)
        def skill_func_wgdwy(skill: Skill):
            skill.owner.base_atk = int(skill.owner.base_atk * 1.6)
            skill.owner.atk = skill.owner.base_atk


        m.add_skill(Skill('无冠的武艺', 'SKILL', -25, apply_func=skill_func_wgdwy).one_off_skill(1))


        # ! 华符「芳华绚烂」（CT3）：（技巧系）放出相同形状的美丽弹幕，本回合Atk+30
        # ? 阶段SKILL 优先级-15 首发回合3 持续时间1 冷却时间3 标签technique：攻击力+30
        def skill_func_hffhxl(skill: Skill):
            skill.owner.atk += 30


        m.add_skill(Skill('华符「芳华绚烂」', 'SKILL', -10, tag='technique',
                          apply_func=skill_func_hffhxl).one_turn_skill(3))


        # ! 极光「华严明星」（CT4）：（弹幕系）将七色的巨大气弹精炼后，向敌人打出，对对手造成【1d4】的伤害
        # ? 阶段SKILL 优先级-10 首发回合4 持续时间1 冷却时间4 标签danmaku：调用对方的hp_change造成1d4伤害
        def skill_func_jghymx(skill: Skill):
            damage = random.randint(1, 4)
            logging.debug(f'造成伤害{damage}')
            message = Message('DAMAGE', 'danmaku', damage, skill.owner, skill.owner.rival)
            skill.owner.rival.hp_change(message)


        m.add_skill(
            Skill('极光「华严明星」', 'SKILL', -10, tag='danmaku', apply_func=skill_func_jghymx).one_turn_skill(4))


        # ! 必杀技：彩符「极彩台风」（CT5）：放出七彩的弹幕雨对对手造成伤害，本回合Atk+450，给予伤害X2
        # ? 阶段SKILL 优先级-15 首发回合5 持续时间1 冷却时间5 标签ultra 独占：攻击力+450
        # ? 阶段INCREASE 优先级-20 持续时间1 标签无：伤害*2

        def skill_func_cfjctf(skill: Skill):
            skill.owner.atk += 450

            def process_func_cfjctf(skill: Skill, message: Message):
                logging.debug(f'伤害 {message.value}*2={message.value * 2}')
                message.value *= 2
                return False

            def trigger_func_cfjctf(skill: Skill, message: Message):
                return True

            skill.owner.increase_queue.add_skill(
                Skill('彩符「极彩台风」inner', 'INCREASE', priority=-20, active=True, process_func=process_func_cfjctf,
                      trigger_func=trigger_func_cfjctf).one_turn_skill())


        m.add_skill(
            Skill('彩符「极彩台风」', 'SKILL', -15, 5, 1, 5, tag='ultra', exclusive=True, apply_func=skill_func_cfjctf))

        game = Game(r, m)
        game.start_game()
        result[game.winner] += 1

    print(result)
