# -*- coding: utf-8 -*-
"""三磁芯最终对比图：开路电压 + 负载功率曲线 + 源阻抗模型"""
import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
BLUE, RED, GREEN, GRAY = '#1f4e9c', '#c0392b', '#1e8449', '#555555'

fig, axes = plt.subplots(1, 3, figsize=(15.6, 5.2))

# ---------- 1) 开路电压 ----------
labels = ['TSC\n闭合环', 'ASC\n弧形', 'OSC\nΩ形']
E_oc = [489, 133, 131]
ax = axes[0]
bars = ax.bar(labels, E_oc, color=[BLUE, RED, '#c98a4b'], width=0.52)
for b, v in zip(bars, E_oc):
    ax.text(b.get_x() + b.get_width() / 2, v + 12, '%d mV' % v, ha='center', fontsize=13, fontweight='bold')
ax.set_ylabel('开路电压 E (mV 峰)', fontsize=12.5)
ax.set_title('(a) 开路电压\n（同绕组 500 匝，100 A 平衡）', fontsize=12.5, fontweight='bold')
ax.set_ylim(0, 560)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.text(0.5, -0.32, 'TSC 高 3.7×：互感被闭合磁路放大 16×\nASC/OSC：开磁路去磁压低 μ_eff（37 vs 3738）',
        transform=ax.transAxes, ha='center', fontsize=10, color='#444')

# ---------- 2) 功率 vs 负载（实测点+模型曲线）----------
ax = axes[1]
R = np.logspace(0.3, 3.8, 200)
# TSC: 感性源 V=E·R/√(R²+3500²), P=V²/R
E_t, XL = 0.489, 3500.0
P_tsc = (E_t * R / np.sqrt(R * R + XL * XL)) ** 2 / R
# ASC/OSC: 恒压源+铜阻
E_a, r_cu = 0.1332, 1.25
P_asc = (E_a * R / np.sqrt(R * R + r_cu * r_cu)) ** 2 / R
E_o = 0.1311
P_osc = (E_o * R / np.sqrt(R * R + r_cu * r_cu)) ** 2 / R

ax.loglog(R, P_tsc * 1e6, color=BLUE, lw=2.4, label='TSC 闭合环（感性源 ωL=3.5kΩ）')
ax.loglog(R, P_asc * 1e6, color=RED, lw=2.4, label='ASC 弧形（阻性源 ≈1.3Ω）')
ax.loglog(R, P_osc * 1e6, color='#c98a4b', lw=2.4, ls='--', label='OSC Ω形（阻性源）')
# 实测点
Rm = [100, 500, 2000]
Pm = [88.4, 17.7, 4.4]
ax.scatter(Rm, Pm, color=RED, s=70, zorder=6, marker='o', label='ASC 实测')
ax.scatter([100], [85.9], color='#c98a4b', s=80, zorder=6, marker='s', label='OSC 实测')
ax.scatter([648], [83.4], color=BLUE, s=80, zorder=6, marker='^', label='TSC 实测（最优）')
for rr, pp in zip(Rm, Pm):
    ax.annotate('%.0f' % pp, (rr, pp), textcoords='offset points', xytext=(0, 9),
                ha='center', fontsize=10, color=RED, fontweight='bold')
ax.annotate('83.4', (648, 83.4), textcoords='offset points', xytext=(10, -4),
            fontsize=10.5, color=BLUE, fontweight='bold')
ax.set_xlabel('负载电阻 R (Ω，对数)', fontsize=12)
ax.set_ylabel('单组功率 P (μW，对数)', fontsize=12)
ax.set_title('(b) 功率—负载特性（曲线=源模型，点=仿真实测）', fontsize=12.5, fontweight='bold')
ax.legend(fontsize=9.5, loc='lower left', framealpha=0.95)
ax.set_xlim(2, 4000)
ax.grid(True, which='both', alpha=0.25)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.text(0.5, -0.30, 'ASC/OSC 最优 ~10Ω：P≈3.5mW（TSC 的 10×）\nTSC 峰值 648Ω：83μW 后被 ωL 压死',
        transform=ax.transAxes, ha='center', fontsize=10, color='#444')

# ---------- 3) 峰值功率对比 + 功率密度 ----------
ax = axes[2]
labels2 = ['TSC\n闭合环', 'ASC\n弧形', 'OSC\nΩ形']
Pmax = [83.4, 874, 850]
pdens = [0.001, 0.015, 0.014]
x = np.arange(3)
bars = ax.bar(x, Pmax, color=[BLUE, RED, '#c98a4b'], width=0.52)
for b, v in zip(bars, Pmax):
    ax.text(b.get_x() + b.get_width() / 2, v + 22, '%d μW' % v, ha='center', fontsize=12.5, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels2, fontsize=11)
ax.set_ylabel('单组最大功率 (μW)', fontsize=12.5)
ax.set_title('(c) 最大功率（各自最优负载）', fontsize=12.5, fontweight='bold')
ax.set_ylim(0, 1050)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
# 功率密度标注
for i, (v, d) in enumerate(zip(Pmax, pdens)):
    ax.text(i, -105, '密度 %.3f mW/cm³' % d, ha='center', fontsize=10, color='#555')
ax.text(0.5, -0.38, 'ASC/OSC 最优功率为 TSC 的 10×（源阻抗低 2700×）',
        transform=ax.transAxes, ha='center', fontsize=10, color='#444')

fig.suptitle('三芯电缆取能：TSC / ASC / OSC 三种磁芯实测对比（100 A 平衡，绕组 500 匝）',
             fontsize=15, fontweight='bold', y=1.06)
p = os.path.join(ASSETS, 'core_final_compare.png')
fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
print('saved', p)
