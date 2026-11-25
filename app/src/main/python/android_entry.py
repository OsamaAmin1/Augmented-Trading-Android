"""Android in-process adapter. No listener, socket or remote API."""
import asyncio, base64, hashlib, json, os, sys, threading
from pathlib import Path
from urllib.parse import urlsplit, unquote
import httpx
_lock=threading.RLock(); _app=None; _cookies=httpx.Cookies(); _root=None
PAGES={'/','/assessment','/market','/fundamental','/technical','/intelligence','/backtest','/optimizer','/historical','/academy','/progress','/integration'}
def initialize(root, private, force_compat=False):
    global _app,_root
    with _lock:
        if _app is not None:return 'ready'
        _root=Path(root); expected=(_root/'warehouse.sha256').read_text().strip()
        if hashlib.sha256((_root/'warehouse.sqlite').read_bytes()).hexdigest()!=expected:raise RuntimeError('Warehouse integrity check failed')
        sys.path.insert(0,str(_root)); os.environ['INVESTOR_DB']=str(Path(private)/'investors.sqlite')
        # Only runtime imports; batch-generation process pools are not used by the app.
        import scipy.optimize as so
        if force_compat or not hasattr(so,'milp'):
            from android_milp import milp
            so.milp=milp
        import server
        _app=server.app
        return 'ready'

def validate_path(target):
    u=urlsplit(target); p=unquote(u.path)
    if u.scheme or u.netloc or u.fragment or not p.startswith('/') or p.startswith('//') or '\\' in p or any(x in ('.','..') for x in p.split('/')):raise ValueError('Invalid local route')
    return p

async def _dispatch(method,target,body):
    global _cookies
    headers={'Host':'127.0.0.1','Content-Type':'application/json'} if method=='POST' else {'Host':'127.0.0.1'}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=_app,raise_app_exceptions=False),base_url='http://127.0.0.1',cookies=_cookies,follow_redirects=False,trust_env=False) as c:
        r=await c.request(method,target,headers=headers,content=body.encode() if method=='POST' else None)
        _cookies=c.cookies
        return r.status_code,r.headers.get('content-type','application/octet-stream'),r.content

def dispatch(method,target,body=''):
    with _lock:
        try:
            p=validate_path(target)
            if method not in ('GET','POST') or len(body.encode())>262144:raise ValueError('Request rejected')
            if p=='/mobile-help.js' and method=='GET':status,mime,data=200,'application/javascript',(_root/'mobile-help.js').read_bytes()
            elif p=='/mobile-catalogue.js' and method=='GET':status,mime,data=200,'application/javascript',(_root/'mobile-catalogue.js').read_bytes()
            elif p in PAGES or (p.startswith('/icons/') and p.endswith('.svg')) or '/api/' in p or p.startswith('/account/'):
                status,mime,data=asyncio.run(_dispatch(method,target,body))
                if mime.startswith('text/html'):
                    # inject before legacy scripts, retain original server routes and auth checks
                    marker=b'<script src="/mobile-catalogue.js"></script><script src="/mobile-help.js"></script>'
                    data=marker+data if b'<script' not in data else data.replace(b'<script',marker+b'<script',1)
            else:status,mime,data=404,'application/json',b'{"error":"Unknown route"}'
        except ValueError:status,mime,data=400,'application/json',b'{"error":"Invalid local request"}'
        return json.dumps({'status':status,'mime':mime.split(';')[0],'body':base64.b64encode(data).decode('ascii')})
