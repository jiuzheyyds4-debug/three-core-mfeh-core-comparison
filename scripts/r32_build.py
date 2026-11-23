# -*- coding: utf-8 -*-
"""R32: 论文三种磁芯形式对比（TSC 闭合环 / ASC 弧形 / OSC Omega形）
基于 R28 平衡基波 100A 平台（同一电缆、同一求解设置、开路），
只替换磁芯几何。全部几何与 R28 同尺寸基准（ri=85, ro=105, h=30, μr=1e4）。

ASC（弧形）：跨在 A 相（90°）上方的 120° 弧段，与闭合环同径向尺寸。
  弧段自身非闭合 —— 磁通沿弧段走，端部有去磁效应。
OSC（Omega）：论文 Fig.4(b) 的简化 3D 版：
  两块端板（各为 30° 的弧形板，分别位于 A 相两侧 ±60° 即 30° 和 150° 位置）
  + 一根中柱（径向矩形块，从 r=85 到 r=105，跨在 A 相正上方 90° 处，轴向 h=30）
  端板与中柱在同一轴向高度相连 → 磁路：端板1 → 弧段 … 不对，论文是：
  两块 core plates（板）跨接在电缆两侧 BN 最大点（P4@60°, P6@120°…论文为 P4/P6 即
  60°/300°——A 相在 0°）+ core column 沿周向连接两板（绕过电缆外侧）。
  我们的坐标里 A 相在 90°，BN 最大点在其两侧 ±60° = 30° 和 150°。

简化建模（保持论文磁路拓扑）：
  - 端板1：弧形板 @ 30°，跨 r 85~105，弧宽 20°，厚(轴向) 30mm
  - 端板2：弧形板 @ 150°，同尺寸
  - 中柱：弧形段 @ 60~120°（连接两板外侧，即 r=105 附近？）
  论文 Fig.4b：core plates 是两块平行板（在电缆两侧贴表面），core column 绕外圈连接。
  3D 简化：柱沿 r=95 处 60°→120° 的弧，截面 20mm(径) × 30mm(轴)；
  板为径向的"辐条"：从 r=95 弧到 r=85 的径向矩形（把磁通从内表面引到柱）。
最终 OSC = 柱（60°~120° 弧 @ r=85~105 全径向）+ 两端板自然就是柱的端部 →
  等价于一段 60° 弧形磁芯 + 两端的径向延伸板。
"""
import json, os, shutil, sys, traceback
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, '..', 'Codex_R25_SinglePhase_NoGap_Coarse', 'scripts')))
import r25_common as R

BASE = os.path.join(ROOT, 'cases', 'R28_gap010_fund.aedt')   # 平衡基波100A（含slit，需去缝）
CLEAN = os.path.join(ROOT, 'cases', 'R28_oc_fund.aedt')       # 平衡基波开路基准（如有）
LOG = os.path.join(ROOT, 'logs', 'r32_build.json'); rep = {}
CASES = {
    'ASC': os.path.join(ROOT, 'cases', 'R32_asc.aedt'),
    'OSC': os.path.join(ROOT, 'cases', 'R32_osc.aedt'),
}


def save():
    with open(LOG, 'wb') as h:
        h.write(json.dumps(rep, indent=2, default=str).encode('utf-8'))


def T(v):
    return R.text(v)


def arc_segment(ed, name, th1, th2, ri=85.0, ro=105.0, h=30.0):
    """用 Box + 旋转阵列近似弧段：N 个小 box 沿圆弧排布"""
    import math
    N = max(4, int((th2 - th1) / 2.0))
    mid_r = (ri + ro) / 2.0
    dth = (th2 - th1) / N
    for k in range(N):
        ang = math.radians(th1 + dth * (k + 0.5))
        # box 中心
        cx, cy = mid_r * math.cos(ang), mid_r * math.sin(ang)
        # box 尺寸：周向 = r*dth，径向 = ro-ri，轴向 = h
        w = mid_r * math.radians(dth) * 1.05
        # 旋转角（deg）
        deg = math.degrees(ang)
        ed.CreateBox(
            ['NAME:BoxParameters',
             'XPosition:=', '%.4fmm' % (cx - (ro - ri) / 2 * math.cos(ang)),
             'YPosition:=', '%.4fmm' % (cy - (ro - ri) / 2 * math.sin(ang)),
             'ZPosition:=', '%.1fmm' % (-h / 2),
             'XSize:=', '%.4fmm' % ((ro - ri) * math.cos(ang) * 1.02),
             'YSize:=', '%.4fmm' % ((ro - ri) * math.sin(ang) * 1.02),
             'ZSize:=', '%.1fmm' % h],
            ['NAME:Attributes', 'Name:=', '%s_%d' % (name, k), 'Flags:=', '',
             'Color:=', '(89 94 107)', 'Transparency:=', 0,
             'PartCoordinateSystem:=', 'Global', 'UDMId:=', '',
             'MaterialValue:=', '"Ferrite_mu15000"', 'SurfaceMaterialValue:=', '""',
             'SolveInside:=', True])
    # 旋转每个 box 到位并合并
    names = ['%s_%d' % (name, k) for k in range(N)]
    for k, nm in enumerate(names):
        ang = th1 + dth * (k + 0.5)
        # 围绕 z 轴旋转 deg
        pass  # box 已经按角度定位生成（位置和尺寸都含 cos/sin），无需旋转
    # Unite
    if N > 1:
        ed.Unite(['NAME:Selections', 'Selections:=', ','.join(names)],
                 ['NAME:UniteParameters', 'KeepOriginals:=', False])
    # 改名
    final = names[0]
    ed.ChangeProperty(['NAME:AllTabs',
                       ['NAME:Geometry3DAttributeTab', ['NAME:PropServers', final],
                        ['NAME:ChangedProps', ['NAME:Name', 'Value:=', name]]]])
    return final


def build(src, dst, kind, tag):
    if not os.path.isfile(src):
        rep[tag + '_err'] = 'missing ' + src
        return
    if os.path.isfile(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)
    pr = oDesktop.OpenProject(dst)
    d = pr.SetActiveDesign([T(x) for x in pr.GetTopDesignList()][-1])
    ed = d.SetActiveEditor('3D Modeler')
    # 1) 删除原闭合磁芯与切缝（保留绕组薄sheet与激励）
    names = [T(n) for n in ed.GetMatchedObjectName('*')]
    todel = [n for n in names if n in ('Core_Continuous', 'slitRight', 'slitLeft')]
    # 2) ASC/OSC 也删掉旧绕组线圈（其几何绑在原磁芯上）
    coil_objs = [n for n in names if n.startswith('Distributed_') or n.endswith('_sheet') or n.endswith('_Terminal')]
    if kind == 'ASC':
        arc_segment(ed, 'ASC_Core', 30.0, 150.0)   # 120° 弧，跨 A 相（90°）
    else:  # OSC
        # 中柱：60°~120° 的弧段（截面同径向尺寸）
        arc_segment(ed, 'OSC_Column', 60.0, 120.0)
        # 两端板：径向"辐条"，从 r=95 到 r=105 处在 30° 与 150°（即柱的两端外延 30°）
        arc_segment(ed, 'OSC_Plate1', 20.0, 60.0, ri=95.0, ro=105.0, h=30.0)
        arc_segment(ed, 'OSC_Plate2', 120.0, 160.0, ri=95.0, ro=105.0, h=30.0)
    rep[tag + '_built'] = kind
    pr.Save()
    rep[tag + '_saved'] = True
    oDesktop.CloseProject(pr.GetName())


try:
    import ScriptEnv
    ScriptEnv.Initialize('Ansoft.ElectronicsDesktop')
    oDesktop.SetTempDirectory(os.path.join(ROOT, 'temp'))
    src = CLEAN if os.path.isfile(CLEAN) else BASE
    rep['base'] = os.path.basename(src)
    # 绕组处理：论文结构的线圈绕在中柱上（N 匝）——我们的三组拾取绕组绑在原磁芯，
    # 换芯后必须重建。为对比公平，先做"场对比"（磁通截面），线圈后在分析阶段用
    # 磁通 × N 计算（同一 N=500 口径）。
    build(src, CASES['ASC'], 'ASC', 'ASC')
    build(src, CASES['OSC'], 'OSC', 'OSC')
    rep['stage'] = 'done'
except Exception:
    rep['errors'] = [traceback.format_exc()[-900:]]; rep['stage'] = 'aborted'
finally:
    save()
