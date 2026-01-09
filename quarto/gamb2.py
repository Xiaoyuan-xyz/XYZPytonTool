import numpy as np
import random
from collections import Counter

# 格子编号 (0-8):
# 0 1 2
# 3 4 5
# 6 7 8

# 8条线
lines = [
    [0, 1, 2],  # 横1
    [3, 4, 5],  # 横2
    [6, 7, 8],  # 横3
    [0, 3, 6],  # 竖1
    [1, 4, 7],  # 竖2
    [2, 5, 8],  # 竖3
    [0, 4, 8],  # 斜1
    [2, 4, 6]   # 斜2
]

def count_completed_lines(selected_cells):
    """计算已完成的线数"""
    count = 0
    for line in lines:
        if all(cell in selected_cells for cell in line):
            count += 1
    return count

def monte_carlo_simulation(max_n=20, trials=100000):
    """蒙特卡洛模拟"""
    # 初始化结果数组
    results = np.zeros((max_n + 1, 9), dtype=np.float64)  # 0-8条线
    expectations = np.zeros(max_n + 1, dtype=np.float64)
    
    for t in range(trials):
        selected = set()  # 已选择的格子集合
        for n in range(max_n + 1):
            # 在第n步时记录状态
            completed = count_completed_lines(selected)
            results[n][completed] += 1
            
            if n < max_n:  # 进行下一步选择
                cell = random.randint(0, 8)
                selected.add(cell)
    
    # 转换为概率
    results /= trials
    
    # 计算期望值
    for n in range(max_n + 1):
        expectations[n] = sum(k * results[n][k] for k in range(9))
    
    return results, expectations

def dp_calculation(max_n=20):
    """动态规划精确计算"""
    states = 512  # 2^9
    line_masks = [sum(1 << cell for cell in line) for line in lines]
    
    def count_completed_dp(mask):
        count = 0
        for line_mask in line_masks:
            if (mask & line_mask) == line_mask:
                count += 1
        return count
    
    dp = np.zeros((max_n + 1, states), dtype=np.float64)
    dp[0][0] = 1.0
    
    for n in range(max_n):
        for mask in range(states):
            if dp[n][mask] == 0:
                continue
            p = dp[n][mask] / 9.0
            for cell in range(9):
                new_mask = mask | (1 << cell)
                dp[n + 1][new_mask] += p
    
    results_dp = np.zeros((max_n + 1, 9), dtype=np.float64)
    expectations_dp = np.zeros(max_n + 1, dtype=np.float64)
    
    for n in range(max_n + 1):
        for mask in range(states):
            if dp[n][mask] == 0:
                continue
            completed = count_completed_dp(mask)
            results_dp[n][completed] += dp[n][mask]
        expectations_dp[n] = sum(k * results_dp[n][k] for k in range(9))
    
    return results_dp, expectations_dp

def compare_results(max_n=15, trials=50000):
    """比较两种方法的结果"""
    print("=" * 80)
    print("蒙特卡洛模拟 (trials = {}) 与动态规划精确计算对比".format(trials))
    print("=" * 80)
    
    # 运行两种计算
    print("正在运行蒙特卡洛模拟...")
    results_mc, expectations_mc = monte_carlo_simulation(max_n, trials)
    
    print("正在运行动态规划计算...")
    results_dp, expectations_dp = dp_calculation(max_n)
    
    # 比较期望值
    print("\n期望值 E[X_n] 对比:")
    print("n\t蒙特卡洛\t动态规划\t差异")
    print("-" * 50)
    for n in range(max_n + 1):
        diff = abs(expectations_mc[n] - expectations_dp[n])
        print(f"{n}\t{expectations_mc[n]:.6f}\t{expectations_dp[n]:.6f}\t{diff:.6f}")
    
    # 比较概率分布（选择几个n值）
    print("\n概率分布对比 (n=5, 10, 15):")
    test_ns = [5, 10, 15]
    
    for n in test_ns:
        print(f"\nn = {n}:")
        print("k\tP_MC(X=k)\tP_DP(X=k)\t差异")
        print("-" * 50)
        for k in range(9):
            if results_dp[n][k] > 0.0001 or results_mc[n][k] > 0.0001:
                diff = abs(results_mc[n][k] - results_dp[n][k])
                print(f"{k}\t{results_mc[n][k]:.6f}\t{results_dp[n][k]:.6f}\t{diff:.6f}")
    
    # 计算总体差异
    print("\n" + "=" * 80)
    print("总体差异统计:")
    
    total_diff = 0
    max_diff = 0
    count = 0
    
    for n in range(max_n + 1):
        for k in range(9):
            if results_dp[n][k] > 0.0001:
                diff = abs(results_mc[n][k] - results_dp[n][k])
                total_diff += diff
                max_diff = max(max_diff, diff)
                count += 1
    
    avg_diff = total_diff / count if count > 0 else 0
    print(f"平均绝对差异: {avg_diff:.6f}")
    print(f"最大绝对差异: {max_diff:.6f}")
    
    # 检查蒙特卡洛的标准误差
    print(f"\n蒙特卡洛模拟的估计标准误差 (基于{trials}次试验):")
    print("理论上，概率p的标准误差约为 sqrt(p(1-p)/N)")
    print(f"对于p≈0.5, SE ≈ {np.sqrt(0.5*0.5/trials):.6f}")
    print(f"对于p≈0.1, SE ≈ {np.sqrt(0.1*0.9/trials):.6f}")
    print(f"对于p≈0.01, SE ≈ {np.sqrt(0.01*0.99/trials):.6f}")

if __name__ == "__main__":
    # 设置随机种子以便结果可重现
    random.seed(42)
    np.random.seed(42)
    
    # 进行比较
    compare_results(max_n=50, trials=50000)
    
    # 额外：输出动态规划的完整概率分布表
    print("\n" + "=" * 80)
    print("动态规划精确计算的前50步概率分布:")
    results_dp, _ = dp_calculation(50)
    print("\nn\t" + "\t".join(f"P(X={k})" for k in range(9)))
    for n in range(16):
        row = [f"{results_dp[n][k]:.6f}" for k in range(9)]
        print(f"{n}\t" + "\t".join(row))