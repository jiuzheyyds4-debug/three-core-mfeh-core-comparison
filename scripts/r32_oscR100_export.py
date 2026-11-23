# -*- coding: utf-8 -*-
import json, os, sys, traceback
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..'))
sys.path.insert(0,os.path.abspath(os.path.join(ROOT,'..','Codex_R25_SinglePhase_NoGap_Coarse','scripts')))
import r25_common as R
CASE=os.path.join(ROOT,'cases','R32_osc_R100.aedt')
LOG=os.path.join(ROOT,'logs','r32_oscR100_export.json'); rep={}
def save():
    with open(LOG,'wb') as h: h.write(json.dumps(rep,indent=2,default=str).encode('utf-8'))
def T(v): return R.text(v)
try:
    import ScriptEnv
    ScriptEnv.Initialize('Ansoft.ElectronicsDesktop')
    oDesktop.SetTempDirectory(os.path.join(ROOT,'temp'))
    pr=oDesktop.OpenProject(CASE)
    d=pr.SetActiveDesign([T(x) for x in pr.GetTopDesignList()][-1])
    rs=d.GetModule('ReportSetup')
    for nm,out in (('R24_Pickup_InducedVoltage','emu_osc_R100.csv'),
                   ('R27_PickupFluxLinkage','flink_osc_R100.csv'),
                   ('R24_All_Winding_Current','cur_osc_R100.csv')):
        try:
            rs.ExportToFile(nm, os.path.join(ROOT,'data',out))
            rep[nm]=os.path.getsize(os.path.join(ROOT,'data',out))
        except Exception as e:
            rep[nm+'_err']=str(e)[:130]
    oDesktop.CloseProject(pr.GetName())
    rep['stage']='done'
except Exception:
    rep['errors']=[traceback.format_exc()[-500:]]; rep['stage']='aborted'
finally: save()
