# -*- coding: utf-8 -*-
"""闭合环 vs 弧形磁芯的磁路对比图（数据图+磁路示意）——用实测数据说话"""
import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyArrowPatch, Rectangle
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
BLUE, RED, GREEN, GRAY, ORANGE = '#1f4e9c', '#c0392b', '#1e8449', '#555555', '#c98a4b'
MU0 = 4e-7 * math.pi


def savefig(fig, name, dpi=180):
    p = os.path.join(ASSETS, name)
    fig.savefig(p, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('saved', p)


# ================================================================
# 图A：磁路拓扑对比（横截面 + 磁路示意）
# ================================================================
fig = plt.figure(figsize=(13.5, 9.2))
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.30, wspace=0.22)

# ---- (a) 闭合环横截面 ----
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_xlim(-120, 120); ax1.set_ylim(-120, 120)
ax1.set_aspect('equal'); ax1.axis('off')
ax1.add_patch(Circle((0, 0), 105, fc='#fdeede', ec=ORANGE, lw=1.8, zorder=1))
ax1.add_patch(Circle((0, 0), 85, fc='white', ec='none', zorder=2))
ax1.add_patch(Wedge((0, 0), 105, 75, 105, width=20, fc='#7a3b18', ec='none', alpha=0.55, zorder=6))
ax1.add_patch(Circle((0, 0), 105, ec=ORANGE, lw=1.8, fill=False, zorder=5))
ax1.add_patch(Circle((0, 0), 85, ec=ORANGE, lw=1.8, fill=False, zorder=5))
A = 28.87
for t, lab, col in ((90, 'A', RED), (210, 'B', '#7a9cc9'), (330, 'C', '#7a9cc9')):
    ar = math.radians(t)
    ax1.add_patch(Circle((A * math.cos(ar), A * math.sin(ar)), 8, fc=col, ec='k', lw=1, zorder=8))
    ax1.text(A * math.cos(ar) * 1.28, A * math.sin(ar) * 1.28, lab, fontsize=12, ha='center', va='center', zorder=9)
# 气隙标记
ax1.annotate('0.1mm 气隙', xy=(math.radians(90 + 180) * 57.3 / 57.3 * -95, 5), xytext=(-108, -14),
             fontsize=10, color='#8a2a1a',
             arrowprops=dict(arrowstyle='-', color='#8a2a1a', lw=1.2),
             bbox=dict(fc='white', ec='#8a2a1a', lw=0.8, alpha=0.95, pad=2))
# 磁通环流箭头（环向）
for a in (30, 150, 270):
    ar = math.radians(a)
    x, y = 95 * math.cos(ar), 95 * math.sin(ar)
    t2 = ar + math.pi / 2
    ax1.add_patch(FancyArrowPatch((x - 10 * math.cos(t2), y - 10 * math.sin(t2)),
                                  (x + 10 * math.cos(t2), y + 10 * math.sin(t2)),
                                  arrowstyle='-|>', mutation_scale=16, color=BLUE, lw=2.4, zorder=9))
ax1.text(0, 112, '磁通绕环一圈闭合', fontsize=11.5, color=BLUE, ha='center', fontweight='bold')
ax1.set_title('(a) TSC 闭合环：磁路闭合', fontsize=13.5, color=BLUE, fontweight='bold', pad=10)
ax1.text(0, -115, '互感被磁芯放大 16×（气隙限制后）', fontsize=11, color=GREEN, ha='center', fontweight='bold')

# ---- (b) 弧形磁芯横截面 ----
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_xlim(-120, 120); ax2.set_ylim(-120, 120)
ax2.set_aspect('equal'); ax2.axis('off')
ax2.add_patch(Wedge((0, 0), 105, 30, 150, width=20, fc='#fdeede', ec=ORANGE, lw=1.8, zorder=3))
ax2.add_patch(Circle((0, 0), 85, fc='none', ec='none'))
for t, lab, col in ((90, 'A', RED), (210, 'B', '#7a9cc9'), (330, 'C', '#7a9cc9')):
    ar = math.radians(t)
    ax2.add_patch(Circle((A * math.cos(ar), A * math.sin(ar)), 8, fc=col, ec='k', lw=1, zorder=8))
    ax2.text(A * math.cos(ar) * 1.28, A * math.sin(ar) * 1.28, lab, fontsize=12, ha='center', va='center', zorder=9)
# 磁通进弧段、端部泄漏
for a in (60, 120):
    ar = math.radians(a)
    x, y = 60 * math.cos(ar), 60 * math.sin(ar)
    ax2.add_patch(FancyArrowPatch((x, y), (x + 18 * math.cos(ar), y + 18 * math.sin(ar)),
                                  arrowstyle='-|>', mutation_scale=15, color=RED, lw=2.2, zorder=9))
# 端部泄漏箭头（虚线灰）
for a, da in ((30, -35), (150, 35)):
    ar = math.radians(a)
    x, y = 108 * math.cos(ar), 108 * math.sin(ar)
    t2 = math.radians(a + da)
    ax2.add_patch(FancyArrowPatch((x, y), (x + 30 * math.cos(t2), y + 30 * math.sin(t2)),
                                  arrowstyle='-|>', mutation_scale=14, color=GRAY, lw=1.8, ls='--', zorder=9))
ax2.text(-60, 118, '磁通在弧内走', fontsize=11.5, color=RED, ha='center', fontweight='bold')
ax2.text(-58, -118, '端部泄漏（空气回流）', fontsize=11, color=GRAY, ha='center', fontweight='bold')
ax2.set_title('(b) ASC 弧形：磁路不闭合', fontsize=13.5, color=RED, fontweight='bold', pad=10)
ax2.text(60, -115, '互感只放大 4.4×（去磁限制）', fontsize=11, color=RED, ha='center', fontweight='bold')

# ---- (c) 磁路等效模型（电路类比）----
ax3 = fig.add_subplot(gs[1, :])
ax3.set_xlim(0, 14); ax3.set_ylim(0, 5.6); ax3.axis('off')
# 闭合环磁路
y_c = 4.0
box = FancyBboxPatch((0.4, y_c - 0.45), 5.4, 0.9, boxstyle='round,pad=0.06',
                     fc='#eef4fb', ec=BLUE, lw=1.6)
ax3.add_patch(box)
ax3.text(1.0, y_c + 0.28, '闭合环磁路', fontsize=12, color=BLUE, fontweight='bold')
# 磁阻串联
ax3.text(1.0, y_c - 0.12, r'$\Phi = \dfrac{NI}{R_{core}+R_{gap}}$', fontsize=13, color='#222')
ax3.text(3.6, y_c - 0.12, r'$R_{gap}=\dfrac{g}{\mu_0 A}=1.3\times10^{5}$', fontsize=11, color='#8a2a1a')
ax3.text(3.6, y_c + 0.28, r'$R_{core}=\dfrac{l}{\mu_r\mu_0 A}=7.9\times10^{4}$', fontsize=11, color=BLUE)
ax3.text(5.95, y_c, r'$\Rightarrow\ \mu_{eff}=3738$', fontsize=13, color=GREEN, fontweight='bold', va='center')
# 弧形磁路
y_a = 1.6
box = FancyBboxPatch((0.4, y_a - 0.45), 5.4, 0.9, boxstyle='round,pad=0.06',
                     fc='#fdf1ef', ec=RED, lw=1.6)
ax3.add_patch(box)
ax3.text(1.0, y_a + 0.28, '弧形磁路（开路）', fontsize=12, color=RED, fontweight='bold')
ax3.text(1.0, y_a - 0.12, r'$\Phi = \dfrac{NI}{R_{arc}+R_{ret}}$', fontsize=13, color='#222')
ax3.text(3.5, y_a + 0.28, r'$R_{arc}=\dfrac{l_{arc}}{\mu_r\mu_0 A}=2.6\times10^{4}$', fontsize=11, color=RED)
ax3.text(3.5, y_a - 0.12, r'$R_{ret}$ (air) $= 1.3\times10^{8}$', fontsize=11, color=GRAY)
ax3.text(5.95, y_a, r'$\Rightarrow\ \mu_{eff}=37$', fontsize=13, color=RED, fontweight='bold', va='center')
# 右侧结论
ax3.add_patch(FancyBboxPatch((8.6, 1.0), 5.1, 3.8, boxstyle='round,pad=0.1',
                             fc='#f4f6f9', ec='#8899aa', lw=1.5))
ax3.text(11.1, 4.4, '磁路闭合性 = 102 倍差距', fontsize=13, fontweight='bold', ha='center')
rows = [
    ('空气回流磁阻 / 气隙磁阻', '950×', GRAY),
    ('μ_eff(closed) / μ_eff(open)', '102×', BLUE),
    ('弧形位置增益补偿', '28×', RED),
    ('净开路电压比 TSC/ASC', '3.7×', GREEN),
]
for i, (t, v, c) in enumerate(rows):
    yy = 3.8 - i * 0.68
    ax3.text(9.0, yy, t, fontsize=11.5, color='#333', va='center')
    ax3.text(13.2, yy, v, fontsize=13, color=c, fontweight='bold', va='center', ha='right')
ax3.set_title('(c) 等效磁路对比（磁阻串联模型）', fontsize=13.5, fontweight='bold', pad=8)

savefig(fig, 'core_compare_topology.png')

# ================================================================
# 图B：四层数据对比（互感→电压→源阻抗→功率）
# ================================================================
fig, axes = plt.subplots(1, 4, figsize=(15.5, 4.6))
labels = ['裸线圈', 'ASC 弧形', 'TSC 闭合环']
x = np.arange(3)

# 1) 互感/磁链
lam = np.array([9.6e-5, 4.24e-4, 1.5567e-3])
ax = axes[0]
bars = ax.bar(x, lam * 1e3, color=[GRAY, RED, BLUE], width=0.55)
for b, v in zip(bars, lam * 1e3):
    ax.text(b.get_x() + b.get_width() / 2, v * 1.05, '%.3f' % v, ha='center', fontsize=11, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5)
ax.set_ylabel('磁链 λ (mWb·匝)', fontsize=11.5)
ax.set_title('绕组磁链（互感×电流）', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1.9)
for s in ('top', 'right'): ax.spines[s].set_visible(False)

# 2) 开路电压
E = np.array([30, 133, 489])
ax = axes[1]
bars = ax.bar(x, E, color=[GRAY, RED, BLUE], width=0.55)
for b, v in zip(bars, E):
    ax.text(b.get_x() + b.get_width() / 2, v + 12, '%d mV' % v, ha='center', fontsize=11.5, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5)
ax.set_ylabel('开路电压 E (mV 峰)', fontsize=11.5)
ax.set_title('E = ωλ', fontsize=12, fontweight='bold')
ax.set_ylim(0, 580)
for s in ('top', 'right'): ax.spines[s].set_visible(False)

# 3) 源阻抗（对数）
Zs = np.array([0.001, 1.3, 3500])
ax = axes[2]
bars = ax.bar(x, Zs, color=[GRAY, RED, BLUE], width=0.55)
ax.set_yscale('log')
for b, v in zip(bars, Zs):
    ax.text(b.get_x() + b.get_width() / 2, v * 1.5, ('%.1f Ω' % v) if v > 0.1 else '≈0', ha='center', fontsize=11, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5)
ax.set_ylabel('源阻抗 |Z| (Ω，对数)', fontsize=11.5)
ax.set_title('源阻抗：感性 vs 阻性', fontsize=12, fontweight='bold')
ax.set_ylim(0.0005, 30000)
for s in ('top', 'right'): ax.spines[s].set_visible(False)

# 4) 最大功率
P = np.array([0.18, 874, 83])
ax = axes[3]
bars = ax.bar(x, P, color=[GRAY, RED, BLUE], width=0.55)
for b, v in zip(bars, P):
    ax.text(b.get_x() + b.get_width() / 2, v + 20, '%d μW' % v, ha='center', fontsize=11.5, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5)
ax.set_ylabel('单组最大功率 (μW)', fontsize=11.5)
ax.set_title('P_max = E²/4|Z|', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1050)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.text(0.5, -0.30, 'ASC 最优负载 ~10Ω（低压大电流）；TSC 最优 ~648Ω（高压小电流）',
        transform=ax.transAxes, ha='center', fontsize=10, color='#444')

fig.suptitle('同绕组（500匝）· 100A 平衡 · 三种磁芯的四级对比：磁链 → 电压 → 源阻抗 → 功率',
             fontsize=14.5, fontweight='bold', y=1.04)
savefig(fig, 'core_compare_4panel.png')
