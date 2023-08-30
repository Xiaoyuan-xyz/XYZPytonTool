import random


class Message:
    """
    所有操作如攻击 治疗都会被封装成一个消息 接受者会处理这个消息
    """

    def __init__(self, src, dest, type, value):
        self.src = src
        self.dest = dest
        self.type = type
        self.value = value


class Skill:
    """
    技能类
    技能类型：
    天赋 talent 一次性 在战斗前使用
    被动 passive 等待一定条件时触发 子类
    普通 normal
    近战 melee
    技术 technique
    魔法 magic
    弹幕 barrage
    必杀 ultra

    一个技能的发动应该是这样
    1. 首先 给对方发技能宣言
    2. 收回对方的反应
    3. 计算技能效果
    4. 给自己和对方发技能效果
    """

    def __init__(
            self,
            name,
            type,
            description,
            use_func,
            owner=None,
            detail=None):
        self.name = name
        self.type = type
        self.description = description
        self.detail = detail  # 技能实际描述
        self.use_func = use_func  # 技能使用时的函数 第一个参数是skill本身
        self.owner: Character = owner  # 注册的时候才回赋值owner

    def use(self):
        return self.use_func(self)


class PassiveSkill(Skill):
    def __init__(
            self,
            name,
            description,
            use_func,
            trigger_func=None,
            owner=None,
            detail=None):
        super().__init__(
            name=name,
            type='passive',
            description=description,
            detail=detail,
            use_func=use_func,
            owner=owner)
        self.trigger_func = trigger_func  # 技能在什么条件下会触发？ 第一个参数应该是message 返回布尔值

    def use(self, message: Message):
        return self.use_func(self, message)

    def trigger(self, message: Message):
        if self.trigger_func is None:
            return False
        return self.trigger_func(message)


class CooldownSkill(Skill):
    def __init__(
            self,
            name,
            type,
            description,
            use_func,
            use_time,
            cooldown,
            countdown,
            recover_func=None,
            owner=None,
            detail=None):
        super().__init__(
            name=name,
            type=type,
            description=description,
            detail=detail,
            use_func=use_func,
            owner=owner)
        self.use_time = use_time  # 使用的时机 未激活时是下一次使用的时机
        self.cooldown = cooldown  # 冷却时间
        self.countdown = countdown  # 持续时间
        self.recover_func = recover_func
        self.active = False

    # 当技能结束时 要如何使得技能恢复原状？
    # 必须保证技能重置时不能因为一些顺序问题而相互矛盾
    def use(self, now_turn):
        self.active = True
        self.stage = now_turn - self.use_time + 1
        self.use_func(self)

    def recover(self):
        if self.recover_func is not None:
            self.recover_func(self)
        self.active = False
        self.use_time += self.cooldown




class Character:
    def __init__(self, name, atk, hp):
        self.name = name
        self.base_atk = atk  # 括号内的值
        self.atk = atk  # 括号外的值
        self.real_atk = atk  # 算上各种buff后的实际值
        self.max_hp = hp
        self.hp = hp
        self.skills = []
        self.buffs = []
        self.rival: Character = None
        self.death = False
        self.damage_factor = 1
        self.damage_offset = 0
        self.passive_list:list[PassiveSkill] = []

    def register_skill(self, skill: Skill):
        skill.owner = self
        self.skills.append(skill)

    def register_skills(self, skills: list[Skill]):
        for skill in skills:
            self.register_skill(skill)

    def use_talent_skill(self):
        for skill in self.skills:
            if skill.type == 'talent':
                skill.use()

    def recover(self, now_turn):
        for skill in self.skills:
            if isinstance(skill, CooldownSkill):
                skill: CooldownSkill
                if now_turn == skill.use_time + skill.countdown:
                    skill.recover()

    def use_skill(self, now_turn):
        skill_type = 'normal'
        skills_should_use = []
        skills_should_keep = []
        for skill in self.skills:
            if isinstance(skill, CooldownSkill):
                skill: CooldownSkill
                if not skill.active and now_turn == skill.use_time:
                    skill_type = skill.type
                    skills_should_use.append(skill)
                if skill.active:
                    skills_should_keep.append(skill)
        if len(skills_should_use) > 0:
            skill_should_use_index = random.randint(1, len(skills_should_use))
        for i in range(len(skills_should_use)):
            if i == skill_should_use_index - 1:
                print(
                    f'{self.name} 新发动了技能 {skills_should_use[i].name} 其余技能延迟1回合')
                skills_should_use[i].use(now_turn=now_turn)
            else:
                skills_should_use[i].use_time += 1
        for skill in skills_should_keep:
            skill.use(now_turn=now_turn)
        # todo 如果这回合使用的技能 不是normal的 那么只能随机选择一个使用
        return skill_type

    def atk_dice(self):
        """
        攻击骰子
        """
        return random.randint(1, 10)

    def attack(self):
        """
        攻击出目
        """
        dice = self.atk_dice()
        print(f"{self.name}的攻击：{self.real_atk}+{dice}={self.real_atk+dice}")
        return self.real_atk + dice

    def apply_message(self, message: Message):
        value = message.value
        if 'Spell' not in message.type:
            print(f'{self.name}的血量：{self.hp}-{value}={self.hp - value}')
        self.hp_change(-value)

    def process_message(self, message):
        """
        接受一个message 让所有被动技能检验是否触发 然后应用这个message
        """
        for skill in self.passive_list:
            if skill.trigger(message):
                ret = skill.use(message)  # 被动技能返回的是 是否要无效化这个被动技能
                if ret:
                    return ret
        self.apply_message(message)
        return False

    def hurt_rival(self, skill_type, damage=None):
        # 发动宣言
        message = Message(self, self.rival, skill_type + 'Spell', 0)
        if self.rival.process_message(message):  # True表示失败
            return
        if damage is None:
            damage = self.rival.base_hurt()
            damage = damage * self.damage_factor + self.damage_offset
        message = Message(self, self.rival, skill_type, damage)
        self.rival.process_message(message)

    def base_hurt(self, depth=1):
        dice = random.randint(1, 10)
        if dice < 10:
            dmg = dice // 2  # 回避 小 小 中 中 大 大 特大 特大 sof
            if depth == 1:
                ret = dmg
            if depth == 2:
                ret = dmg * 2
            if depth >= 3:
                ret = dmg * 4
            print(f'骰子出目{dice} 基础伤害{ret}')
        else:  # sof 大成功或大失败
            depth_change = random.choice([1, -1])  # 1代表大失败 -1代表大成功
            print(f'骰子出目{dice} {"大成功" if depth_change == -1 else "大失败"}')
            depth += depth_change
            if depth == 0:
                self.hurt_rival('normal')  # 大成功 发动反击
                ret = 0
            if depth >= 1:
                ret = self.base_hurt(depth)

        return ret

    def hp_change(self, value):
        self.hp += value

        if self.hp <= 0:
            self.death = True
            print(f'{self.name}战败！')
            raise Exception('战败方', self.name)

    def clean(self):
        self.real_atk = self.atk
        self.damage_factor = 1
        self.damage_offset = 0
        self.passive_list = []
        for skill in self.skills:
            if isinstance(skill, PassiveSkill):
                self.passive_list.append(skill)


if __name__ == '__main__':
    count = 0
    total_fight = 10000
    for i in range(total_fight):
        try:
            # 角色生成
            print('对战开始')
            retsu = Character('烈', 80, 15)

            def skill_func_lhw(skill: Skill):
                owner: Character = skill.owner
                owner.atk = int(owner.base_atk * 1.8)
                print(f"{skill.owner.name}发动技能 {skill.name}")
            skill_lhw = Skill(
                '烈 海 王',
                type='talent',
                description='海王是中华武术的巅峰，烈海王又是其中佼佼者，凭借高超的技术使战斗力X1.8',
                detail='天赋技能，战斗前使攻击力*1.8，向下取整。',
                use_func=skill_func_lhw)
            retsu.register_skill(skill_lhw)

            def trigger_func_xl(message: Message):
                type = message.type
                return type == 'normal' or type == 'melee'

            def skill_func_xl(skill: Skill, message: Message):
                print(
                    f"{skill.owner.name}发动技能 {skill.name} 伤害降低{message.value}/2={message.value//2}")
                message.value = message.value // 2
                return False
            skill_xl = PassiveSkill(
                '消力',
                description='传自郭海皇的绝学，普通攻击以及近战系技能所造成的的最终伤害/2',
                detail='被动技能，当受到普通攻击或近战攻击时，使这个值减半，向下取整。',
                use_func=skill_func_xl,
                trigger_func=trigger_func_xl)
            retsu.register_skill(skill_xl)

            def skill_func_jtdl(skill: Skill):
                owner: Character = skill.owner
                owner.atk -= 10
                owner.hp -= 2
                print(f"{skill.owner.name}发动技能 {skill.name}")
            skill_jtdl = Skill(
                '假腿断裂',
                type='talent',
                description='肢体缺失导致HP-2，Atk-10（吃到了美味的晚餐，断裂后的伤害减轻了）',
                detail='天赋技能，战斗前使攻击力-10，生命值-2。',
                use_func=skill_func_jtdl)
            retsu.register_skill(skill_jtdl)

            def skill_func_sqndcc(skill: Skill, message: Message):
                dice = random.randint(1, 100)
                print(
                    f"{skill.owner.name}发动技能 {skill.name} 出目是{dice} 判定{'成功'if dice>75 else '失败'}")
                return dice > 75

            def trigger_func_sqndcc(message: Message):
                type = message.type
                return type == 'technique' or type == 'melee'
            skill_sqndcc = PassiveSkill(
                '四千年的传承',
                description='不会陷入异常状态，面对近战系、技术系的技能可以进行【1d100】的破解判定，75以上成功',
                detail='被动技能，当受到近战系、技术系技能时，有25%的概率使攻击无效',
                use_func=skill_func_sqndcc,
                trigger_func=trigger_func_sqndcc)
            retsu.register_skill(skill_sqndcc)

            def skill_func_wzh(skill: Skill):
                owner: Character = skill.owner
                owner.real_atk += 60
                def skill_func_wzh_inner(skill:Skill, message:Message):
                    dice = random.randint(1, 100)
                    if message.type=='melee' or message.type == 'normal':
                        ret = dice > 30
                    elif message.type=='ultra':
                        ret = dice > 75
                    else:
                        ret = dice > 50
                    print(f"{skill.owner.name}发动技能 {skill.name} 出目是{dice} 应对技能类型{message.type} 判定{'成功' if ret else '失败'}")
                    return ret
                def trigger_func_wzh_inner(message:Message):
                    return 'Spell' not in message.type
                skill_wzh_inner = PassiveSkill(
                    name='武之怀passive',
                    description='',
                    detail='被动技能，当受到近战系、技术系技能时，有70%的概率使攻击无效，必杀技为25%，其余技能为50%。',
                    use_func=skill_func_wzh_inner,
                    trigger_func=trigger_func_wzh_inner,
                    owner=owner
                )
                owner.passive_list = [it for it in owner.passive_list if it.name != '四千年的传承']
                owner.passive_list.append(skill_wzh_inner)
                print(f"{skill.owner.name}发动技能 {skill.name}")
            skill_wzh = CooldownSkill(
                '武之怀',
                type='ultra',
                description='3T内Atk+60。3T内可对所有攻击进行【1d100】的破解判定，普通攻击与近战系、技巧系技能30以上成功，其余技能50以上成功，必杀技75以上成功。',
                detail='3T内atk+60 将四千年的传承替换为 武之怀passive',
                use_time=5,
                cooldown=5,
                countdown=1,
                use_func=skill_func_wzh,)
            retsu.register_skill(skill_wzh)

            def skill_func_crlhw(skill: Skill):
                owner = skill.owner
                owner.real_atk += 600
                owner.damage_factor *= 3
                print(f"{skill.owner.name}发动技能 {skill.name}")
            skill_crlhw = CooldownSkill(
                '超人烈海王',
                type='ultra',
                description='：Atk+600，给予伤害X3，之后2T回避概率翻倍',
                detail='必杀系，atk+650，基础伤害*3',
                use_time=6,
                cooldown=6,
                countdown=1,
                use_func=skill_func_crlhw)
            retsu.register_skill(skill_crlhw)


            meirin = Character('美铃', 100, 15)

            def skill_func_wgdwy(skill: Skill):
                owner: Character = skill.owner
                print(f"{skill.owner.name}发动技能 {skill.name}")
                owner.atk = int(owner.base_atk * 1.6)
            skill_wgdwy = Skill(
                '无冠的武艺',
                type='talent',
                description='纵使不出全力仍是极强的武者，AtkX1.6',
                detail='天赋技能，战斗前使攻击力*1.6，向下取整。',
                use_func=skill_func_wgdwy)
            meirin.register_skill(skill_wgdwy)

            def skill_func_hffhxl(skill: Skill):
                owner: Character = skill.owner
                owner.real_atk += 30
                print(f"{skill.owner.name}发动技能 {skill.name}")
            skill_hffhxl = CooldownSkill(
                '华符「芳华绚烂」',
                type='technique',
                description='（技巧系）放出相同形状的美丽弹幕，本回合Atk+30',
                detail='技巧系，本回合atk+30。',
                use_time=3,
                cooldown=3,
                countdown=1,
                use_func=skill_func_hffhxl)
            meirin.register_skill(skill_hffhxl)

            def skill_func_jghymx(skill: Skill):
                owner = skill.owner
                damage = random.randint(1, 4)
                print(f"{skill.owner.name}发动技能 {skill.name} 对敌人造成基础伤害{damage}")
                owner.hurt_rival('barrage', damage)

            skill_jghymx = CooldownSkill(
                '极光「华严明星」',
                type='normal',
                description='（弹幕系）将七色的巨大气弹精炼后，向敌人打出，对对手造成【1d4】的伤害',
                detail='普通系，即时生效，产生弹幕系的1d4伤害',
                use_time=4,
                cooldown=4,
                countdown=1,
                use_func=skill_func_jghymx)
            meirin.register_skill(skill_jghymx)

            def skill_func_cfjctf(skill: Skill):
                owner = skill.owner
                owner.real_atk += 450
                owner.damage_factor *= 2
                print(f"{skill.owner.name}发动技能 {skill.name}")
            skill_cfjctf = CooldownSkill(
                '彩符「极彩台风」',
                type='ultra',
                description='放出七彩的弹幕雨对对手造成伤害，本回合Atk+450，给予伤害X2',
                detail='必杀系，atk+450，基础伤害*2',
                use_time=5,
                cooldown=5,
                countdown=1,
                use_func=skill_func_cfjctf)
            meirin.register_skill(skill_cfjctf)

            retsu.rival = meirin
            meirin.rival = retsu

            # 开始前 使用被动技能
            now_turn = 0
            retsu.use_talent_skill()
            meirin.use_talent_skill()
            while not retsu.death and not meirin.death:
                now_turn += 1
                print(f'第{now_turn}回合开始')
                # buff 结算环节
                retsu.recover(now_turn=now_turn)
                meirin.recover(now_turn=now_turn)
                # 技能释放环节 矛盾的技能怎么办？
                retsu.clean() # 基础数值复位
                meirin.clean()
                retsu_skill_type = retsu.use_skill(now_turn=now_turn)
                meirin_skill_type = meirin.use_skill(now_turn=now_turn)
                # 拼点环节
                atk1 = retsu.attack()
                atk2 = meirin.attack()
                if atk1 > atk2:
                    print(f'{retsu.name}取得攻击机会')
                    retsu.hurt_rival(skill_type=retsu_skill_type)
                if atk1 < atk2:
                    print(f'{meirin.name}取得攻击机会')
                    meirin.hurt_rival(skill_type=meirin_skill_type)
                print(f'烈的hp{retsu.hp}, 美铃的hp{meirin.hp}')

        except Exception as e:
            count += 0 if e.args[1] == '烈' else 1

    print(f'烈的胜率：{count/total_fight:.2%}')
