"""Desktop Chromium with intercepted virtual origin; not Android WebView validation."""
from pathlib import Path
import sys,tempfile,zipfile,json,csv,base64,concurrent.futures
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(P/'app/src/main/python'));import android_entry as ae
checks=[]
def ck(name,v):checks.append({'test':name,'passed':bool(v)});assert v,name
with tempfile.TemporaryDirectory() as t,concurrent.futures.ThreadPoolExecutor(max_workers=1) as worker,sync_playwright() as pw:
    root=Path(t)/'runtime';root.mkdir()
    with zipfile.ZipFile(P/'app/src/main/assets/runtime.zip') as z:z.extractall(root)
    worker.submit(ae.initialize,str(root),str(Path(t)/'private'),True).result()
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);ctx=browser.new_context(viewport={'width':430,'height':932},device_scale_factor=1);page=None;errors=[];language='en'
    def bridge(source,path,opts):
        return json.loads(worker.submit(ae.dispatch,opts.get('method','GET'),path,opts.get('body','')).result())
    def load(path):
        global page,language
        if page is not None:
            language=page.evaluate("localStorage.getItem('augmented-language')||'en'");page.close()
        page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.expose_binding('localHTTP',bridge)
        obj=json.loads(worker.submit(ae.dispatch,'GET',path,'').result());assert obj['status']==200
        html=base64.b64decode(obj['body']).decode();catalogue=(root/'mobile-catalogue.js').read_text();helpjs=(root/'mobile-help.js').read_text()
        # Browser policy blocks navigation to all HTTP(S) URLs. Use about:blank with real HTML and bridge fetch to the same embedded ASGI adapter.
        pre="<script>Object.defineProperty(window,'localStorage',{value:{value:"+json.dumps(language)+",getItem(){return this.value},setItem(k,v){this.value=v}}});window.fetch=async(path,opts={})=>{let r=await window.localHTTP(path,opts);let bytes=Uint8Array.from(atob(r.body),x=>x.charCodeAt(0));return new Response(bytes,{status:r.status,headers:{'Content-Type':r.mime}})};</script>"
        marker='<script src="/mobile-catalogue.js"></script><script src="/mobile-help.js"></script>'
        html=html.replace(marker,pre+'<script>'+catalogue+'</script><script>'+helpjs+'</script>');page.set_content(html)
    load('/')
    page.locator('#aug-toolbar').wait_for();ck('Toolbar loaded',page.locator('#aug-toolbar').is_visible());page.locator('#alias').fill('brochure-test');page.locator('#password').fill('fictional-testing-password-123');page.locator('#register').click();page.locator('#error').wait_for();page.wait_for_function("document.getElementById('error').textContent.includes('Account created')");page.locator('#signin').click();page.locator('#dashboard').wait_for(state='visible');ck('Login on phone-size view',page.locator('#dashboard').is_visible())
    page.locator('#aug-toolbar button').first.click();ck('Arabic RTL',page.locator('html').get_attribute('dir')=='rtl');ck('Arabic dashboard heading',page.locator('#dashboard h1').inner_text()=='التقييم والتدريب والتقدم');page.screenshot(path=str(P/'preview_dashboard_ar.png'))
    page.locator('#aug-toolbar button').last.click();page.locator('#aug-overlay').wait_for(state='visible');page.locator('#aug-overlay input').fill('RSI 14');ck('Search RSI 14',page.locator('.aug-list-item').count()==1);page.locator('.aug-list-item').click();ck('Arabic metric title',page.locator('#aug-overlay h2').last.inner_text()=='مؤشر القوة النسبية 14');ck('Arabic metric formula',page.locator('#aug-overlay').inner_text().find('وايلدر')>=0);page.screenshot(path=str(P/'preview_help_ar.png'));page.locator('.aug-close').click()
    load('/backtest');page.wait_for_function("document.getElementById('strategy').options.length>0");page.wait_for_timeout(150);ck('Language retained across workspace',page.locator('html').get_attribute('dir')=='rtl');ck('11 executable strategy options',page.locator('#strategy option').count()==11);page.locator('#strategy').select_option('ST-20');ck('Strategy ID unchanged',page.locator('#strategy').input_value()=='ST-20');ck('Arabic strategy option', 'اتباع الاتجاه' in page.locator('#strategy option:checked').inner_text());page.locator('#strategy + .aug-info').click();ck('Strategy contextual help',page.locator('#aug-overlay').inner_text().find('SMA3')>=0);page.locator('.aug-close').click();page.locator('#run').click();page.locator('#results').wait_for(state='visible',timeout=30000);ck('Backtest result in Arabic mode',page.locator('#results').is_visible());page.locator('#aug-toolbar button').first.click();ck('English restored',page.locator('html').get_attribute('dir')=='ltr' and 'Trend Following' in page.locator('#strategy option:checked').inner_text())
    load('/optimizer');page.wait_for_function("document.getElementById('i0').options.length>0");page.locator('#i0').select_option('EGX:ADIB');page.locator('#run').click();page.locator('#results').wait_for(state='visible',timeout=30000);ck('Optimizer result in phone-size view',page.locator('#results').is_visible());page.screenshot(path=str(P/'preview_optimizer_en.png'))
    for path in ['/assessment','/market','/fundamental','/technical','/intelligence','/historical','/academy','/progress','/integration']:
        load(path);page.locator('#aug-toolbar').wait_for();ck('Help toolbar '+path,page.locator('#aug-toolbar').is_visible());page.wait_for_timeout(100)
    ck('No uncaught browser script errors',not errors);print('PASS',len(checks));browser.close()
with (P/'android_browser_checks.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['test','passed']);w.writeheader();w.writerows(checks)
