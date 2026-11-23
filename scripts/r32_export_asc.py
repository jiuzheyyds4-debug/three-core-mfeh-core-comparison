# -*- coding: utf-8 -*-
"""R32 导出：ASC/OSC 两种磁芯在 t=20ms 的场（磁芯区域 + 全环形区域）
磁芯区域网格自适应：ASC/OSC 几何不同，用统一大环域导出（r85-105 全环 + z±15），
分析阶段用各自的角度区间积分。"""
import json, os, shutil, sys, traceback
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, '..', 'Codex_R25_SinglePhase_NoGap_Coarse', 'scripts')))
import r25_common as R
LOG = os.path.join(ROOT, 'logs', 'r32_export.json'); rep = {}


def save():
    with open(LOG, 'wb') as h:
        h.write(json.dumps(rep, indent=2, default=str).encode('utf-8'))


def T(v):
    return R.text(v)


def export_case(case, tag, tstr):
    CASE = os.path.join(ROOT, 'cases', case)
    pr = oDesktop.OpenProject(CASE)
    d = pr.SetActiveDesign([T(x) for x in pr.GetTopDesignList()][-1])
    if not os.path.isdir('C:/TempBphi'):
        os.makedirs('C:/TempBphi')

    def exp(out, mn, mx, sz):
        if os.path.isfile(out):
            os.remove(out)
        f = d.GetModule('FieldsReporter'); f.CalcStack('clear'); f.EnterQty('B')
        f.ExportOnGrid(out, mn, mx, sz, 'Setup1 : Transient', ['Time:=', tstr], True, 'Cylindrical')
        return os.path.getsize(out) if os.path.isfile(out) else 0

    # 磁芯径向域（含空气，分析时按角度截取）
    rep[tag + '_core'] = exp('C:/TempBphi/%s_core.fld' % tag,
                             ['85mm', '0deg', '-15mm'], ['105mm', '360deg', '15mm'],
                             ['1mm', '3deg', '1mm'])
    # 电缆近场（看磁芯对场的扰动）
    rep[tag + '_air'] = exp('C:/TempBphi/%s_air.fld' % tag,
                            ['40mm', '0deg', '-20mm'], ['85mm', '360deg', '20mm'],
                            ['2mm', '4deg', '2mm'])
    if rep[tag + '_core'] > 100000:
        shutil.copyfile('C:/TempBphi/%s_core.fld' % tag, os.path.join(ROOT, 'data', 'T3', 'B_%s_core.fld' % tag))
    if rep[tag + '_air'] > 100000:
        shutil.copyfile('C:/TempBphi/%s_air.fld' % tag, os.path.join(ROOT, 'data', 'T3', 'B_%s_air.fld' % tag))
    oDesktop.CloseProject(pr.GetName())


try:
    import ScriptEnv
    ScriptEnv.Initialize('Ansoft.ElectronicsDesktop')
    oDesktop.SetTempDirectory(os.path.join(ROOT, 'temp'))
    export_case('R32_asc.aedt', 'r32_asc', '20ms')
    rep['stage_asc'] = 'done'
    save()
except Exception:
    rep['errors'] = [traceback.format_exc()[-800:]]; rep['stage_asc'] = 'aborted'
finally:
    save()
