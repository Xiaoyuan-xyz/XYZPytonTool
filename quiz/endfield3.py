import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from tqdm import tqdm

plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False # 正常显示负号

# 设置随机种子保证可重复性
np.random.seed(42)

def simulate_gacha(first_pool_pulls, strategy, num_simulations=10000):
    """
    模拟抽卡过程
    
    参数:
    first_pool_pulls: 第一个卡池计划抽的抽数
    strategy: 策略类型
        0: 抽到x抽，如果之前出6星则停止
        1: 抽到x抽，如果出6星则补到30或60抽
        2: 抽到x抽，如果之前出up则停止
        3: 抽到x抽，如果出up则补到30或60抽
        4: 无论如何都抽x抽
    num_simulations: 模拟次数
    """
    
    results = {
        'first_up': 0,
        'second_up': 0,
        'total_up': 0,
        'total_6star': 0
    }
    
    # 卡池奖励抽数
    reward_30_pool1 = 10  # 30抽送的本期10抽
    reward_60_pool2 = 10  # 60抽送的下期10抽
    
    for _ in range(num_simulations):
        # 初始化状态
        pity_counter = 31  # 已垫31抽
        guarantee_6star = False
        guarantee_up_pool1 = False
        guarantee_up_pool2 = False
        
        # 第一个卡池的实际可支配抽数
        # 注意：30抽奖励不计入消耗，但会获得额外10抽
        pool1_pulls_remaining = first_pool_pulls
        pool1_actual_pulls = 0
        pool1_reward_triggered = False
        
        first_up_obtained = False
        second_up_obtained = False
        pulled_6star_in_pool1 = False
        
        # === 第一个卡池抽卡 ===
        while pool1_actual_pulls < first_pool_pulls and not first_up_obtained:
            # 检查策略停止条件
            if strategy == 0 and pulled_6star_in_pool1:
                break
            if strategy == 2 and first_up_obtained:
                break
            
            # 实际进行一次抽卡
            pool1_actual_pulls += 1
            
            # 检查是否触发30抽奖励（在抽完第30抽后获得）
            if pool1_actual_pulls == 30 and not pool1_reward_triggered:
                pool1_reward_triggered = True
                # 获得10抽，但不计入当前卡池消耗
                # 这10抽会直接加到当前卡池的抽数中，但不消耗计划抽数
                # 相当于额外多了10抽
                pool1_pulls_remaining += 10
            
            # 计算本次抽卡是否出6星
            if guarantee_6star:
                is_6star = True
                guarantee_6star = False
                pity_counter = 0
            else:
                base_prob = 0.008
                if pity_counter >= 65:
                    # 65抽后概率递增5%
                    increased_prob = base_prob + (pity_counter - 64) * 0.05
                    base_prob = min(increased_prob, 1.0)
                
                is_6star = np.random.random() < base_prob
                
                if is_6star:
                    pity_counter = 0
                else:
                    pity_counter += 1
                    
                    # 检查80抽保底（包含垫抽）
                    if pity_counter >= 80:
                        guarantee_6star = True
            
            if is_6star:
                pulled_6star_in_pool1 = True
                results['total_6star'] += 1
                
                # 判断是否为up
                is_up = np.random.random() < 0.5
                
                # 检查120抽保底up
                if guarantee_up_pool1:
                    is_up = True
                    guarantee_up_pool1 = False
                
                if is_up:
                    first_up_obtained = True
                    results['first_up'] += 1
                    results['total_up'] += 1
                else:
                    # 歪了，记录下一个up保底
                    guarantee_up_pool2 = True
            
            # 策略1和3：如果出了6星，补到30或60抽
            if strategy in [1, 3] and is_6star:
                if pool1_actual_pulls < 30:
                    # 补到30抽
                    extra_needed = 30 - pool1_actual_pulls
                    if extra_needed > 0:
                        pool1_pulls_remaining -= extra_needed
                        pool1_actual_pulls = 30
                        # 补抽的这几次也要计算保底，但简化处理，不详细模拟
                elif pool1_actual_pulls < 60:
                    # 补到60抽
                    extra_needed = 60 - pool1_actual_pulls
                    if extra_needed > 0:
                        pool1_pulls_remaining -= extra_needed
                        pool1_actual_pulls = 60
                break
        
        # 记录第一个卡池结束时已经获得的抽卡奖励状态
        pool1_pulls_done = pool1_actual_pulls
        
        # === 第二个卡池抽卡 ===
        # 剩余抽数 = 总抽数100 - 第一个卡池实际消耗的抽数（不包括奖励）
        # 注意：第一个卡池实际消耗的是 pool1_actual_pulls 抽，但其中可能包含了30抽奖励的10抽
        # 我们需要计算实际消耗的计划抽数
        actual_consumed = min(first_pool_pulls, pool1_actual_pulls)
        if pool1_reward_triggered and pool1_actual_pulls >= 30:
            # 如果触发了30抽奖励，实际消耗的计划抽数是30，但获得了10额外抽
            # 所以实际消耗的计划抽数应该是 min(first_pool_pulls, 30)
            actual_consumed = min(first_pool_pulls, 30)
            if pool1_actual_pulls > 30:
                # 如果继续抽了，超过30的部分消耗计划抽数
                actual_consumed += (pool1_actual_pulls - 30)
        
        remaining_pulls = 100 - actual_consumed
        
        if remaining_pulls > 0:
            # 第二个卡池的抽卡
            pool2_pulls = 0
            pool2_reward_60_triggered = False
            guarantee_up_pool2_current = guarantee_up_pool2
            
            while pool2_pulls < remaining_pulls and not second_up_obtained:
                pool2_pulls += 1
                
                # 检查60抽奖励（在抽完第60抽后获得下期10抽，但这里已经最后一期了，所以这10抽用于当前卡池）
                if pool2_pulls == 60 and not pool2_reward_60_triggered:
                    pool2_reward_60_triggered = True
                    remaining_pulls += 10  # 额外获得10抽
                
                # 计算是否出6星
                if guarantee_6star:
                    is_6star = True
                    guarantee_6star = False
                    pity_counter = 0
                else:
                    base_prob = 0.008
                    if pity_counter >= 65:
                        increased_prob = base_prob + (pity_counter - 64) * 0.05
                        base_prob = min(increased_prob, 1.0)
                    
                    is_6star = np.random.random() < base_prob
                    
                    if is_6star:
                        pity_counter = 0
                    else:
                        pity_counter += 1
                        
                        if pity_counter >= 80:
                            guarantee_6star = True
                
                if is_6star:
                    results['total_6star'] += 1
                    
                    is_up = np.random.random() < 0.5
                    
                    if guarantee_up_pool2_current:
                        is_up = True
                        guarantee_up_pool2_current = False
                    
                    # 检查119抽未出up的保底
                    if pool2_pulls >= 119 and not is_up:
                        is_up = True
                    
                    if is_up:
                        second_up_obtained = True
                        results['second_up'] += 1
                        results['total_up'] += 1
                    else:
                        # 歪了，记录下一个up保底（但这里已经是最后一个卡池，可以不记录）
                        pass
            
            if second_up_obtained:
                results['second_up'] += 1
    
    # 计算平均概率
    for key in results:
        results[key] = results[key] / num_simulations
    
    return results

def analyze_strategies():
    """分析不同策略和抽数分配的效果"""
    
    strategies = [
        "抽到x抽，如果之前出6星则停止",
        "抽到x抽，如果出6星则补到30或60抽",
        "抽到x抽，如果之前出up则停止",
        "抽到x抽，如果出up则补到30或60抽",
        "无论如何都抽x抽"
    ]
    
    # 测试不同的第一个卡池抽数
    first_pool_pulls_range = range(0, 101, 5)
    
    # 存储结果
    all_results = defaultdict(lambda: defaultdict(list))
    
    for strategy_id, strategy_name in enumerate(strategies):
        print(f"分析策略 {strategy_id}: {strategy_name}")
        
        for pulls in tqdm(first_pool_pulls_range):
            results = simulate_gacha(pulls, strategy_id, num_simulations=20000)  # 减少模拟次数以加快速度
            
            all_results[strategy_id]['first_pool_pulls'].append(pulls)
            all_results[strategy_id]['first_up_rate'].append(results['first_up'])
            all_results[strategy_id]['second_up_rate'].append(results['second_up'])
            all_results[strategy_id]['total_up_rate'].append(results['total_up'])
            all_results[strategy_id]['total_6star_rate'].append(results['total_6star'])
    
    return all_results, strategies

def plot_results(all_results, strategies):
    """绘制结果图表"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('终末地抽卡策略分析 - 不同抽数分配的效果', fontsize=16)
    
    colors = ['blue', 'green', 'red', 'purple', 'orange']
    
    # 第一个UP率
    ax1 = axes[0, 0]
    for strategy_id, color in enumerate(colors):
        pulls = all_results[strategy_id]['first_pool_pulls']
        rates = all_results[strategy_id]['first_up_rate']
        ax1.plot(pulls, rates, color=color, label=f'策略{strategy_id}', linewidth=2)
    ax1.set_xlabel('第一个卡池抽数')
    ax1.set_ylabel('第一个UP获得概率')
    ax1.set_title('第一个UP率')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 第二个UP率
    ax2 = axes[0, 1]
    for strategy_id, color in enumerate(colors):
        pulls = all_results[strategy_id]['first_pool_pulls']
        rates = all_results[strategy_id]['second_up_rate']
        ax2.plot(pulls, rates, color=color, label=f'策略{strategy_id}', linewidth=2)
    ax2.set_xlabel('第一个卡池抽数')
    ax2.set_ylabel('第二个UP获得概率')
    ax2.set_title('第二个UP率')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 总UP率
    ax3 = axes[0, 2]
    for strategy_id, color in enumerate(colors):
        pulls = all_results[strategy_id]['first_pool_pulls']
        rates = all_results[strategy_id]['total_up_rate']
        ax3.plot(pulls, rates, color=color, label=f'策略{strategy_id}', linewidth=2)
    ax3.set_xlabel('第一个卡池抽数')
    ax3.set_ylabel('总UP获得概率')
    ax3.set_title('总UP率 (期望值)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 总6星率
    ax4 = axes[1, 0]
    for strategy_id, color in enumerate(colors):
        pulls = all_results[strategy_id]['first_pool_pulls']
        rates = all_results[strategy_id]['total_6star_rate']
        ax4.plot(pulls, rates, color=color, label=f'策略{strategy_id}', linewidth=2)
    ax4.set_xlabel('第一个卡池抽数')
    ax4.set_ylabel('总6星获得概率')
    ax4.set_title('总6星率 (期望值)')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # 找到最优值
    ax5 = axes[1, 1]
    for strategy_id, color in enumerate(colors):
        pulls = all_results[strategy_id]['first_pool_pulls']
        rates = all_results[strategy_id]['total_up_rate']
        max_rate = max(rates)
        max_pulls = pulls[rates.index(max_rate)]
        ax5.scatter(max_pulls, max_rate, color=color, s=100, marker='*', 
                label=f'策略{strategy_id}: {max_pulls}抽, {max_rate:.3f}')
    ax5.set_xlabel('第一个卡池抽数')
    ax5.set_ylabel('最大总UP率')
    ax5.set_title('各策略最优总UP率')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # 策略对比表格
    ax6 = axes[1, 2]
    ax6.axis('tight')
    ax6.axis('off')
    
    # 准备表格数据
    table_data = [['策略', '最优抽数', '第一UP率', '第二UP率', '总UP率', '总6星率']]
    for strategy_id in range(5):
        pulls = all_results[strategy_id]['first_pool_pulls']
        rates = all_results[strategy_id]['total_up_rate']
        max_idx = rates.index(max(rates))
        
        row = [
            f'策略{strategy_id}',
            f'{pulls[max_idx]}',
            f'{all_results[strategy_id]["first_up_rate"][max_idx]:.3f}',
            f'{all_results[strategy_id]["second_up_rate"][max_idx]:.3f}',
            f'{rates[max_idx]:.3f}',
            f'{all_results[strategy_id]["total_6star_rate"][max_idx]:.3f}'
        ]
        table_data.append(row)
    
    table = ax6.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    ax6.set_title('最优结果汇总', y=0.8)
    
    plt.tight_layout()
    plt.savefig('gacha_strategy_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()

def print_optimal_strategies(all_results, strategies):
    """打印最优策略的详细信息"""
    
    print("\n" + "="*80)
    print("终末地抽卡策略分析结果")
    print("="*80)
    
    for strategy_id, strategy_name in enumerate(strategies):
        print(f"\n策略 {strategy_id}: {strategy_name}")
        print("-" * 60)
        
        pulls = all_results[strategy_id]['first_pool_pulls']
        total_up_rates = all_results[strategy_id]['total_up_rate']
        
        # 找到总UP率最高的点
        max_idx = np.argmax(total_up_rates)
        optimal_pulls = pulls[max_idx]
        max_up_rate = total_up_rates[max_idx]
        
        # 找到多个接近最优的点
        near_optimal = []
        for i, rate in enumerate(total_up_rates):
            if rate >= max_up_rate * 0.99:  # 99%的最优值
                near_optimal.append((pulls[i], rate))
        
        print(f"  最优抽数分配: 第一个卡池抽 {optimal_pulls} 抽")
        print(f"  期望总UP数: {max_up_rate:.4f}")
        print(f"  第一UP率: {all_results[strategy_id]['first_up_rate'][max_idx]:.4f}")
        print(f"  第二UP率: {all_results[strategy_id]['second_up_rate'][max_idx]:.4f}")
        print(f"  总6星率: {all_results[strategy_id]['total_6star_rate'][max_idx]:.4f}")
        
        if len(near_optimal) > 1:
            print(f"\n  接近最优的分配方案:")
            for p, r in near_optimal:
                if p != optimal_pulls:
                    print(f"    第一个卡池抽 {p} 抽 -> 总UP率 {r:.4f}")

def main():
    print("开始分析终末地抽卡策略...")
    print("这将运行多次模拟，请稍候...\n")
    
    all_results, strategies = analyze_strategies()
    plot_results(all_results, strategies)
    print_optimal_strategies(all_results, strategies)
    
    print("\n分析完成！图表已保存为 'gacha_strategy_analysis.png'")

if __name__ == "__main__":
    main()