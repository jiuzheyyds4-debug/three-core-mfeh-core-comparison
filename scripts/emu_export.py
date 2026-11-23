# -*- coding: utf-8 -*-
import json, os, sys, traceback
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..'))
sys.path.insert(0,os.path.abspath(os.path.join(ROOT,'..','Codex_R25_SinglePhase_NoGap_Coarse','scripts')))
import r25_common as R
CASE=os.path.join(ROOT,'cases','R32_asc_R100.aedt')
TAG='asc_R100'
LOG=os.path.join(ROOT,'logs','emu_%s.json'%TAG); rep={}
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
    for repname,out in (('R24_Pickup_InducedVoltage','emu_%s.csv'%TAG),):
        try:
            rs.ExportToFile(repname, os.path.join(ROOT,'data',out))
            rep[repname]=os.path.getsize(os.path.join(ROOT,'data',out))
        except Exception as e:
            rep[repname+'_err']=str(e)[:150]
    oDesktop.CloseProject(pr.GetName())
    rep['stage']='done'
except Exception:
    rep['errors']=[traceback.format_exc()[-500:]]; rep['stage']='aborted'
finally: save()
