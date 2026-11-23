# -*- coding: utf-8 -*-
"""R32 OSC 修复：三个部件 Unite 成一个整体（消除端部重叠导致的网格冲突），
然后 Validate 验证。"""
import json, os, sys, traceback
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, '..', 'Codex_R25_SinglePhase_NoGap_Coarse', 'scripts')))
import r25_common as R
CASE = os.path.join(ROOT, 'cases', 'R32_osc.aedt')
LOG = os.path.join(ROOT, 'logs', 'r32_oscfix.json'); rep = {}


def save():
    with open(LOG, 'wb') as h:
        h.write(json.dumps(rep, indent=2, default=str).encode('utf-8'))


def T(v):
    return R.text(v)


try:
    import ScriptEnv
    ScriptEnv.Initialize('Ansoft.ElectronicsDesktop')
    oDesktop.SetTempDirectory(os.path.join(ROOT, 'temp'))
    pr = oDesktop.OpenProject(CASE)
    d = pr.SetActiveDesign([T(x) for x in pr.GetTopDesignList()][-1])
    ed = d.SetActiveEditor('3D Modeler')
    names = [T(n) for n in ed.GetMatchedObjectName('*')]
    parts = [n for n in names if n in ('OSC_Column', 'OSC_Plate1', 'OSC_Plate2')]
    rep['parts'] = parts
    if len(parts) == 3:
        ed.Unite(['NAME:Selections', 'Selections:=', ','.join(parts)],
                 ['NAME:UniteParameters', 'KeepOriginals:=', False])
        rep['united'] = True
        ed.ChangeProperty(['NAME:AllTabs',
                           ['NAME:Geometry3DAttributeTab', ['NAME:PropServers', 'OSC_Column'],
                            ['NAME:ChangedProps', ['NAME:Name', 'Value:=', 'OSC_Core']]]])
        rep['renamed'] = 'OSC_Core'
    # Validate
    try:
        v = d.Validate()
        rep['validate'] = str(v)
    except Exception as e:
        rep['val_err'] = str(e)[:200]
    pr.Save()
    save()
    oDesktop.CloseProject(pr.GetName())
    rep['stage'] = 'done'
except Exception:
    rep['errors'] = [traceback.format_exc()[-600:]]; rep['stage'] = 'aborted'
finally:
    save()
