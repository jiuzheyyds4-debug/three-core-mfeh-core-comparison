# -*- coding: utf-8 -*-
import json, os, sys, traceback
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..'))
sys.path.insert(0,os.path.abspath(os.path.join(ROOT,'..','Codex_R25_SinglePhase_NoGap_Coarse','scripts')))
import r25_common as R
LOG=os.path.join(ROOT,'logs','r32_fix.json'); rep={}
def save():
    with open(LOG,'wb') as h: h.write(json.dumps(rep,indent=2,default=str).encode('utf-8'))
def T(v): return R.text(v)
def fix(dst,tag):
    pr=oDesktop.OpenProject(dst)
    d=pr.SetActiveDesign([T(x) for x in pr.GetTopDesignList()][-1])
    ed=d.SetActiveEditor('3D Modeler')
    names=[T(n) for n in ed.GetMatchedObjectName('*')]
    todel=[n for n in names if n in ('Core_Continuous','slitRight','slitLeft')]
    if todel:
        ed.Delete(['NAME:Selections','Selections:=',','.join(todel)])
        rep[tag+'_del']=todel
    pr.Save(); oDesktop.CloseProject(pr.GetName())
try:
    import ScriptEnv
    ScriptEnv.Initialize('Ansoft.ElectronicsDesktop')
    oDesktop.SetTempDirectory(os.path.join(ROOT,'temp'))
    fix(os.path.join(ROOT,'cases','R32_asc.aedt'),'ASC')
    fix(os.path.join(ROOT,'cases','R32_osc.aedt'),'OSC')
    rep['stage']='done'
except Exception:
    rep['errors']=[traceback.format_exc()[-600:]]; rep['stage']='aborted'
finally: save()
