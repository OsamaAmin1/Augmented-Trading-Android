"""Host-side verification of local adapter, help catalogue and integer compatibility.
Uses isolated temporary data; does not claim an Android device test.
"""
import base64, csv, hashlib, json, math, os, random, sqlite3, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(P/'app/src/main/python'))
import android_entry as ae
from android_milp import milp
from scipy.optimize import milp as native, Bounds, LinearConstraint
checks=[]
def ck(name,value):
    checks.append({'test':name,'passed':bool(value)});assert value,name
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/'runtime';private=Path(td)/'private';root.mkdir()
    with zipfile.ZipFile(P/'app/src/main/assets/runtime.zip') as z:
        ck('ZIP integrity',z.testzip() is None);ck('No private records bundled',not any(n.startswith('private/') for n in z.namelist()));z.extractall(root)
    with sqlite3.connect(root/'warehouse.sqlite') as db:
        ck('Warehouse integrity',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok');ck('72 original tables',db.execute("select count(*) from sqlite_master where type='table'").fetchone()[0]==72)
    sha=hashlib.sha256((root/'warehouse.sqlite').read_bytes()).hexdigest();ck('Warehouse hash',sha==(root/'warehouse.sha256').read_text().strip())
    data=json.loads((root/'help_catalogue.json').read_text());rows=data['entries'];registry=list(csv.DictReader((root/'backtest_registry.csv').open()));ck('All 35 exact strategy IDs',set(r['id'] for r in rows if r['group']=='strategy')==set(r['id'] for r in registry));ck('No duplicate help IDs',len({r['id'] for r in rows})==len(rows));
    for r in rows:
        ck('Bilingual help '+r['id'],all(r[k]['en'].strip() and r[k]['ar'].strip() and any('\u0600'<=c<='\u06ff' for c in r[k]['ar']) for k in ('meaning','use','calculation')) and bool(r['en'] and r['ar']))
    ids={r['id'] for r in rows};ck('Fundamental metric coverage',set(x['metric'] for x in csv.DictReader((root/'fundamental_metrics.csv').open()))<=ids)
    ck('Technical metric coverage',set('interval_return drawdown sma3 sma5 sma20 sma50 sma200 ema5 ema12 ema26 rsi3 rsi14 macd macd_signal macd_hist bb_upper bb_lower support5 resistance5 atr14 stoch14 volume_ratio5 obv'.split())<=ids)
    ck('Initialize embedded engine',ae.initialize(str(root),str(private),True)=='ready')
    def request(method,path,data=None):
        out=json.loads(ae.dispatch(method,path,json.dumps(data) if data is not None else ''));return out['status'],base64.b64decode(out['body'])
    def obj(method,path,data=None):
        status,b=request(method,path,data);return status,json.loads(b)
    ck('External route rejected',request('GET','https://example.com')[0]==400);ck('Traversal rejected',request('GET','/icons/%2e%2e/warehouse.sqlite')[0]==400);ck('Warehouse not exposed',request('GET','/warehouse.sqlite')[0]==404)
    for p in ['/api/profile','/assessment','/market','/fundamental','/technical','/intelligence','/backtest','/optimizer','/historical','/academy','/progress','/integration']:
        ck('Anonymous blocked '+p,request('GET',p)[0]==401)
    status,b=request('GET','/');ck('Home injected help scripts',status==200 and b'/mobile-help.js' in b and b'/mobile-catalogue.js' in b)
    for p in ['/mobile-help.js','/mobile-catalogue.js']:ck('Local asset '+p,request('GET',p)[0]==200)
    creds={'alias':'android-test','password':'fictional-testing-password-123'};ck('Register',obj('POST','/account/register',creds)[0]==200);ck('Sign in',obj('POST','/account/login',creds)[0]==200)
    ck('Persistent auth and zero live authorization',obj('GET','/api/profile')[1]['approved_allocation']==0)
    for p in sorted(ae.PAGES):
        status,b=request('GET',p);ck('Authenticated workspace '+p,status==200 and b'/mobile-help.js' in b)
    for p in ['/api/schema','/api/resume','/market/api/meta','/fundamental/api/catalogue','/technical/api/catalogue','/backtest/api/meta','/historical/api/meta','/historical/api/snapshot?step=0','/academy/api/catalogue','/progress/api/evidence','/integration/api/status']:
        ck('Embedded API '+p,obj('GET',p)[0]==200)
    ck('Academy 31 lessons',len(obj('GET','/academy/api/catalogue')[1]['modules'])==31)
    ck('Historical gate closed',not obj('GET','/historical/api/meta')[1]['gate']['strict_execution_allowed'])
    ck('Candidate experiment acknowledgment',obj('POST','/historical/api/paper',{})[0]==400)
    r=obj('POST','/optimizer/api/run',{'scenario':'WAR-mild','ids':['EGX:ADIB'],'params':{'horizon':20}});ck('Optimizer API executes',r[0]==200 and all(d['status']=='optimal' for d in r[1]['decisions']) and not r[1]['live_authorized'])
    r=obj('POST','/market/api/start',{'scenario':'WAR-mild','capital':100000});ck('Virtual replay starts',r[0]==200);t=r[1]['token'];ck('Virtual buy queued',obj('POST','/market/api/order',{'token':t,'replay_revision':0,'id':'EGX:ADIB','side':'buy','quantity':100})[0]==200);ck('Virtual replay advances',obj('POST','/market/api/advance',{'token':t,'replay_revision':1})[0]==200)
    ck('Private record encrypted',b'WAR-mild' not in (private/'investors.sqlite').read_bytes());ck('Logout',obj('POST','/account/logout',{})[0]==200);ck('Logout revokes',request('GET','/api/profile')[0]==401);ck('Re-login retains virtual replay',obj('POST','/account/login',creds)[0]==200 and len(obj('GET','/api/profile')[1]['replays'])==1)
    ck('Source remains unchanged',hashlib.sha256((root/'warehouse.sqlite').read_bytes()).hexdigest()==sha)
    # Independent enumeration, same frozen financial optimization model with fallback solver.
    import optimizer as opt
    rng=random.Random(1602)
    for j in range(60):
        cash=100000;held=[rng.randrange(0,8)];marks=[10000];f=np.array([[rng.uniform(.8,1.3)] for _ in range(7)]);p=opt.parameters(risk=rng.choice([0,.4,1,2]),reserve=10,asset_cap=70,portfolio_cap=80,turnover=60,alpha=.8);r=opt.optimize(cash,held,marks,f,p);eq=cash+held[0]*marks[0];choices=[]
        for target in range(30):
            b=[max(0,target-held[0])];s=[max(0,held[0]-target)];c,h,_,status=opt.execute(cash,held,marks,b,s,p)
            if status.startswith('rejected'):continue
            loss=1-(c+f[:,0]*h[0]*marks[0])/eq;tail=min(v+np.maximum(loss-v,0).mean()/(1-p['alpha']) for v in [0,*[x for x in loss if x>0]]);choices.append((-loss.mean()-p['risk']*tail)*100)
        ck('Exact enumeration '+str(j),bool(choices) and r['status']=='optimal' and abs(max(choices)-r['objective_pct'])<1e-6)
    for j in range(20):
        # Two-asset bounded integer problems vs original SciPy native MILP.
        c=np.array([rng.uniform(-2,2),rng.uniform(-2,2),1.]); b=Bounds([0,0,0],[6,5,30]); a=LinearConstraint([[1,2,0],[1,-1,-1]],[-np.inf,-np.inf],[8,0]);args=dict(integrality=[1,1,0],bounds=b,constraints=a,options={'time_limit':5,'mip_rel_gap':1e-8});x=milp(c,**args);y=native(c,**args);ck('Native MILP parity '+str(j),x.status==y.status==0 and abs(x.fun-y.fun)<1e-6)
    z=milp(np.array([-1.]),integrality=[1],bounds=Bounds([0],[10]),constraints=LinearConstraint([[1]],[-np.inf],[6]),options={'time_limit':0});ck('Timeout fails closed',z.status!=0 and z.x is None)
with (P/'android_host_checks.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['test','passed']);w.writeheader();w.writerows(checks)
print('PASS',len(checks))
