# -*- coding: utf-8 -*-
"""t=20ms 磁感应强度分布图（改进版：柱坐标→规则笛卡尔网格双线性插值，消除接缝）"""
import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge
from matplotlib.colors import LogNorm

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'T3')
ASSETS = os.path.join(ROOT, 'assets')
A = 28.87


def load_polar(path, zlim=0.51):
    """读 .fld → (rs, phis, 2D array |B| mT)，柱坐标规则网格"""
    g = {}
    for line in open(path, errors='replace').readlines()[2:]:
        q = line.split()
        if len(q) < 6:
            continue
        try:
            r, phi, z, bx, by, bz = [float(x) for x in q[:6]]
        except Exception:
            continue
        if abs(z * 1e3) > zlim:
            continue
        key = (round(r * 1e3, 2), round(math.degrees(phi) % 360, 2))
        B = math.sqrt(bx * bx + by * by + bz * bz) * 1e3
        if key not in g or B > g[key]:
            g[key] = B
    rs = np.array(sorted(set(k[0] for k in g)))
    ps = np.array(sorted(set(k[1] for k in g)))
    Z = np.full((len(rs), len(ps)), np.nan)
    ri = {v: i for i, v in enumerate(rs)}
    pj = {v: j for j, v in enumerate(ps)}
    for (r, p), v in g.items():
        Z[ri[r], pj[p]] = v
    return rs, ps, Z


def bilinear(rs, ps, Z, rq, pq):
    """在 (r, phi) 上双线性插值；越界返回 nan；phi 周期延拓"""
    # 周期延拓 phi
    if ps[0] > 0.01 or ps[-1] < 359.99:
        pass
    rs = np.asarray(rs); ps = np.asarray(ps)
    Zx = np.concatenate([Z, Z[:, :1]], axis=1)
    psx = np.append(ps, ps[0] + 360.0)
    out = np.full(rq.shape, np.nan)
    i = np.clip(np.searchsorted(rs, rq) - 1, 0, len(rs) - 2)
    j = np.clip(np.searchsorted(psx, pq) - 1, 0, len(psx) - 2)
    ok = (rq >= rs[0]) & (rq <= rs[-1]) & (pq >= psx[0]) & (pq <= psx[-1])
    r0 = rs[i]; r1 = rs[i + 1]; p0 = psx[j]; p1 = psx[j + 1]
    tr = np.where(r1 > r0, (rq - r0) / (r1 - r0), 0)
    tp = np.where(p1 > p0, (pq - p0) / (p1 - p0), 0)
    v00 = Zx[i, j]; v01 = Zx[i, j + 1]; v10 = Zx[i + 1, j]; v11 = Zx[i + 1, j + 1]
    v = (v00 * (1 - tr) * (1 - tp) + v01 * (1 - tr) * tp +
         v10 * tr * (1 - tp) + v11 * tr * tp)
    out[ok] = v[ok]
    return out


def build_map(core_f, air_f, N=420, rmax=108):
    """合成磁芯区+空气区的笛卡尔图"""
    xv = np.linspace(-rmax, rmax, N)
    X, Y = np.meshgrid(xv, xv)
    R = np.hypot(X, Y)
    P = np.degrees(np.arctan2(Y, X)) % 360
    Z = np.full(X.shape, np.nan)

    for f, rlo, rhi in ((air_f, 39.0, 85.0), (core_f, 84.9, 105.1)):
        if not os.path.isfile(os.path.join(D, f)):
            continue
        rs, ps, Zl = load_polar(os.path.join(D, f))
        m = (R >= max(rs[0], rlo)) & (R <= min(rs[-1], rhi))
        if not m.any():
            continue
        vals = bilinear(rs, ps, Zl, R[m], P[m])
        Z[m] = vals
    return X, Y, Z


CASES = [
    ('(a) ASC 弧形磁芯（120° 弧，跨 A 相）', 'B_r32_asc_core.fld', 'B_r32_asc_air.fld', 'asc'),
    ('(b) OSC Ω形磁芯（中柱 60~120° + 端板 20~60°/120~160°）',
     'B_r32_osc_core.fld', 'B_r32_osc_air.fld', 'osc'),
]


def draw_core(ax, kind, color='white', lw=2.2, dashed_lw=1.4):
    if kind == 'asc':
        ax.add_patch(Wedge((0, 0), 105, 30, 150, width=20, fill=False, ec=color, lw=lw, zorder=6))
    else:
        ax.add_patch(Wedge((0, 0), 105, 60, 120, width=20, fill=False, ec=color, lw=lw, zorder=6))
        ax.add_patch(Wedge((0, 0), 105, 20, 60, width=10, fill=False, ec=color,
                           lw=dashed_lw, ls='--', zorder=6))
        ax.add_patch(Wedge((0, 0), 105, 120, 160, width=10, fill=False, ec=color,
                           lw=dashed_lw, ls='--', zorder=6))


# ---------------- 图1：全域对数色标 ----------------
fig, axes = plt.subplots(1, 2, figsize=(14.4, 7.0))
for ax, (title, cf, af, kind) in zip(axes, CASES):
    X, Y, Z = build_map(cf, af)
    Zp = np.where(Z > 0.05, Z, np.nan)
    pm = ax.pcolormesh(X, Y, Zp, shading='auto', cmap='turbo',
                       norm=LogNorm(vmin=0.05, vmax=5.0), rasterized=True)
    draw_core(ax, kind, 'white')
    for t, lab, c in ((90, 'A', 'white'), (210, 'B', '#cccccc'), (330, 'C', '#cccccc')):
        ar = math.radians(t)
        ax.add_patch(Circle((A * math.cos(ar), A * math.sin(ar)), 24.5,
                            fill=False, ec=c, lw=1.5, ls=':', zorder=7))
        ax.plot(A * math.cos(ar), A * math.sin(ar), 'o', ms=4, color=c, zorder=8)
        ax.text(A * math.cos(ar) * 1.95, A * math.sin(ar) * 1.95, lab,
                color='white', fontsize=14, fontweight='bold', ha='center', va='center', zorder=9)
    ax.set_aspect('equal')
    ax.set_xlim(-112, 112); ax.set_ylim(-112, 112)
    ax.set_xlabel('x (mm)', fontsize=11); ax.set_ylabel('y (mm)', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=8)
    cb = plt.colorbar(pm, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label('|B| (mT，对数 0.05~5)', fontsize=10); cb.ax.tick_params(labelsize=9)

fig.suptitle('t = 20 ms（A 相峰值 100 A）磁感应强度分布 · 中心平面 z = 0\n'
             '白实线=磁芯，白点线=导体包络，白虚线=OSC 端板',
             fontsize=13.5, fontweight='bold', y=1.03)
p1 = os.path.join(ASSETS, 'B_dist_20ms_asc_osc.png')
fig.savefig(p1, dpi=170, bbox_inches='tight', facecolor='white')
plt.close(fig)
print('saved', p1)

# ---------------- 图2：磁芯区线性色标放大 ----------------
fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.6))
for ax, (title, cf, af, kind) in zip(axes, CASES):
    X, Y, Z = build_map(cf, af, N=520)
    # 只显示 r>82 的磁芯环带
    R = np.hypot(X, Y)
    Zm = np.where((R >= 83) & (R <= 107), Z, np.nan)
    pm = ax.pcolormesh(X, Y, Zm, shading='auto', cmap='turbo',
                       vmin=0, vmax=5.0, rasterized=True)
    draw_core(ax, kind, 'black', 2.0, 1.3)
    for t, lab in ((90, 'A'), (210, 'B'), (330, 'C')):
        ar = math.radians(t)
        ax.text(A * math.cos(ar) * 1.55, A * math.sin(ar) * 1.55, lab,
                fontsize=11, ha='center', va='center', color='#333', zorder=9)
    ax.set_aspect('equal')
    ax.set_xlim(-112, 112); ax.set_ylim(-112, 112)
    ax.set_title(title, fontsize=11.5, fontweight='bold')
    ax.set_xlabel('x (mm)', fontsize=10); ax.set_ylabel('y (mm)', fontsize=10)
    cb = plt.colorbar(pm, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label('|B| (mT)', fontsize=10)

fig.suptitle('磁芯环带放大（线性色标）—— 磁芯内部磁密分布，t = 20 ms',
             fontsize=13.5, fontweight='bold', y=1.02)
p2 = os.path.join(ASSETS, 'B_dist_20ms_core_zoom.png')
fig.savefig(p2, dpi=170, bbox_inches='tight', facecolor='white')
plt.close(fig)
print('saved', p2)

# ---------------- 数值摘要 ----------------
print()
print('=== 磁芯内 B 的统计（r 85~105, |z|<0.5）===')
for title, cf, af, kind in CASES:
    rs, ps, Z = load_polar(os.path.join(D, cf))
    v = Z[~np.isnan(Z)]
    print('  %-24s 均值 %.1f mT  最大 %.1f mT  最小 %.2f mT' % (
        title.split('（')[0].replace('(a) ', '').replace('(b) ', ''), v.mean(), v.max(), v.min()))
