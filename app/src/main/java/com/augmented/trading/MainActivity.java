package com.augmented.trading;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.net.Uri;
import android.webkit.*;
import android.widget.*;
import android.graphics.Color;
import android.view.Gravity;
import android.util.Base64;
import com.chaquo.python.Python;
import com.chaquo.python.PyObject;
import com.chaquo.python.android.AndroidPlatform;
import org.json.JSONObject;
import java.io.*;
import java.util.*;
import java.util.zip.*;

public class MainActivity extends Activity {
    private static final String ORIGIN="https://appassets.androidplatform.net";
    private static final int EXPORT=401;
    private WebView web; private TextView loading; private PyObject engine; private byte[] pendingExport;
    private boolean local(Uri u){return "https".equals(u.getScheme()) && "appassets.androidplatform.net".equals(u.getHost()) && u.getPort()==-1 && u.getUserInfo()==null;}
    @Override public void onCreate(Bundle state){super.onCreate(state);loading=new TextView(this);loading.setText(R.string.loading);loading.setGravity(Gravity.CENTER);loading.setTextSize(18);loading.setBackgroundColor(Color.rgb(244,245,250));setContentView(loading);
        new Thread(()->{try{File runtime=prepare(); if(!Python.isStarted())Python.start(new AndroidPlatform(getApplicationContext())); engine=Python.getInstance().getModule("android_entry");engine.callAttr("initialize",runtime.getAbsolutePath(),new File(getNoBackupFilesDir(),"private").getAbsolutePath());runOnUiThread(()->{if(!isFinishing()&&!isDestroyed())showWeb();});}catch(Exception ex){android.util.Log.e("AugmentedTrading","Local runtime initialization failed",ex);runOnUiThread(()->loading.setText(R.string.error));}},"initialize-local-engine").start();
    }
    private File prepare() throws IOException {
        File runtime=new File(getNoBackupFilesDir(),"runtime-11901");File marker=new File(runtime,".ready");if(marker.isFile())return runtime;
        File temp=new File(getNoBackupFilesDir(),"runtime-11901.tmp");deleteTree(temp);if(!temp.mkdirs())throw new IOException("Cannot prepare app directory");
        try(ZipInputStream zip=new ZipInputStream(getAssets().open("runtime.zip"))){ZipEntry e;byte[] buf=new byte[32768];long total=0;while((e=zip.getNextEntry())!=null){File f=new File(temp,e.getName());if(!f.getCanonicalPath().startsWith(temp.getCanonicalPath()+File.separator))throw new IOException("Unsafe bundle path");if(e.isDirectory()){f.mkdirs();continue;}f.getParentFile().mkdirs();try(OutputStream out=new FileOutputStream(f)){int n;while((n=zip.read(buf))>0){total+=n;if(total>300_000_000)throw new IOException("Bundle too large");out.write(buf,0,n);}}}}
        if(!new File(temp,"warehouse.sqlite").isFile())throw new IOException("Missing database");new File(temp,".ready").createNewFile();deleteTree(runtime);if(!temp.renameTo(runtime))throw new IOException("Unable to install bundled data");return runtime;
    }
    private static void deleteTree(File f){if(f.isDirectory()){File[] children=f.listFiles();if(children!=null)for(File c:children)deleteTree(c);}if(f.exists())f.delete();}
    private synchronized String dispatch(String method,String target,String body){try{return engine.callAttr("dispatch",method,target,body).toString();}catch(Exception e){android.util.Log.e("AugmentedTrading","Local request failed",e);return "{\"status\":500,\"mime\":\"application/json\",\"body\":\"eyJlcnJvciI6IkxvY2FsIGVuZ2luZSBlcnJvciJ9\"}";}}
    private WebResourceResponse denied(){return new WebResourceResponse("text/plain","UTF-8",403,"Forbidden",Collections.singletonMap("Cache-Control","no-store"),new ByteArrayInputStream(new byte[0]));}
    private void showWeb(){web=new WebView(this);WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setJavaScriptCanOpenWindowsAutomatically(false);s.setSupportMultipleWindows(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);s.setCacheMode(WebSettings.LOAD_NO_CACHE);web.setWebChromeClient(new WebChromeClient());WebView.setWebContentsDebuggingEnabled(false);
        web.addJavascriptInterface(new Bridge(),"LocalEngine");web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){return !local(r.getUrl());}
            @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest r){Uri u=r.getUrl();if(!local(u)||!"GET".equals(r.getMethod()))return denied();String t=u.getEncodedPath();if(t==null||t.isEmpty())t="/";if(u.getEncodedQuery()!=null)t+="?"+u.getEncodedQuery();try{JSONObject j=new JSONObject(dispatch("GET",t,""));int status=j.getInt("status");byte[] b=Base64.decode(j.getString("body"),Base64.DEFAULT);if(status==401&&r.isForMainFrame()){runOnUiThread(()->web.loadUrl(ORIGIN+"/"));return denied();}if(status>=300&&status<400)return denied();Map<String,String> headers=new HashMap<>();headers.put("Cache-Control","no-store");headers.put("X-Content-Type-Options","nosniff");headers.put("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'");return new WebResourceResponse(j.getString("mime"),"UTF-8",status,status==200?"OK":"Local response",headers,new ByteArrayInputStream(b));}catch(Exception e){return denied();}}
        });setContentView(web);web.loadUrl(ORIGIN+"/");}
    public final class Bridge {
        @JavascriptInterface public String request(String method,String path,String body){if(path==null||method==null||body==null)return "{}";return dispatch(method,path,body);}
        @JavascriptInterface public void saveJson(String filename,String text){if(text==null||text.length()>5_000_000)return;runOnUiThread(()->{if(pendingExport!=null)return;new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Export private data / تصدير بيانات خاصة").setMessage("The exported JSON may contain private financial information. اختر مكاناً آمناً لحفظ الملف.").setNegativeButton(android.R.string.cancel,null).setPositiveButton(android.R.string.ok,(d,w)->{pendingExport=text.getBytes(java.nio.charset.StandardCharsets.UTF_8);Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,(filename==null?"export.json":filename.replaceAll("[^a-zA-Z0-9_.-]","_")));try{startActivityForResult(i,EXPORT);}catch(Exception e){pendingExport=null;}}).show();});}
    }
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==EXPORT){byte[] bytes=pendingExport;pendingExport=null;if(result==RESULT_OK&&data!=null&&bytes!=null){try(OutputStream out=getContentResolver().openOutputStream(data.getData())){if(out!=null)out.write(bytes);}catch(Exception e){Toast.makeText(this,"Export failed / تعذر التصدير",Toast.LENGTH_LONG).show();}}}}
    @Override public void onBackPressed(){if(web!=null&&web.canGoBack())web.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){if(web!=null){web.removeJavascriptInterface("LocalEngine");web.destroy();web=null;}pendingExport=null;super.onDestroy();}
}
