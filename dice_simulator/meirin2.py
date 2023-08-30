import logging
import tqdm
import random

from dice_simulator import ActiveFunction, PassiveFunction, SkillGroup, Message, Character, Game

FOREVER = 999

# SkillGroup技能激活
SG_PASSIVE = -10
SG_COUNTERATTACK = -5
SG_ACTIVE = 0

# SKILL
TABLE = -30
ATK_MULTIPLY = -10
ATK_ADDITION = -5
ATK_FINAL = -2
ATTACK = 0

# INCREASE/REDUCTION
DAMAGE_MULTIPLY = 10
DAMAGE_ADDITION = 20
FINAL_DAMAGE_MULTIPLY = 30

debug_mode = False
if debug_mode:
    logging.basicConfig(level=logging.DEBUG)
    n_times = 1
else:
    logging.basicConfig(level=logging.WARN)
    n_times = 100000
turns_total_1 = [0] * 40
turns_total_2 = [0] * 40
result = {'烈海王': 0, '红美铃': 0}
for i in tqdm.tqdm(range(n_times)):
    random.seed(i)


    # ! 烈 海 王：海王是中华武术的巅峰，烈海王又是其中佼佼者，凭借高超的技术使战斗力X1.8
    # ? 攻击力*1.8
    def i11(skill:ActiveFunction):
        target = skill.target
        target.atk = int(target.atk*1.8)
    f11 = ActiveFunction('烈 海 王', 'SKILL', priority=ATK_MULTIPLY, duration=FOREVER, apply_func=i11)
    s1 = SkillGroup('烈 海 王', SG_PASSIVE, 1, 999, [f11])
    # ! 消力：传自郭海皇的绝学，普通攻击以及近战系技能所造成的的最终伤害/2（对战斗力230以上的对手无效）
    # ? 普通攻击及近战系技能造成的最终伤害/2
    def i21(skill:PassiveFunction, message:Message):
        if (message.kind == 'ATTACK' and 'melee' in message.tags) or message.kind == 'HURT':
            logging.info(f'消力：{message.value}/2={message.value//2}')
            message.value = int(message.value/2)
    f21 = PassiveFunction('消力', 'REDUCTION', priority=FINAL_DAMAGE_MULTIPLY, duration=FOREVER, process_func=i21)
    s2 = SkillGroup('消力', SG_PASSIVE, 1, 999, [f21])
    # ! Flower star（CT4）：（弹幕系）对对手放出带有神秘力量的星形花弹，造成必中的【2+1d5】点伤害。
    # ? 弹幕系技能攻击 伤害2+1d5
    def i31(skill:ActiveFunction):
        dice = random.randint(1, 2)
        logging.info(f'花弹将要造成{dice}点伤害')
        message = Message('ATTACK', dice)
        message.tags['danmaku'] = 1
        message.tags['skill_attack'] = 1
        skill.target.opponent.process_message(message)
    f31 = ActiveFunction('Flower star', 'SKILL', priority=ATTACK, duration=1, apply_func=i31)
    s31 = SkillGroup('Flower star', SG_ACTIVE, 4, 4, [f31])
    def i32(skill:ActiveFunction):
        logging.info(f'花弹将要造成2点必中伤害')
        message = Message('ATTACK', 2)
        message.tags['danmaku'] = 1
        message.tags['skill_attack'] = 1
        message.tags['uncounterattackable'] = 1
        skill.target.opponent.process_message(message)
    f32 = ActiveFunction('Flower star', 'SKILL', priority=ATTACK, duration=1, apply_func=i32)
    s32 = SkillGroup('Flower star', SG_ACTIVE, 4, 4, [f32], base_tags={'uncounterattackable': 1})
    # ! 武之怀（CT5）：3T内Atk+60。3T内可对所有攻击进行【1d100】的破解判定，普通攻击与近战系、技巧系技能30以上成功，其余技能50以上成功，必杀技75以上成功。
    # ? 对ATTACK和HURT类，最终伤害有如上概率为0
    def i41(skill:PassiveFunction, message:Message):
        if 'uncounterattackable' in message.tags:
            return
        if message.kind == 'ATTACK' or message.kind == 'HURT':
            target = skill.target
            dice = random.randint(1, 100)
            verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
            verdict_offset_from_message = 0 if 'verdict_offset' not in message.tags else message.tags['verdict_offset']
            verdict_offset = verdict_offset_from_owner + verdict_offset_from_message
            if 'skill_attack' not in message.tags or 'melee' in message.tags or 'technique' in message.tags:
                result = dice > 30 + verdict_offset
                logging.info(f'武之怀破解：{dice}/{30 + verdict_offset} {"成功" if result else "失败"}')
            elif 'ultra' in message.tags:
                result = dice > 75 + verdict_offset
                logging.info(f'武之怀破解：{dice}/{75 + verdict_offset} {"成功" if result else "失败"}')
            else:
                result = dice > 50 + verdict_offset
                logging.info(f'武之怀破解：{dice}/{50 + verdict_offset} {"成功" if result else "失败"}')
            if result:
                 message.value = 0
    f41 = PassiveFunction('武之怀', 'REDUCTION', priority=FINAL_DAMAGE_MULTIPLY, duration=3, process_func=i41)
    def i42(skill:ActiveFunction):
        skill.target.atk += 60
    f42 = ActiveFunction('武之怀', 'SKILL', priority=ATK_ADDITION, duration=3, apply_func=i42)
    s4 = SkillGroup('武之怀', SG_PASSIVE, 5, 5, [f41, f42], base_tags={'ultra': 1})
    # ! 超人烈海王（CT6）：Atk+650，给予伤害X4，之后2T回避概率翻倍
    def i51(skill:ActiveFunction):
        skill.target.atk += 650
    f51 = ActiveFunction('超人烈海王1', 'SKILL', priority=ATK_ADDITION, duration=1, apply_func=i51)
    def i52(skill:PassiveFunction, message:Message):
        if message.kind == 'HURT':
            message.value *= 4
    f52 = PassiveFunction('超人烈海王2', 'INCREASE', priority=DAMAGE_MULTIPLY, duration=1, process_func=i52)
    def i53(skill:ActiveFunction):
        target = skill.target
        target.damage_list['回避'] *= 2
    f53 = ActiveFunction('超人烈海王3', 'SKILL', priority=DAMAGE_MULTIPLY, duration=2, apply_func=i53)
    s5 = SkillGroup('超人烈海王', SG_PASSIVE, 6, 1, [f51, f52, f53], base_tags={'ultra': 1})
    # ! 秘术 【天文密葬法】（CT9）：一天仅能使用能够一次 制造虚假的月亮，削弱妖怪的力量，3T内战斗环节中，妖怪对手的Atk变为与自身最终结算后相同，无法回避/破解/防御，给予伤害X2/引导宇宙的力量，发出轨道诡异的大量弹幕轰击无法回避/破解/防御 Atk+850，给予伤害X5
    # ? 只能使用一次 3T内对手最终Atk变为和自身最终相同 给予伤害*2
    def i61(skill:ActiveFunction):
        skill.target.opponent.atk = skill.target.atk
    f61 = ActiveFunction('秘术【天文密葬法】1', 'SKILL', priority=ATK_FINAL, duration=3, apply_func=i61)
    def i62(skill:PassiveFunction, message:Message):
        if message.kind == 'HURT':
            message.value *= 2
    f62 = PassiveFunction('秘术【天文密葬法】2', 'INCREASE', priority=DAMAGE_MULTIPLY, duration=3, process_func=i62)
    s61 = SkillGroup('秘术【天文密葬法】 虚假之月', SG_PASSIVE, 9, FOREVER, [f61, f62], base_tags={'ultra': 1, 'uncounterattackable': 1})
    # ? 只能使用一次 atk+850, 给予伤害*5
    def i63(skill:ActiveFunction):
        skill.target.atk += 850
    f63 = ActiveFunction('秘术【天文密葬法】1', 'SKILL', priority=ATK_ADDITION, duration=3, apply_func=i63)
    def i64(skill:PassiveFunction, message:Message):
        if message.kind == 'HURT':
            message.value *= 5
    f64 = PassiveFunction('秘术【天文密葬法】2', 'INCREASE', priority=DAMAGE_MULTIPLY, duration=3, process_func=i64)
    s62 = SkillGroup('秘术【天文密葬法】 弹幕攻击', SG_PASSIVE, 9, FOREVER, [f63, f64], base_tags={'ultra': 1, 'uncounterattackable': 1})
    s6 = s61 if random.random() < 0.5 else s62
    # ! 四千年的传承：不会陷入异常状态，面对近战系、技术系的技能可以进行【1d100】的破解判定，75以上成功
    # ? 不可破解 必杀技不能破解
    def i71(skill:PassiveFunction, message:Message):
        if message.kind != 'SPELL' or 'uncounterattackable' in message.skill.tags:
            return
        s = message.skill
        if 'ultra' in s.tags:
            return
        if 'melee' in s.tags or 'technique' in s.tags:
            target = skill.target
            s = message.skill
            dice = random.randint(1, 100)
            verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
            verdict_offset_from_skill = 0 if 'verdict_offset' not in s.tags else s.tags['verdict_offset']
            verdict = 75  + verdict_offset_from_owner + verdict_offset_from_skill
            logging.info(f'四千年的传承 破解判定：{dice}/{verdict} {"成功" if dice > verdict else "失败"}')
            if dice > verdict:
                message.tags['counterattack'] = 1
    f71 = PassiveFunction('四千年的传承', 'PASSIVE', priority=0, duration=FOREVER, process_func=i71)
    s7 = SkillGroup('四千年的传承', SG_COUNTERATTACK, 1, FOREVER, [f71], base_tags={'uncounterattackable': 1})



    # ! 红 海 皇：超越海王，即为海皇，AtkX2.25，Hp+3。面对所有技能可以进行【1d100】的破解判定，75以上成功：海王是中华武术的巅峰，烈海王又是其中佼佼者，凭借高超的技术使战斗力X1.8
    # ? AtkX2.25 注：必杀技应该是不能破解的
    def i81(skill: ActiveFunction):
        target = skill.target
        target.atk = int(target.atk * 2.25)
    f81 = ActiveFunction('红 海 皇', 'SKILL', priority=ATK_MULTIPLY, duration=FOREVER, apply_func=i81)
    s81 = SkillGroup('红 海 皇', SG_PASSIVE, 1, FOREVER, [f81])
    # ? 所有技能可破解
    def i82(skill:PassiveFunction, message:Message):
        if message.kind != 'SPELL' or 'uncounterattackable' in message.skill.tags:
            return
        s = message.skill
        if 'ultra' in s.tags:
            return
        target = skill.target
        dice = random.randint(1, 100)
        verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
        verdict_offset_from_skill = 0 if 'verdict_offset' not in s.tags else s.tags['verdict_offset']
        verdict = 75 + verdict_offset_from_owner + verdict_offset_from_skill
        logging.info(f'红海皇破解 破解判定：{dice}/{verdict} {"成功" if dice > verdict else "失败"}')
        if dice > verdict:
            message.tags['counterattack'] = 1
    f82 = PassiveFunction('红 海 皇', 'PASSIVE', priority=0, duration=FOREVER, process_func=i82)
    s82 = SkillGroup('红 海 皇', SG_COUNTERATTACK, 1, FOREVER, [f82], base_tags={'uncounterattackable': 1})
    # ! 武之巅峰:（CT5）：Atk+60，3T内可对所有攻击进行【1d100】的破解判定，普通攻击与技能30以上成功，必杀技75以上成功
    # ? 对ATTACK和HURT类，最终伤害有如上概率为0
    def i91(skill: PassiveFunction, message: Message):
        if 'uncounterattackable' in message.tags:
            return
        if message.kind == 'ATTACK' or message.kind == 'HURT':
            target = skill.target
            dice = random.randint(1, 100)
            verdict_offset_from_owner = 0 if 'verdict_offset' not in target.tags else target.tags['verdict_offset']
            verdict_offset_from_message = 0 if 'verdict_offset' not in message.tags else message.tags['verdict_offset']
            verdict_offset = verdict_offset_from_owner + verdict_offset_from_message
            if 'ultra' in message.tags:
                result = dice > 75 + verdict_offset
                logging.info(f'武之巅峰破解：{dice}/{75 + verdict_offset} {"成功" if result else "失败"}')
            else:
                result = dice > 30 + verdict_offset
                logging.info(f'武之巅峰破解：{dice}/{30 + verdict_offset} {"成功" if result else "失败"}')
            if result:
                message.value = 0
    f91 = PassiveFunction('武之巅峰', 'REDUCTION', priority=FINAL_DAMAGE_MULTIPLY, duration=3, process_func=i91)
    s9 = SkillGroup('武之巅峰', SG_PASSIVE, 5, 1, [f91], base_tags={'ultra': 1})
    # ! 消力：习自烈海王的技巧，普通攻击造成的伤害/2（对Atk240以上的对手与拥有特殊技巧的对手无效）
    def i10_1(skill:PassiveFunction, message:Message):
        if (message.kind == 'ATTACK' and 'melee' in message.tags) or message.kind == 'HURT':
            logging.info(f'消力：{message.value}/2={message.value//2}')
            message.value = int(message.value/2)
    f10_1 = PassiveFunction('消力', 'REDUCTION', priority=FINAL_DAMAGE_MULTIPLY, duration=FOREVER, process_func=i10_1)
    s10_ = SkillGroup('消力', SG_PASSIVE, 1, 999, [f10_1])
    # ! 三华【崩山彩极炮】（CT5）：（近战系）给予敌人强烈的三击，造成必中的【2+3d2】的伤害
    # ? 类似花弹
    def i11_1(skill:ActiveFunction):
        dice = sum([random.randint(1, 2), random.randint(1, 2), random.randint(1, 2)])
        logging.info(f'三华【崩山彩极炮】将要造成{dice}点伤害')
        message = Message('ATTACK', dice)
        message.tags['melee'] = 1
        message.tags['skill_attack'] = 1
        skill.target.opponent.process_message(message)
    f11_1 = ActiveFunction('三华【崩山彩极炮】', 'SKILL', priority=ATTACK, duration=1, apply_func=i11_1)
    s11_1 = SkillGroup('三华【崩山彩极炮】', SG_ACTIVE, 5, 5, [f11_1])
    def i11_2(skill:ActiveFunction):
        logging.info(f'三华【崩山彩极炮】将要造成2点必中伤害')
        message = Message('ATTACK', 2)
        message.tags['melee'] = 1
        message.tags['skill_attack'] = 1
        message.tags['uncounterattackable'] = 1
        skill.target.opponent.process_message(message)
    f11_2 = ActiveFunction('三华【崩山彩极炮】', 'SKILL', priority=ATTACK, duration=1, apply_func=i11_2)
    s11_2 = SkillGroup('三华【崩山彩极炮】', SG_ACTIVE, 5, 5, [f11_2], base_tags={'uncounterattackable': 1})
    # ! 彩华【虹色太极拳】（CT4）：（技巧系）发出如波纹一般在地面缓慢扩散流动的气波，由此长时间限制住对手行动。3T内对手Atk-40，本回合对手需进行一次【1d100】的束缚判定，低于30陷入束缚
    def i12_1(skill:ActiveFunction):
        opponent = skill.target.opponent
        opponent.atk -= 40
    f12_1 = ActiveFunction('彩华【虹色太极拳】', 'SKILL', priority=ATK_ADDITION, duration=3, apply_func=i12_1)
    def i12_2(skill:ActiveFunction):
        opponent = skill.target.opponent
        dice = random.randint(1, 100)
        logging.info(f'彩华【虹色太极拳】判定：{dice}/30 {"成功" if dice < 30 else "失败"}')
        if dice < 30:
            skill.target.tags['auto_win'] = 1
    f12_2 = ActiveFunction('彩华【虹色太极拳】', 'SKILL', priority=ATK_ADDITION, duration=1, apply_func=i12_2)
    s12_ = SkillGroup('彩华【虹色太极拳】', SG_ACTIVE, 4, 4, [f12_1, f12_2], base_tags={'technique': 1})
    # ! 攻消力（CT3）：（近战系）以消力技巧对对手造成巨大伤害，本回合Atk+60，造成伤害+2
    def i13_1(skill:ActiveFunction):
        target = skill.target
        target.atk += 60
    f13_1 = ActiveFunction('攻消力', 'SKILL', priority=ATK_ADDITION, duration=1, apply_func=i13_1)
    def i13_2(skill:PassiveFunction, message:Message):
        if message.kind != 'HURT':
            return
        logging.info(f'攻消力伤害+2：{message.value}+2={message.value+2}')
        message.value += 2
    f13_2 = PassiveFunction('攻消力', 'INCREASE', priority=DAMAGE_ADDITION, duration=1, process_func=i13_2)
    s13_ = SkillGroup('攻消力', SG_ACTIVE, 3, 3, [f13_1, f13_2], base_tags={'melee': 1})
    # ! 星气【星脉地转弹】（CT7）：向敌人打出高纯度的巨大彩色气弹：Atk+700,造成伤害X4 可以选择在蓄力后发动，每蓄力1T，Atk+50，蓄力2T以上时本技能无法破解/回避/防御
    # ? 考虑到剧情 固定蓄力2T
    def i14_1(skill:ActiveFunction):
        target = skill.target
        target.atk += 800
    f14_1 = ActiveFunction('星气【星脉地转弹】', 'SKILL', priority=ATK_ADDITION, duration=1, apply_func=i14_1)
    def i14_2(skill:PassiveFunction, message:Message):
        if message.kind != 'HURT':
            return
        logging.info(f'星气【星脉地转弹】伤害×4：{message.value}*4={message.value*4}')
        message.value *= 4
    f14_2 = PassiveFunction('星气【星脉地转弹】', 'INCREASE', priority=DAMAGE_MULTIPLY, duration=1, process_func=i14_2)
    s14_ = SkillGroup('星气【星脉地转弹】', SG_ACTIVE, 9, 9, [f14_1, f14_2], base_tags={'uncounterattackable': 1, 'ultra': 1})
    # ! 华符 【彩光莲华掌】（CT6）：将大量的气打入对手体内再引爆之，造成大伤害的超大打击。Atk+600，造成伤害X3，战斗结算后对方进行【1d100】的内伤判定，30以下Hp减半
    def i15_1(skill:ActiveFunction):
        target = skill.target
        target.atk += 600
    f15_1 = ActiveFunction('华符 【彩光莲华掌】', 'SKILL', priority=ATK_ADDITION, duration=1, apply_func=i15_1)
    def i15_2(skill:PassiveFunction, message:Message):
        if message.kind != 'HURT':
            return
        logging.info(f'华符 【彩光莲华掌】伤害×3：{message.value}*3={message.value*3}')
        message.value *= 3
    f15_2 = PassiveFunction('华符 【彩光莲华掌】', 'INCREASE', priority=DAMAGE_MULTIPLY, duration=1, process_func=i15_2)
    def i15_3(skill:ActiveFunction):
        dice = random.randint(1, 100)
        logging.info('' + f'华符 【彩光莲华掌】内伤：{dice}/30 {"成功" if dice < 30 else "失败"}')
        if dice < 30:
            opponent = skill.target.opponent
            value = opponent.hp - opponent.hp // 2
            message = Message('DAMAGE', value)
            opponent.process_message(message)
    f15_3 = ActiveFunction('华符 【彩光莲华掌】', 'PURSUIT', priority=0, duration=1, apply_func=i15_3)
    s15_ =  SkillGroup('华符 【彩光莲华掌】', SG_ACTIVE, 6, 6, [f15_1, f15_2, f15_3], {'ultra': 1})


    retsu = Character('烈海王', 120, 17, 17)
    meirin = Character('红美铃', 100, 18, 18)

    retsu.register_skill(s1)

    retsu.register_skill(s2)
    retsu.register_skill(s31)
    retsu.register_skill(s32)
    retsu.register_skill(s4)
    retsu.register_skill(s5)
    retsu.register_skill(s6)
    retsu.register_skill(s7)
    meirin.register_skill(s81)
    meirin.register_skill(s82)
    meirin.register_skill(s81)
    meirin.register_skill(s9)

    meirin.register_skill(s10_)
    meirin.register_skill(s11_1)
    meirin.register_skill(s11_2)
    meirin.register_skill(s12_)
    meirin.register_skill(s13_)
    meirin.register_skill(s14_)
    meirin.register_skill(s15_)



    game = Game(retsu, meirin)
    game.start()
    result[game.winner] += 1
    if game.winner == '烈海王':
        turns_total_1[game.turn] += 1
    else:
        turns_total_2[game.turn] += 1

print(result)
print(turns_total_1)
print(turns_total_2)

