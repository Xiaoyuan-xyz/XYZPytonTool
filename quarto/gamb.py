import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import platform
from tqdm import tqdm

# OSに応じた日本語フォント設定
system = platform.system()
if system == 'Darwin':  # macOS
    matplotlib.rcParams['font.family'] = 'Hiragino Sans GB'
elif system == 'Windows':  # Windows
    matplotlib.rcParams['font.family'] = ['Yu Gothic', 'MS Gothic']
else:  # Linux
    matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'IPAGothic']

matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 10

# 乱数シード設定
np.random.seed(42)

# シミュレーションパラメータ
n_players = 5000  # プレイヤー数
n_rounds = 1440    # ゲーム回数
initial_wealth = 100  # 初期資産（円）

# ゲームパラメータ（中輪）
colors = ['青', '黄', '緑', '赤', '紫']
slots = [10, 6, 5, 3, 1, 25]  # 各色のマス数 + 外れ

# 中輪の倍率
middle_odds = {
    '青': 3,
    '黄': 5,
    '緑': 6,
    '赤': 10,
    '紫': 30,
    '外れ': 0
}

# 外輪の倍率分布
outer_slots = [2]*5 + [3]*6 + [5]*3 + [10]*1 + [1]*35
outer_avg = np.mean(outer_slots)  # 1.76

# ケリー最適戦略
f_star = 0.018  # 投資比率
a_i = np.array([0.40, 0.24, 0.20, 0.12, 0.04])  # 賭け金配分割合

# 各プレイヤーの100回ゲームをシミュレーション
final_wealths = np.zeros(n_players)

for player in tqdm(range(n_players)):
    wealth = initial_wealth
    
    for round_num in range(n_rounds):
        # 現在の賭け金
        bet_amount = wealth * f_star
        
        # 各色への賭け金配分
        bets_per_color = bet_amount * a_i
        
        # 中輪の結果
        middle_result = np.random.choice(
            ['青', '黄', '緑', '赤', '紫', '外れ'],
            p=[0.2, 0.12, 0.1, 0.06, 0.02, 0.5]
        )
        
        if middle_result == '外れ':
            # 全損
            wealth -= bet_amount
        else:
            # 当たり：色のインデックスを取得
            color_idx = colors.index(middle_result)
            
            # 外輪の倍率（独立）
            outer_multiplier = np.random.choice(outer_slots)
            
            # 収益計算
            middle_multiplier = middle_odds[middle_result]
            total_multiplier = middle_multiplier * outer_multiplier
            
            # その色の収益
            profit = bets_per_color[color_idx] * total_multiplier
            
            # 資産更新：賭け金回収 + 収益
            wealth = wealth - bet_amount + profit
    
    final_wealths[player] = wealth

# 結果分析
print("=" * 50)
print("モンテカルロシミュレーション結果")
print("=" * 50)
print(f"初期資産: {initial_wealth}円")
print(f"プレイヤー数: {n_players}人")
print(f"ゲーム回数: {n_rounds}回")
print()
print(f"最終資産平均: {np.mean(final_wealths):.2f}円")
print(f"最終資産中央値: {np.median(final_wealths):.2f}円")
print(f"最終資産標準偏差: {np.std(final_wealths):.2f}円")
print()
print(f"最大資産: {np.max(final_wealths):.2f}円")
print(f"最小資産: {np.min(final_wealths):.2f}円")
print(f"破産者数（資産≤10円）: {np.sum(final_wealths <= 10)}人")
print(f"資産倍増以上者数（資産≥200円）: {np.sum(final_wealths >= 200)}人")
print()
print("最終資産パーセンタイル:")
for p in [10, 25, 50, 75, 90]:
    print(f"  {p}%: {np.percentile(final_wealths, p):.2f}円")

# 平均対数収益率
mean_log_return = np.mean(np.log(final_wealths / initial_wealth)) / n_rounds
print(f"\n平均1回あたり対数収益率: {mean_log_return:.6f}")
print(f"幾何平均成長率（1回あたり）: {(np.exp(mean_log_return) - 1)*100:.4f}%")
print("=" * 50)

# 可視化 - 図1: 資産分布
fig1, axes1 = plt.subplots(1, 3, figsize=(15, 5))

# 1. 最終資産分布ヒストグラム
ax1 = axes1[0]
n, bins, patches = ax1.hist(final_wealths, bins=50, alpha=0.7, 
                           color='skyblue', edgecolor='black')
ax1.axvline(np.mean(final_wealths), color='red', linestyle='--', 
           label=f'平均: {np.mean(final_wealths):.2f}円')
ax1.axvline(np.median(final_wealths), color='green', linestyle='--', 
           label=f'中央値: {np.median(final_wealths):.2f}円')
ax1.set_xlabel('最終資産（円）')
ax1.set_ylabel('人数')
ax1.set_title('100回後の資産分布（2500人）')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 対数スケール分布
ax2 = axes1[1]
log_wealth = np.log10(final_wealths + 1)
ax2.hist(log_wealth, bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
ax2.set_xlabel('最終資産の対数値（log₁₀）')
ax2.set_ylabel('人数')
ax2.set_title('資産分布（対数スケール）')
ax2.grid(True, alpha=0.3)

# 対数軸に元の金額を表示するための目盛り
log_ticks = [0, 1, 2, 3, 4]  # 10^0=1, 10^1=10, 10^2=100, 10^3=1000, 10^4=10000
log_tick_labels = ['1', '10', '100', '1000', '10000']
secax = ax2.secondary_xaxis('top')
secax.set_xticks(log_ticks)
secax.set_xticklabels(log_tick_labels)
secax.set_xlabel('実際の金額（円）')

# 3. 分位点グラフ
ax3 = axes1[2]
sorted_wealth = np.sort(final_wealths)
percentiles = np.arange(1, n_players + 1) / n_players * 100
ax3.plot(percentiles, sorted_wealth, 'b-', linewidth=2)
ax3.fill_between(percentiles, 0, sorted_wealth, alpha=0.2, color='blue')
ax3.set_xlabel('パーセンタイル順位（%）')
ax3.set_ylabel('最終資産（円）')
ax3.set_title('資産分位点プロット')
ax3.grid(True, alpha=0.3)

# 参考線
ax3.axhline(initial_wealth, color='gray', linestyle='--', alpha=0.5, label='初期資産')
ax3.axhline(200, color='orange', linestyle='--', alpha=0.5, label='2倍ライン')
ax3.legend()

plt.tight_layout()
plt.savefig('asset_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

# 図2: 資産変動パスの例
fig2, ax2 = plt.subplots(figsize=(10, 6))

# 成功者、普通、失敗者から各2人ずつ選ぶ
sorted_indices = np.argsort(final_wealths)
sample_indices = np.concatenate([
    sorted_indices[:2],  # 最下位2人
    sorted_indices[n_players//2-1:n_players//2+1],  # 中央付近2人
    sorted_indices[-2:]  # トップ2人
])

# 色分け
colors_path = ['red', 'orange', 'blue', 'cyan', 'green', 'purple']
labels = ['最下位1', '最下位2', '中央付近1', '中央付近2', 'トップ1', 'トップ2']

for idx, color, label in zip(sample_indices, colors_path, labels):
    # そのプレイヤーのパスを再シミュレーション
    wealth_path = [initial_wealth]
    wealth = initial_wealth
    
    # 再現用に乱数シードを設定
    rng = np.random.RandomState(idx + 123)
    
    for round_num in range(n_rounds):
        bet_amount = wealth * f_star
        bets_per_color = bet_amount * a_i
        
        middle_result = rng.choice(
            ['青', '黄', '緑', '赤', '紫', '外れ'],
            p=[0.2, 0.12, 0.1, 0.06, 0.02, 0.5]
        )
        
        if middle_result == '外れ':
            wealth -= bet_amount
        else:
            color_idx = colors.index(middle_result)
            outer_multiplier = rng.choice(outer_slots)
            middle_multiplier = middle_odds[middle_result]
            total_multiplier = middle_multiplier * outer_multiplier
            profit = bets_per_color[color_idx] * total_multiplier
            wealth = wealth - bet_amount + profit
        
        wealth_path.append(wealth)
    
    ax2.plot(range(n_rounds + 1), wealth_path, color=color, linewidth=2, alpha=0.8, label=label)

ax2.axhline(initial_wealth, color='black', linestyle='--', alpha=0.5)
ax2.set_xlabel('ゲーム回数')
ax2.set_ylabel('資産（円）')
ax2.set_title('異なる運命をたどった6人の資産変動パス')
ax2.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
ax2.grid(True, alpha=0.3)
ax2.set_yscale('log')  # 対数スケールで表示

# 右側に軸を追加して線形スケールも表示
secaxy = ax2.secondary_yaxis('right')
secaxy.set_ylabel('資産（円） - 線形スケール')

plt.tight_layout()
plt.savefig('wealth_paths_examples.png', dpi=150, bbox_inches='tight')
plt.show()

# 図3: 成功者と失敗者の分布比較
fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

# 成功者の分布（上位20%）
success_threshold = np.percentile(final_wealths, 80)
success_mask = final_wealths >= success_threshold
failure_mask = final_wealths < initial_wealth  # 損失を出した人

ax31 = axes3[0]
success_wealths = final_wealths[success_mask]
failure_wealths = final_wealths[failure_mask]

bins = np.logspace(0, 5, 50)  # 1円から100000円まで対数スケール
ax31.hist(success_wealths, bins=bins, alpha=0.7, color='green', 
         edgecolor='darkgreen', label=f'成功者（上位20%）：{len(success_wealths)}人')
ax31.hist(failure_wealths, bins=bins, alpha=0.7, color='red', 
         edgecolor='darkred', label=f'失敗者（損失）：{len(failure_wealths)}人')
ax31.set_xscale('log')
ax31.set_xlabel('最終資産（円） - 対数スケール')
ax31.set_ylabel('人数')
ax31.set_title('成功者と失敗者の分布比較')
ax31.legend()
ax31.grid(True, alpha=0.3)

# 初期資産からの変化率
ax32 = axes3[1]
returns = (final_wealths - initial_wealth) / initial_wealth * 100  # パーセント

# 収益率のヒストグラム
ax32.hist(returns, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
ax32.axvline(0, color='black', linestyle='--', alpha=0.5, label='損益分岐点')
ax32.axvline(np.mean(returns), color='red', linestyle='--', 
            label=f'平均: {np.mean(returns):.1f}%')
ax32.axvline(np.median(returns), color='green', linestyle='--', 
            label=f'中央値: {np.median(returns):.1f}%')

# 極端な値のためx軸を制限
ax32.set_xlim([-100, 5000])  # -100%から+5000%
ax32.set_xlabel('収益率（%）')
ax32.set_ylabel('人数')
ax32.set_title('収益率分布')
ax32.legend()
ax32.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('success_failure_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# 要約統計
print("\n" + "="*50)
print("シミュレーション結果のまとめ")
print("="*50)
print(f"1. 平均収益率: {np.mean(returns):.2f}%")
print(f"2. 中央値収益率: {np.median(returns):.2f}%")
print(f"3. 正の収益を得たプレイヤー: {np.sum(returns > 0)}人 ({np.sum(returns > 0)/n_players*100:.1f}%)")
print(f"4. 100円以下（実質破産）: {np.sum(final_wealths <= 10)}人 ({np.sum(final_wealths <= 10)/n_players*100:.1f}%)")
print(f"5. 1000円以上（10倍以上）: {np.sum(final_wealths >= 1000)}人 ({np.sum(final_wealths >= 1000)/n_players*100:.1f}%)")
print("="*50)
print("結論: このギャンブルは平均的にはわずかにプラスだが、")
print("      リスクが非常に高く、多くのプレイヤーは損失を被る。")
print("      ケリー公式は最適成長率を保証するが、")
print("      個人の成功を保証するものではない。")