import logging
import tqdm
import random

from dice_simulator import ActiveFunction, PassiveFunction, SkillGroup, Message, Character, Game

debug_mode = True
if debug_mode:
    logging.basicConfig(level=logging.DEBUG)
    n_times = 1
else:
    logging.basicConfig(level=logging.WARN)
    n_times = 100000
turns_total_1 = [0] * 30
turns_total_2 = [0] * 30
result = {'灵梦': 0, '千亦': 0}
for i in tqdm.tqdm(range(n_times)):



    # ! 1. 天符【伸手及月】（CT1）：一场战斗中只能使用一次，3T内自身每回合Hp+2，战斗骰变为【3d40】，并暂时获得对特殊攻击的耐性。
    def skill_11(skill: ActiveFunction):
        """
        每回合自身hp+2 不超过血量上限
        """
        target = skill.target
        target.hp += 2
        if target.hp > target.max_hp:
            target.hp = target.max_hp
        logging.info(f'{skill.target.name} Hp+2 当前Hp {target.hp}')


    skill_hp_plus_2_per_turn = ActiveFunction('每回合血量+2', 'SKILL', -5, 3, skill_11)


    def skill_12(skill: ActiveFunction):
        """
        DICE 战斗骰变为3d40
        """
        logging.debug(f'{skill.target.name} 战斗骰变为3d40')
        target = skill.target
        target.last_dice = sum([random.randint(1, 40) for i in range(3)])


    skill_fight_dice_3d40 = ActiveFunction('战斗骰子3d40', 'DICE', -10, 3, skill_12)


    def skill_13(skill: ActiveFunction):
        """
        获得【特殊攻击耐性】
        """
        logging.debug(f'{skill.target.name} 获得【特殊攻击耐性】')
        target = skill.target
        target.tags["resistance"] = 1


    skill_resistance = ActiveFunction('获得特殊攻击耐性', 'SKILL', -30, 3, skill_13)
    # ! 1. 天符【伸手及月】（CT1） 一场战斗中只能使用一次
    skill_tfssjy = SkillGroup('天符【伸手及月】', 0, 1, 999,
                              [skill_hp_plus_2_per_turn, skill_fight_dice_3d40, skill_resistance])


    # ! 2. 四千年的传承：面对近战系、技术系的技能可以进行【1d100】的破解判定，75以上成功
    # ? 每个回合都要破解的技能可以更新自己的tags？
    # ? 可不可以把攻击骰也视作一个技能？
    def process_21(skill: PassiveFunction, message: Message):
        """
        对手技能【宣言时】 如果这个技能是【近战系】或【技巧系】 有1d100>75概率【破解】
        """
        if message.kind != 'SPELL':
            return
        s = message.skill
        # 不可破解标记
        # 话说没这词啊
        if 'melee' in s.tags or 'technique' in s.tags:
            if 'uncounterattackable' in s.tags:
                logging.debug(f'{skill.name} 发动 但 {message.skill.name} 不可破解')
                return
            verdict = 75
            target = skill.target
            verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
            verdict_offset_from_skill = 0 if 'verdict_offset' not in s.tags else s.tags['verdict_offset']
            verdict += verdict_offset_from_owner + verdict_offset_from_skill
            dice = random.randint(1, 100)
            result = dice > verdict
            if dice > verdict:
                message.tags['counterattack'] = 1
            logging.info(f"{skill.name}发动 出目是{dice}/{verdict} 判定{'成功' if result else '失败'}")


    skill_counterattack = PassiveFunction('破解近战系和技巧系技能', 'PASSIVE', 0, 999, process_21)
    skill_sqndcc = SkillGroup('四千年的传承', -10, 1, 999, [skill_counterattack])


    # ! 创造偶像的造形神：每回合开始时制造一个偶像。每次发动技能/必杀技的场合，制造1个偶像。（自身技能/必杀技被破解的场合，视为偶像制造失败）
    # 偶像数目为3个以上时，自身发动技能/必杀技的场合给予对手无视减伤的【1d3】点伤害
    # 偶像数目为6个以上时，为自身提供4点护甲
    # 偶像数目为9个以上时，自身普通攻击所给予的小伤害/中伤害全部视为大伤害
    # 偶像数目为12个以上时，每次自身普通攻击成功的场合，在伤害判定结束后令对手Hp减半
    # ? 要不把所有技能列表合并成主动列表和被动列表？
    def create_haniwa(target: Character, owner: Character):
        """
        制造一个偶像
        如果这是制造的第六个偶像 获得4点护甲
        """
        if 'haniwa' not in target.tags:
            target.tags['haniwa'] = 0
        target.tags['haniwa'] += 1
        logging.info(f'{target.name} 制造了一个偶像 当前偶像数{target.tags["haniwa"]}')
        if target.tags['haniwa'] == 6:
            logging.info(f'当前偶像数{target.tags["haniwa"]}  获得4点护甲')
            target.tags['armor'] = 4

            def reduction_armor(skill: PassiveFunction, message: Message):
                """
                受到伤害时 减少一点护甲值 伤害归零
                """
                if message.kind != 'ATTACK' and message.kind != 'HURT':
                    return
                if message.value == 0:
                    return
                if target.tags['armor'] > 0:
                    target.tags['armor'] -= 1
                    logging.info(f'受到伤害{message.value} 减少护甲1点 当前护甲{target.tags["armor"]}')
                    message.value = 0
                    if target.tags['armor'] == 0:
                        skill.is_expired = True

            skill_armor = PassiveFunction('护甲', 'REDUCTION', 50, 999, reduction_armor, True)
            skill_armor.owner = owner
            skill_armor.target = target
            target.add_skill(skill_armor)


    def skill_31(skill: ActiveFunction):
        """
        每【回合开始时】
        制造一个偶像 如果这是制造的第六个偶像 获得4点护甲
        """
        target = skill.target
        owner = skill.owner
        create_haniwa(target, owner)


    skill_create_haniwa_at_turn_start = ActiveFunction('回合开始时制造偶像', 'SKILL', -50, 999, skill_31)


    def process_32(skill: PassiveFunction, message: Message):
        """
        自身【技能宣言后】 如果该技能没有被破解
        制造一个偶像 如果这是制造的第六个偶像 获得4点护甲
        """
        if message.kind != 'SPELL_SELF':
            return
        if 'counterattack' in message.tags:
            return
        target = skill.target
        owner = skill.owner
        create_haniwa(target, owner)


    skill_create_haniwa_after_skill_spell = PassiveFunction('技能宣言后制造偶像', 'PASSIVE', -10, 999, process_32)


    def process_33(skill: PassiveFunction, message: Message):
        """
        技能【宣言后】 如果当前偶像大于等于3 给对方造成【无视减伤】的1d3伤害
        """
        if message.kind != 'SPELL_SELF':
            return
        target = skill.target
        if 'haniwa' not in target.tags or target.tags['haniwa'] < 3:
            return
        opponent = target.opponent
        dice = random.randint(1, 3)
        message = Message('ATTACK', dice)
        message.tags['ignore_damage_reduction'] = 1
        message.tags['skill_attack'] = 1
        opponent.process_message(message)


    skill_haniwa_attack = PassiveFunction('技能宣言后攻击', 'PASSIVE', 0, 999, process_33)


    def skill_34(skill: ActiveFunction):
        """
        当持有9个及以上的偶像时 对方受到的小伤害和中伤害全部视为大伤害
        """
        target = skill.target
        if 'haniwa' not in target.tags or target.tags['haniwa'] < 9:
            return
        opponent = target.opponent
        opponent.damage_list["小伤害"] = opponent.damage_list["回避"]
        opponent.damage_list["中伤害"] = opponent.damage_list["回避"]


    skill_damage_list_change = ActiveFunction('小伤害和中伤害视为大伤害', 'SKILL', -30, 999, skill_34)


    def process_35(skill: PassiveFunction, message: Message):
        """
        【伤害结束后】 如果持有12个及以上的偶像
        如果普通攻击造成了伤害 发起一次相当于对方hp一半（向上取整）的【直接伤害】
        """
        if message.kind != 'DAMAGE_OVER':
            return
        target = skill.target
        if 'haniwa' not in target.tags or target.tags['haniwa'] < 12:
            return
        if message.value > 0 and 'skill_attack' not in message.tags:
            opponent = target.opponent
            damage = opponent.hp - opponent.hp // 2
            if damage > 0:
                logging.info(f'追加攻击 对方血量下降一半：{damage}')
                new_message = Message('DAMAGE', value=damage)
                new_message.tags['skill_attack'] = 1
                opponent.process_message(new_message)


    skill_damage_after_damage = PassiveFunction('技能宣言后攻击', 'PASSIVE', -50, 999, process_35)
    skill_czoxdzxs = SkillGroup('创造偶像的造形神', 0, 1, 999,
                                [skill_create_haniwa_at_turn_start, skill_create_haniwa_after_skill_spell,
                                 skill_haniwa_attack, skill_damage_list_change, skill_damage_after_damage])


    # ! 贫穷神的加护：自动发动，一天只能只用一次，令对手的大成功转变为大失败
    def process_41(skill: PassiveFunction, message: Message):
        """
        对手大成功时 将其变为大失败 发动一次后失效
        """
        if message.kind != 'SOF':
            return
        damage_name = skill.target.opponent.get_damage_name(message.value)
        if damage_name == '大成功' and not skill.is_expired:
            message.value = skill.target.opponent.damage_list['大失败']
            logging.info(f'{skill.name}发动 对手大成功 将其变为大失败')
            skill.is_expired = True


    skill_reverse = PassiveFunction('逆转大成功', 'COMPETE', 0, 999, process_41)
    skill_pqsdjh = SkillGroup('贫穷神的加护', -10, 1, 999, [skill_reverse])


    # ! 毫无默契：每回合进行一次【1d100】的误伤判定，70以下时本回合无法进行普通攻击 持续3回合
    def skill_51(skill: ActiveFunction):
        """
        【回合开始时】 进行1d100的判定 大于30时跳过本回合的DICE阶段 持续3回合
        """
        dice = random.randint(1, 100)
        if dice > 30:
            logging.info(f'{skill.name}发动 dice={dice}/30 跳过本回合的DICE阶段')
            skill.target.skip_stage.append('DICE')
        else:
            logging.info(f'{skill.name}发动 dice={dice}/30')


    skill_skip_dice = ActiveFunction('跳过DICE', 'SKILL', -50, 3, skill_51)
    skill_hwmq = SkillGroup('毫无默契', -60, 1, 999, [skill_skip_dice])


    # ! 四季鲜花之主：每回合上升【1d3】点Atk，Atk到达300点时不再上升
    def skill61(skill: ActiveFunction):
        target = skill.target
        if target.base_atk < 300:
            dice = random.randint(1, 3)
            target.base_atk += dice
            if target.base_atk > 300:
                target.base_atk = 300
            logging.info(f'{skill.name} 发动 攻击力白值上升 {dice} 现在攻击力白值 {target.base_atk}')


    skill_base_atk_up = ActiveFunction('攻击力白值上升', 'SKILL', -20, 999, skill61)
    skill_sjxhzz = SkillGroup('四季鲜花之主', -30, 1, 999, [skill_base_atk_up])


    # ! 【这合理吗？】：一场战斗中仅能使用一次，将自身或对手的骰子出目中的个位与十位逆转
    def skill71(skill: ActiveFunction):
        """
        双方投掷战斗骰后 如果我方atk+dice小于（小于等于）对方 且以下条件有一个满足：
        互换我方dice个位和十位后 我方atk+dice不小于（大于）对方
        互换对方dice个位和十位后 我方atk+dice不小于（大于）对方
        则发动 互换个位和十位 当dice是三位数及以上时 也只互换个位和十位 只有一位数时变为整十数
        """
        if skill.is_expired:
            return
        target = skill.target
        opponent = target.opponent
        dice1 = target.last_dice
        atk1 = target.atk
        total1 = dice1 + atk1
        dice2 = opponent.last_dice
        atk2 = opponent.atk
        total2 = dice2 + atk2
        if total1 > total2:
            return
        new_dice1 = (dice1 // 100) * 100 + (dice1 % 10) * 10 + (dice1 // 10) % 10
        new_dice2 = (dice2 // 100) * 100 + (dice2 % 10) * 10 + (dice2 // 10) % 10
        new_total1 = new_dice1 + atk1
        new_total2 = new_dice2 + atk2
        if total1 < total2:
            if new_total1 >= total2:
                target.last_dice = new_dice1
                logging.info(f'{skill.name} 发动 互换 {target.name} 的个位和十位 {dice1} -> {new_dice1}')
                skill.is_expired = True
                return
            if total1 >= new_total2:
                opponent.last_dice = new_dice2
                logging.info(f'{skill.name} 发动 互换 {opponent.name} 的个位和十位 {dice2} -> {new_dice2}')
                skill.is_expired = True
                return
        if total1 == total2:
            if new_total1 > total2:
                target.last_dice = new_dice1
                logging.info(f'{skill.name} 发动 互换 {target.name} 的个位和十位 {dice1} -> {new_dice1}')
                skill.is_expired = True
                return
            if total1 > new_total2:
                opponent.last_dice = new_dice2
                logging.info(f'{skill.name} 发动 互换 {opponent.name} 的个位和十位 {dice2} -> {new_dice2}')
                skill.is_expired = True
                return


    skill_swap_dice = ActiveFunction('互换个位十位', 'DICE', 0, 999, skill71)
    skill_zhlm = SkillGroup('这合理吗？', -30, 1, 999, [skill_swap_dice])


    # ! 与朋友的回忆（CT3）：（自身加持类）3T内可以进行【1d100】的破解判定，本回合技能30以上成功，必杀技75以上成功，其后2T技能45以上成功，必杀技90以上成功
    def process_81(skill: PassiveFunction, message: Message):
        """
        对手技能【宣言时】 如果是必杀技有1d100>75破解 技能>30 之后两回合90/45
        """
        if message.kind != 'SPELL':
            return
        s = message.skill
        # 不可破解标记
        # 话说没这词啊
        if 'uncounterattackable' in s.tags:
            logging.debug(f'{skill.name} 发动 但 {message.skill.name} 不可破解')
            return
        if skill.lasting == 1:
            verdict = 75 if 'ultra' in s.tags else 30
        else:
            verdict = 90 if 'ultra' in s.tags else 45
        target = skill.target
        verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
        verdict_offset_from_skill = 0 if 'verdict_offset' not in s.tags else s.tags['verdict_offset']
        verdict += verdict_offset_from_owner + verdict_offset_from_skill
        dice = random.randint(1, 100)
        result = dice > verdict
        if dice > verdict:
            message.tags['counterattack'] = 1
        logging.info(f"{skill.name}发动 出目是{dice}/{verdict} 判定{'成功' if result else '失败'}")


    function81 = PassiveFunction('破解技能', 'PASSIVE', 0, 3, process_81)
    skill_ypydhy = SkillGroup('与朋友的回忆', -30, 3, 3, [function81])


    # ! 武之怀（CT5）：3T内Atk+60
    def skill91(skill: ActiveFunction):
        skill.target.atk += 60


    function91 = ActiveFunction('武之怀', 'SKILL', -5, 3, skill91)
    skill_wzh = SkillGroup('武之怀', 0, 5, 5, [function91])


    # ! 华胥的亡灵：每次发动技能/必杀技时对手的Hp上限-1（最低降到1点）。
    def process_101(skill: PassiveFunction, message: Message):
        """
        自身【技能宣言后】 对方生命上限-1 最低为1
        """
        if message.kind != 'SPELL_SELF':
            return
        opponent = skill.target.opponent
        if opponent.max_hp > 1:
            opponent.max_hp -= 1
            if opponent.hp > opponent.max_hp:
                opponent.hp = opponent.max_hp
            logging.info(f"{skill.name}发动 对手生命上限-1 现在为{opponent.hp}/{opponent.max_hp}")


    function101 = PassiveFunction('降低对方生命上限', 'PASSIVE', -10, 999, process_101)
    skill_hxdwl = SkillGroup('华胥的亡灵', -30, 1, 999, [function101])


    # ! 本能【本我的解放】（CT2）：（自身加持系）本回合对手无法回避
    def skill_111(skill: ActiveFunction):
        """
        本回合对方无法回避
        """
        opponent = skill.target.opponent
        opponent.damage_list["回避"] = 0


    function111 = ActiveFunction('本我的解放', 'SKILL', -30, 1, skill_111)
    skill_bnbwdjf = SkillGroup('本能【本我的解放】', 0, 2, 2, [function111])


    # ! 【Subterranean Sun】（CT7）：我就是地底的太阳！无法回避/破解/防御，Atk+825，给予伤害X5，对对手进行一次【特殊攻击】坠落：进行一次【1d100】的堕落判定，出目为40以上时对手Atk-30，出目为75以上时本回合战斗自动成功。（对手拥有特殊攻击耐性的场合，成功值变为65/90）
    def skill_121(skill: ActiveFunction):
        """
        本回合atk+825
        """
        skill.target.atk += 825
        logging.info(f'{skill.name}发动 现在atk为{skill.target.atk}+825={skill.target.atk + 825}')


    function121 = ActiveFunction('sun加攻', 'SKILL', -5, 1, skill_121)


    def increase_122(skill: PassiveFunction, message: Message):
        """
        伤害x5
        """
        if message.kind == 'HURT':
            logging.info(f'{skill.name}发动 伤害x5 现在伤害为{message.value}*5={message.value * 5}')
            message.value *= 5


    function122 = PassiveFunction('sun伤害x5', 'INCREASE', 10, 1, increase_122)


    def skill123(skill: ActiveFunction):
        """
        坠落判定，出目为40以上时对手Atk-30，出目为75以上时本回合战斗自动成功。（对手拥有特殊攻击耐性的场合，成功值变为65/90）
        """
        dice = random.randint(1, 100)
        target = skill.target
        opponent = skill.target.opponent
        if 'resistance' in opponent.tags:
            if dice > 65:
                opponent.atk -= 30
                logging.info(f'坠落判定：{dice}/65/90 对手Atk-30')
            elif dice > 90:
                target.tags['auto_win'] = 1
                logging.info(f'坠落判定：{dice}/65/90 本回合自动胜利')
            else:
                logging.info(f'坠落判定：{dice}/65/90 无事发生')
        else:
            if dice > 40:
                opponent.atk -= 30
                logging.info(f'坠落判定：{dice}/40/75 对手Atk-30')
            elif dice > 75:
                target.tags['auto_win'] = 1
                logging.info(f'坠落判定：{dice}/40/75 本回合自动胜利')
            else:
                logging.info(f'坠落判定：{dice}/40/75 无事发生')


    function123 = ActiveFunction('坠落', 'SKILL', -5, 1, skill123)
    skill_subterranean_sun = SkillGroup('【Subterranean Sun】', 0, 7, 7, [function121, function122, function123],
                                        base_tags={'uncounterattackable': 1})


    # ! 红符【巨阙】（CT3）：（近战系）本回合Hp-2, Atk+80， 给予伤害+4
    def skill131(skill: ActiveFunction):
        """
        当自己生命值>2 时 本回合hp-2 atk+80
        """
        if skill.target.hp > 2:
            skill.target.hp -= 2
            skill.target.atk += 80
            logging.info(f'【巨阙】：{skill.target.name} 本回合Hp-2 Atk+80')
            skill.tags['success'] = 1
        else:
            logging.info(f'【巨阙】：{skill.target.name} 失败 生命值过低：{skill.target.hp}')
            skill.tags['success'] = 0


    function131 = ActiveFunction('巨阙加攻', 'SKILL', -5, 1, skill131)


    def increase_132(skill: PassiveFunction, message: Message):
        """
        给予伤害+4
        """
        if message.kind == 'HURT':
            if skill.belongs_to.functions[0].tags['success'] == 1:
                logging.info(f'巨阙加伤害： {message.value}+4={message.value + 4}')
                message.value += 4
            else:
                logging.info(f'巨阙加伤害失败 生命值过低')


    function132 = PassiveFunction('巨阙加伤害', 'INCREASE', 20, 1, increase_132)
    skill_hfjq = SkillGroup('红符【巨阙】', 0, 3, 3, [function131, function132], base_tags={'melee': 1})


    # ! 神光【无忤为宗】（CT6）：2T内自身受到的最终伤害减半。
    def reduction_141(skill: PassiveFunction, message: Message):
        """
        2T内自身受到的最终伤害减半
        """
        if message.kind == 'HURT':
            logging.info(f'{skill.name} 本回合受到的伤害减半 {message.value}//2={message.value // 2}')
            message.value //= 2


    function141 = PassiveFunction('无忤为宗减伤', 'REDUCTION', 30, 2, reduction_141)
    skill_wwwz = SkillGroup('神光【无忤为宗】', 0, 6, 6, [function141])


    # ! 玉符【众神的光辉弹冠】 （CT6） ：本回合结束后对对手造成2点追加伤害
    def pursuit_151(skill: ActiveFunction):
        """
        回合结束时 对对手造成两点伤害
        """
        message = Message('ATTACK', 2)
        logging.info(f'{skill.name} 发动 造成两点伤害')
        skill.target.opponent.process_message(message)


    function151 = ActiveFunction('众神的光辉弹冠', 'PURSUIT', 0, 1, pursuit_151)
    skill_yfzsdghdg = SkillGroup('玉符【众神的光辉弹冠】', 0, 6, 6, [function151])


    # ! 过于危险的背景武者 （CT4）：进行一次特殊攻击：【失衡】：进行一次【1d100】的失衡判定，50以上本回合对手无法行动 对方有特殊攻击耐性的情况下为90
    def skill_161(skill: ActiveFunction):
        """
        失衡
        """
        dice = random.randint(1, 100)
        opponent = skill.target.opponent
        if 'resistance' in opponent.tags:
            if dice > 90:
                opponent.skip_stage.extend(['SKILL', 'PASSIVE', 'DICE', 'COMPETE', 'INCREASE', 'REDUCTION', 'PURSUIT'])
                logging.info(f'失衡判定：{dice}/90 对手无法行动')
            else:
                logging.info(f'失衡判定：{dice}/90 无事发生')
        else:
            if dice > 50:
                opponent.skip_stage.extend(['SKILL', 'PASSIVE', 'DICE', 'COMPETE', 'INCREASE', 'REDUCTION', 'PURSUIT'])
                logging.info(f'失衡判定：{dice}/50 对手无法行动')
            else:
                logging.info(f'失衡判定：{dice}/50 无事发生')


    function161 = ActiveFunction('过于危险的背景武者', 'SKILL', -60, 1, skill_161)
    skill_gywxdbjwz = SkillGroup('【过于危险的背景武者】', 0, 4, 4, [function161])


    # ! 假腿：每轮战斗都需要进行一次【1d100】的假腿判定，80以上假腿断裂，该回合战斗自动失败同时之后的战斗中Atk-20
    def skill_171(skill: ActiveFunction):
        """
        假腿 回合开始时进行1d100>80 成功后对手本回合战斗自动成功 攻击力白值-20 只能触发一次
        """
        dice = random.randint(1, 100)
        if dice > 80:
            skill.target.opponent.tags['auto_win'] = 1
            skill.target.base_atk -= 20
            logging.info(f'假腿判定：{dice}/80 假腿断裂 对手本回合战斗自动成功 攻击力白值-20')
            skill.is_expired = True
        else:
            logging.info(f'假腿判定：{dice}/80 假腿未断裂')


    function171 = ActiveFunction('假腿', 'SKILL', -50, 999, skill_171)
    skill_jt = SkillGroup('【假腿】', -30, 1, 999, [function171])

    cha1 = Character('灵梦', 105, 32, 42)
    cha2 = Character('千亦', 100, 32, 42)
    cha1.register_skill(skill_tfssjy)
    cha1.register_skill(skill_sqndcc)
    cha1.register_skill(skill_pqsdjh)
    cha1.register_skill(skill_hwmq)
    cha1.register_skill(skill_sjxhzz)
    cha1.register_skill(skill_zhlm)
    cha1.register_skill(skill_wzh)
    cha1.register_skill(skill_bnbwdjf)
    cha1.register_skill(skill_subterranean_sun)
    cha1.register_skill(skill_wwwz)
    cha1.register_skill(skill_yfzsdghdg)
    cha1.register_skill(skill_gywxdbjwz)
    cha2.register_skill(skill_ypydhy)
    cha2.register_skill(skill_czoxdzxs)
    cha2.register_skill(skill_hxdwl)
    cha2.register_skill(skill_hfjq)
    cha2.register_skill(skill_jt)

    random.seed(i)  # 15175

    game = Game(cha1, cha2)
    game.start()
    result[game.winner] += 1
    if game.winner == '灵梦':
        turns_total_1[game.turn] += 1
    else:
        turns_total_2[game.turn] += 1
    # if game.turn < 3:
    #     print(i, game.turn)

print(result)
print(turns_total_1)
print(turns_total_2)
