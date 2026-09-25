"""Prepare the offline Android project on a GitHub-hosted Linux runner.

The reviewed HTML app is packaged inside the APK, never fetched from a website.
Generated files live only in RUNNER_TEMP; source templates stay in GitHub.
"""
from pathlib import Path
import json, os, re, sys

FILES = json.loads(r'''{
 "settings.gradle": "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\ndependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\nrootProject.name = 'ProgressPercent'\ninclude ':app'\n",
 "build.gradle": "plugins { id 'com.android.application' version '8.11.1' apply false }\n",
 "gradle.properties": "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx3g -Dfile.encoding=UTF-8\n",
 "app/build.gradle": "plugins { id 'com.android.application' }\nandroid {\n namespace 'com.jeevesh.progress'\n compileSdk 36\n defaultConfig {\n  applicationId 'com.jeevesh.progress'\n  minSdk 26\n  targetSdk 36\n  versionCode Integer.parseInt(System.getenv('GITHUB_RUN_NUMBER') ?: '1')\n  versionName '1.1.0-preview'\n  testInstrumentationRunner 'androidx.test.runner.AndroidJUnitRunner'\n }\n buildFeatures { buildConfig true }\n buildTypes { release { minifyEnabled false; signingConfig signingConfigs.debug } }\n compileOptions { sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }\n lint { abortOnError true }\n}\ndependencies {\n implementation 'androidx.webkit:webkit:1.14.0'\n androidTestImplementation 'androidx.test.ext:junit:1.2.1'\n androidTestImplementation 'androidx.test:core:1.6.1'\n androidTestImplementation 'androidx.test:runner:1.6.2'\n}\n",
 "app/src/main/AndroidManifest.xml": "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n <application android:label=\"Progress %\" android:icon=\"@drawable/ic_launcher\" android:roundIcon=\"@drawable/ic_launcher\" android:theme=\"@style/AppTheme\" android:allowBackup=\"false\" android:usesCleartextTraffic=\"false\" android:supportsRtl=\"true\">\n  <activity android:name=\".MainActivity\" android:exported=\"true\" android:configChanges=\"orientation|screenSize|keyboardHidden\" android:windowSoftInputMode=\"adjustResize\">\n   <intent-filter><action android:name=\"android.intent.action.MAIN\"/><category android:name=\"android.intent.category.LAUNCHER\"/></intent-filter>\n  </activity>\n </application>\n</manifest>\n",
 "app/src/main/res/values/styles.xml": "<resources><style name=\"AppTheme\" parent=\"android:style/Theme.Material.Light.NoActionBar\">\n <item name=\"android:fontFamily\">sans</item><item name=\"android:colorAccent\">#087F78</item>\n <item name=\"android:windowLightStatusBar\">true</item><item name=\"android:statusBarColor\">#EFF5F7</item>\n <item name=\"android:navigationBarColor\">#FFFFFF</item><item name=\"android:windowActionModeOverlay\">true</item>\n <item name=\"android:windowBackground\">#EFF5F7</item>\n</style></resources>\n",
 "app/src/main/res/drawable/ic_launcher.xml": "<vector xmlns:android=\"http://schemas.android.com/apk/res/android\" android:width=\"108dp\" android:height=\"108dp\" android:viewportWidth=\"108\" android:viewportHeight=\"108\">\n <path android:fillColor=\"#087F78\" android:pathData=\"M0,0h108v108h-108z\"/>\n <path android:strokeColor=\"#FFFFFF\" android:strokeWidth=\"8\" android:strokeLineCap=\"round\" android:pathData=\"M36,77L72,31\"/>\n <path android:fillColor=\"#FFFFFF\" android:pathData=\"M36,25a12,12 0,1 0,0 24a12,12 0,1 0,0 -24M72,59a12,12 0,1 0,0 24a12,12 0,1 0,0 -24\"/>\n <path android:fillColor=\"#087F78\" android:pathData=\"M36,32a5,5 0,1 0,0 10a5,5 0,1 0,0 -10M72,66a5,5 0,1 0,0 10a5,5 0,1 0,0 -10\"/>\n</vector>\n",
 "app/src/main/java/com/jeevesh/progress/MainActivity.java": "package com.jeevesh.progress;\n\nimport android.app.*;\nimport android.content.*;\nimport android.graphics.Color;\nimport android.net.Uri;\nimport android.os.*;\nimport android.print.*;\nimport android.util.AtomicFile;\nimport android.view.*;\nimport android.webkit.*;\nimport android.widget.*;\nimport androidx.webkit.WebViewAssetLoader;\nimport java.io.*;\nimport java.nio.charset.StandardCharsets;\nimport java.util.concurrent.Executors;\nimport org.json.*;\n\npublic class MainActivity extends Activity {\n    private static final String APP = \"https://appassets.androidplatform.net/assets/index.html\";\n    private static final int EXPORT = 10, IMPORT = 11, MAX = 15000000;\n    private WebView web;\n    private AtomicFile data;\n    private String pendingExport;\n    private boolean pickerOpen;\n    private final java.util.concurrent.ExecutorService io = Executors.newSingleThreadExecutor();\n\n    public WebView getWebView() { return web; }\n\n    @Override public void onCreate(Bundle state) {\n        super.onCreate(state);\n        data = new AtomicFile(new File(getFilesDir(), \"progress-v2.json\"));\n        FrameLayout root = new FrameLayout(this);\n        root.setBackgroundColor(Color.rgb(243,245,250));\n        web = new WebView(this);\n        root.addView(web, new FrameLayout.LayoutParams(-1,-1));\n        setContentView(root);\n        root.setOnApplyWindowInsetsListener((v,insets) -> {\n            if (Build.VERSION.SDK_INT >= 30) {\n                android.graphics.Insets safe = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.ime() | WindowInsets.Type.displayCutout());\n                v.setPadding(safe.left,safe.top,safe.right,safe.bottom);\n                return WindowInsets.CONSUMED;\n            }\n            v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());\n            return insets.consumeSystemWindowInsets();\n        });\n        root.requestApplyInsets();\n        WebSettings settings = web.getSettings();\n        settings.setJavaScriptEnabled(true);\n        settings.setDomStorageEnabled(true);\n        settings.setAllowFileAccess(false);\n        settings.setAllowContentAccess(false);\n        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);\n        settings.setSupportMultipleWindows(false);\n        settings.setJavaScriptCanOpenWindowsAutomatically(false);\n        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG);\n        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()\n            .addPathHandler(\"/assets/\", new WebViewAssetLoader.AssetsPathHandler(this)).build();\n        web.setWebViewClient(new WebViewClient() {\n            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {\n                Uri url = request.getUrl();\n                if (APP.equals(url.toString())) {\n                    WebResourceResponse response = loader.shouldInterceptRequest(url);\n                    if (response != null) return response;\n                }\n                return new WebResourceResponse(\"text/plain\",\"UTF-8\",403,\"Blocked\",null,new ByteArrayInputStream(new byte[0]));\n            }\n            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {\n                return !APP.equals(request.getUrl().toString());\n            }\n            @Override public void onReceivedError(WebView view,WebResourceRequest request,WebResourceError error) {\n                if(request.isForMainFrame()) message(\"Could not open the app. Please restart it or update Android System WebView.\");\n            }\n        });\n        web.setWebChromeClient(new WebChromeClient() {\n            @Override public boolean onJsAlert(WebView view,String url,String text,JsResult result) {\n                new AlertDialog.Builder(MainActivity.this).setTitle(\"Progress %\").setMessage(text)\n                    .setPositiveButton(\"OK\",(d,w)->result.confirm()).setOnCancelListener(d->result.cancel()).show();\n                return true;\n            }\n            @Override public boolean onJsConfirm(WebView view,String url,String text,JsResult result) {\n                new AlertDialog.Builder(MainActivity.this).setTitle(\"Progress %\").setMessage(text)\n                    .setPositiveButton(\"Continue\",(d,w)->result.confirm())\n                    .setNegativeButton(\"Cancel\",(d,w)->result.cancel()).setOnCancelListener(d->result.cancel()).show();\n                return true;\n            }\n        });\n        web.addJavascriptInterface(new NativeStore(),\"ProgressAndroid\");\n        web.loadUrl(APP);\n        if (Build.VERSION.SDK_INT >= 33) {\n            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,this::goBack);\n        }\n    }\n\n    private void goBack() {\n        web.evaluateJavascript(\"(function(){if(typeof view!=='undefined'&&view!=='dashboard'){show('dashboard');return true;}return false;})()\",\n            result -> { if(!\"true\".equals(result)) finish(); });\n    }\n    @Override public void onBackPressed() { goBack(); }\n\n    private void message(String text) {\n        runOnUiThread(() -> Toast.makeText(this,text,Toast.LENGTH_LONG).show());\n    }\n    private static String readLimited(InputStream input) throws IOException {\n        if(input==null) throw new IOException(\"No input\");\n        ByteArrayOutputStream out=new ByteArrayOutputStream();\n        byte[] buffer=new byte[8192];\n        int n;\n        while((n=input.read(buffer))!=-1) {\n            if(out.size()+n>MAX) throw new IOException(\"Backup exceeds 15 MB\");\n            out.write(buffer,0,n);\n        }\n        return out.toString(StandardCharsets.UTF_8.name());\n    }\n    public class NativeStore {\n        @JavascriptInterface public synchronized String readState() {\n            try(FileInputStream input=data.openRead()) { return readLimited(input); }\n            catch(FileNotFoundException e) { return null; }\n            catch(Exception e) { return \"{unreadable\"; } // Let the UI preserve rather than overwrite damaged data.\n        }\n        @JavascriptInterface public synchronized boolean writeState(String json) {\n            if(json==null||json.getBytes(StandardCharsets.UTF_8).length>MAX) return false;\n            FileOutputStream output=null;\n            try {\n                JSONObject parsed=new JSONObject(json);\n                if(parsed.getInt(\"version\")!=2) return false;\n                output=data.startWrite();\n                output.write(json.getBytes(StandardCharsets.UTF_8));\n                data.finishWrite(output);\n                return true;\n            } catch(Exception e) { if(output!=null)data.failWrite(output); return false; }\n        }\n        @JavascriptInterface public void exportBackup(String json,String filename) {\n            if(json==null||json.getBytes(StandardCharsets.UTF_8).length>MAX) {message(\"Backup is too large.\");return;}\n            runOnUiThread(()->{\n                if(pickerOpen) { message(\"Finish the current file selection first.\"); return; }\n                pendingExport=json; pickerOpen=true;\n                Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE)\n                    .setType(\"application/json\").putExtra(Intent.EXTRA_TITLE,\"progress-percent-backup.json\");\n                try { startActivityForResult(intent,EXPORT); }\n                catch(ActivityNotFoundException e) { pendingExport=null;pickerOpen=false;message(\"No file picker is available.\"); }\n            });\n        }\n        @JavascriptInterface public void restoreBackup() {\n            runOnUiThread(()->{\n                if(pickerOpen) {message(\"Finish the current file selection first.\");return;}\n                pickerOpen=true;\n                Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType(\"*/*\");\n                try {startActivityForResult(intent,IMPORT);}\n                catch(ActivityNotFoundException e) {pickerOpen=false;message(\"No file picker is available.\");}\n            });\n        }\n        @JavascriptInterface public void printReport() {\n            runOnUiThread(()->{\n                PrintManager manager=(PrintManager)getSystemService(PRINT_SERVICE);\n                if(manager!=null) manager.print(\"Progress report\",web.createPrintDocumentAdapter(\"Progress report\"),new PrintAttributes.Builder().build());\n            });\n        }\n    }\n    @Override protected void onActivityResult(int request,int result,Intent intent) {\n        super.onActivityResult(request,result,intent);\n        if(request!=EXPORT&&request!=IMPORT)return;\n        pickerOpen=false;\n        if(result!=RESULT_OK||intent==null||intent.getData()==null) {\n            pendingExport=null; message(\"File selection cancelled.\"); return;\n        }\n        Uri uri=intent.getData();\n        if(request==EXPORT) {\n            String payload=pendingExport;pendingExport=null;\n            if(payload==null) {message(\"Please export your backup again.\");return;}\n            io.execute(()->{\n                try(OutputStream output=getContentResolver().openOutputStream(uri,\"wt\")) {\n                    if(output==null)throw new IOException(\"No output\");\n                    output.write(payload.getBytes(StandardCharsets.UTF_8));\n                    message(\"Backup saved.\");\n                } catch(Exception e) {message(\"Backup could not be saved. Please try another location.\");}\n            });\n        } else {\n            io.execute(()->{\n                try(InputStream input=getContentResolver().openInputStream(uri)) {\n                    String json=readLimited(input);\n                    runOnUiThread(()->web.evaluateJavascript(\"window.restoreAndroidBackup(\"+JSONObject.quote(json)+\")\",null));\n                } catch(Exception e) {message(\"Could not read this backup. Choose a JSON backup under 15 MB.\");}\n            });\n        }\n    }\n    @Override protected void onPause() {super.onPause();web.onPause();}\n    @Override protected void onResume() {super.onResume();if(web!=null)web.onResume();}\n    @Override protected void onDestroy() {\n        if(web!=null){web.removeJavascriptInterface(\"ProgressAndroid\");web.destroy();}\n        io.shutdown();super.onDestroy();\n    }\n}\n",
 "app/src/androidTest/java/com/jeevesh/progress/ProgressTest.java": "package com.jeevesh.progress;\n\nimport androidx.test.core.app.ActivityScenario;\nimport androidx.test.ext.junit.runners.AndroidJUnit4;\nimport org.junit.Test;\nimport org.junit.runner.RunWith;\nimport static org.junit.Assert.*;\nimport java.util.concurrent.*;\nimport java.util.concurrent.atomic.AtomicReference;\n\n@RunWith(AndroidJUnit4.class)\npublic class ProgressTest {\n    private String js(ActivityScenario<MainActivity> activity,String code) throws Exception {\n        CountDownLatch latch=new CountDownLatch(1);\n        AtomicReference<String> answer=new AtomicReference<>();\n        activity.onActivity(a->a.getWebView().evaluateJavascript(code,result->{answer.set(result);latch.countDown();}));\n        assertTrue(\"JavaScript callback timeout\",latch.await(20,TimeUnit.SECONDS));\n        return answer.get();\n    }\n    private void ready(ActivityScenario<MainActivity> activity) throws Exception {\n        for(int i=0;i<100;i++){\n            if(\"true\".equals(js(activity,\"typeof state !== 'undefined' && !!document.querySelector('#prevWeek')\")))return;\n            Thread.sleep(100);\n        }\n        fail(\"Offline dashboard did not load\");\n    }\n    @Test public void offlineJournalPersistsAndReportsWork() throws Exception {\n        try(ActivityScenario<MainActivity> activity=ActivityScenario.launch(MainActivity.class)){\n            ready(activity);\n            assertEquals(\"true\",js(activity,\"document.querySelector('#pageTitle').textContent === 'Weekly overview'\"));\n            assertEquals(\"true\",js(activity,\"normal(7.2,10) === 72 && difference(72,70) === 2 && normal(null,10) === null\"));\n            assertEquals(\"true\",js(activity,\"monday('2026-01-01') === '2025-12-29'\"));\n            assertEquals(\"true\",js(activity,\"$('#time_family').parentElement.hidden && $('#targetFamily').parentElement.hidden && !$('#dashboard').textContent.includes('Family target')\"));\n            js(activity,\"show('journal'); loadDay(); document.querySelector('#time_sleep_hours').value='8'; document.querySelector('#time_sleep_hours').dispatchEvent(new Event('input')); $('#time_sleep_seconds').value='1'; $('#time_sleep_seconds').dispatchEvent(new Event('input'));\");\n            js(activity,\"$('#tab-body').click(); $('#steps').value='6000'; $('#tab-sleep').click();\");\n            assertEquals(\"true\",js(activity,\"$('#time_sleep').value==='08:00:01' && $('#steps').value==='6000' && !$('#panel-sleep').hidden && $('#panel-body').hidden\"));\n            js(activity,\"$('#clearDraft').click();\");\n            assertEquals(\"true\",js(activity,\"$('#time_sleep').value==='' && $('#time_sleep_hours').value===''\"));\n            js(activity,\"$('#tab-time').click(); $('#time_work_minutes').value='60'; $('#time_work_minutes').dispatchEvent(new Event('input')); $('#tab-sleep').click(); $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"!$('#panel-time').hidden && state.records.length===0\"));\n            js(activity,\"loadDay(); $('#tab-sleep').click();\");\n            js(activity,\"$('#stage_deep_hours').value='1'; $('#stage_deep_hours').dispatchEvent(new Event('input'));\");\n            assertEquals(\"true\",js(activity,\"$('#stage_deep').parentElement.querySelector('.tag').textContent==='Add total sleep'\"));\n            js(activity,\"$('#time_sleep_hours').value='8'; $('#time_sleep_hours').dispatchEvent(new Event('input'));\");\n            assertEquals(\"true\",js(activity,\"$('#stage_deep').parentElement.querySelector('.tag').textContent==='12.5% of sleep'\"));\n\n            js(activity,\"show('journal'); loadDay(); $('#time_sleep').value='08:00:01'; $('#time_work').value='08:00:00'; $('#steps').value='6000'; $('#distance').value='4000'; $('#weight').value='72.125'; $('#height').value='175.1'; $('#complete').checked=true; $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"state.records.length === 1 && state.records[0].time.sleep === 28801 && state.records[0].weight === 72125 && state.records[0].height === 1751\"));\n            js(activity,\"$('#time_work').value='24:00:00'; $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"$('#formError').textContent.includes('exceed 24 hours') && state.records[0].time.work === 28800\"));\n            js(activity,\"$('#time_work').value='08:00:00'; $('#stage_deep').value='09:00:00'; $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"$('#formError').textContent.includes('cannot exceed')\"));\n            activity.recreate(); ready(activity);\n            assertEquals(\"true\",js(activity,\"state.records.length===1 && state.records[0].time.sleep===28801\"));\n            js(activity,\"show('lifetime')\");\n            assertEquals(\"true\",js(activity,\"$('#lifetime').textContent.includes('33.3%') && $('#lifetime').textContent.includes('23.33 years')\"));\n            js(activity,\"show('health')\");\n            assertEquals(\"true\",js(activity,\"$('#health').textContent.includes('72.125') && $('#health').textContent.includes('175.1')\"));\n            js(activity,\"$('#demoBtn').click(); show('dashboard')\");\n            assertEquals(\"true\",js(activity,\"demo && state.records.length === 28 && state.records.every(r=>r.time.family===null && r.archivedFamilySeconds===3600 && r.time.other===5400) && !scores(state.records[0]).some(s=>s.id==='family') && !projection(state.records,70).some(s=>s.key==='family')\"));\n            js(activity,\"$('#demoBtn').click()\");\n            assertEquals(\"true\",js(activity,\"!demo && state.records.length===1\"));\n            js(activity,\"show('settings'); $('#age').value='28'; $('#profileForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"state.profile.age===28\"));\n            activity.recreate(); ready(activity);\n            assertEquals(\"true\",js(activity,\"state.profile.age===28 && state.records.length===1\"));\n        }\n    }\n}\n"
}''')
BOOTSTRAP = r'''
if (!Array.prototype.at) Object.defineProperty(Array.prototype,'at',{value:function(i){i=Math.trunc(i)||0;if(i<0)i+=this.length;return this[i];}});
if (!window.structuredClone) window.structuredClone = value => JSON.parse(JSON.stringify(value));
if (!crypto.randomUUID) crypto.randomUUID = () => ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,c=>(c^crypto.getRandomValues(new Uint8Array(1))[0]&15>>c/4).toString(16));
const appStorage = {
 getItem(key) { return ProgressAndroid.readState(); },
 setItem(key,value) { if(!ProgressAndroid.writeState(value)) throw Error('Could not save data on your phone. Free storage and try again.'); }
};
'''
ANDROID_JS = r'''
download = (data,name) => ProgressAndroid.exportBackup(typeof data==='string'?data:JSON.stringify(data,null,2),name);
$('#importBtn').onclick = () => ProgressAndroid.restoreBackup();
$('#printBtn').onclick = () => {show('dashboard');setTimeout(()=>ProgressAndroid.printReport(),250);};
window.restoreAndroidBackup = json => {
 try {
  const incoming=validateState(JSON.parse(json));
  if(!confirm('Restore this backup? Matching dates and your profile/goals will be replaced. Export your current entries first if you need a copy.')) return;
  const next={...incoming,records:[...new Map([...state.records,...incoming.records].map(r=>[r.date,r])).values()]};
  validateState(next);
  if(!demo) appStorage.setItem(KEY,JSON.stringify(next));
  state=next;readOnly=false;loadError='';$('#backupError').textContent='';loadDay();render();toast('Backup restored');
 } catch(error) {$('#backupError').textContent=error.message;toast('Backup was not restored. Your existing entries are unchanged.');}
};
document.querySelectorAll('[data-view]').forEach(b=>{
 const labels={dashboard:'Overview',journal:'Journal',lifetime:'Lifetime',health:'Sleep',settings:'Profile'};
 b.textContent=labels[b.dataset.view];
});
'''

UX_JS = r'''

(() => {
 $('#time_family').parentElement.hidden=true;
 $('#targetFamily').parentElement.hidden=true;
 const form=$('#dayForm'), fields=[...form.querySelectorAll(':scope > fieldset')];
 $('#journal .card > p').textContent='Log what you know. Leave the rest blank. You can finish your entry later.';
 $('#journal .tag').textContent='Your daily rhythm';
 const sections=[['sleep','Sleep','Rest & recovery'],['time','Time','Work, people & daily life'],['body','Body','Movement & how you feel'],['notes','Notes','Goals & reflections']];
 const tabs=document.createElement('div');tabs.className='entry-tabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Daily entry sections');
 fields[0].after(tabs);
 const panels={};
 function choose(key){
  sections.forEach(([id])=>{panels[id].hidden=id!==key;const b=$('#tab-'+id);b.setAttribute('aria-selected',String(id===key));b.tabIndex=id===key?0:-1});
 }
 sections.forEach(([key,title,sub],i)=>{
  const b=document.createElement('button');b.type='button';b.id='tab-'+key;b.className='entry-tab '+key;b.setAttribute('role','tab');b.setAttribute('aria-controls','panel-'+key);b.textContent=title;b.onclick=()=>choose(key);
  b.onkeydown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?3:(i+(e.key==='ArrowRight'?1:3))%4;choose(sections[n][0]);$('#tab-'+sections[n][0]).focus()}};
  tabs.append(b);const p=document.createElement('div');p.id='panel-'+key;p.className='entry-panel '+key;p.setAttribute('role','tabpanel');p.setAttribute('aria-labelledby',b.id);p.innerHTML='<h3>'+sub+'</h3>';panels[key]=p;form.insertBefore(p,fields[1]);
 });
 const sleepBox=document.createElement('div');sleepBox.className='formgrid';sleepBox.append($('#time_sleep').parentElement);panels.sleep.append(sleepBox);
 const stages=document.createElement('details');stages.className='optional-stages';stages.innerHTML='<summary>Add sleep stages <span class="muted small">Optional</span></summary>';stages.append(fields[2]);panels.sleep.append(stages);
 panels.time.append(fields[1]);fields[1].querySelector('legend').textContent='Time spent today';fields[1].querySelector('p').textContent='Count each activity once. Your total must fit within 24 hours. Previously logged family time is included in Miscellaneous.';
 panels.body.append(fields[3]);fields[3].querySelector('legend').hidden=true;
 panels.notes.append(fields[4],fields[5]);
 const budget=$('#dayBudget');tabs.before(budget);
 const meters=[];
 function safeSleep(){try{return parseDuration($('#time_sleep').value)}catch(e){return null}}
 function refreshShares(){meters.forEach(m=>m.refreshShare())}
 function meter(input){
  const oldLabel=input.parentElement,title=oldLabel.childNodes[0].textContent.trim();
  const card=document.createElement('div');card.className='duration-card';oldLabel.replaceWith(card);
  input.type='hidden';input.removeAttribute('pattern');card.append(input);
  const head=document.createElement('div');head.className='row';const label=document.createElement('strong');label.textContent=title;const share=document.createElement('span');share.className='tag';head.append(label,share);card.append(head);
  const row=document.createElement('div');row.className='duration-parts';card.append(row);
  const parts=['hours','minutes','seconds'].map((unit,i)=>{
   const l=document.createElement('label');l.textContent=unit;
   const n=document.createElement('input');n.id=input.id+'_'+unit;n.type='number';n.inputMode='numeric';n.min='0';n.max=i?'59':'24';n.step='1';n.placeholder='0';n.setAttribute('aria-label',title+' '+unit);l.append(n);row.append(l);if(i===2)l.hidden=true;return n;
  });
  const actions=document.createElement('div');actions.className='quick-values';card.append(actions);
  function refresh(){
   const value=parts.every(n=>n.value===''&&!n.validity.badInput)?null:parts.reduce((s,n,i)=>s+Number(n.value||0)*[3600,60,1][i],0);
   const invalid=parts.some(n=>!n.validity.valid)||value>86400;
   input.value=invalid?'25:00:00':value===null?'':duration(value);
   share.textContent=invalid?'Check time':value===null?'Not logged':pct(value/(input.id.startsWith('stage_')?(safeSleep()||86400):86400)*100)+(input.id.startsWith('stage_')?' of sleep':' of day');
   updateBudget();refreshShares();
  }
  const presets=input.id==='time_sleep'?[6,7,8,9]:input.id==='time_work'?[4,6,8]:[.25,.5,1];
  presets.forEach(h=>{const b=document.createElement('button');b.type='button';b.textContent=h<1?h*60+' min':h+' hr';b.setAttribute('aria-label',title+' '+b.textContent);b.onclick=()=>{parts[0].value=Math.floor(h);parts[1].value=h%1*60;parts[2].value='0';refresh()};actions.append(b)});
  const exact=document.createElement('button');exact.type='button';exact.textContent='Seconds';exact.setAttribute('aria-expanded','false');exact.onclick=()=>{const l=parts[2].parentElement;l.hidden=!l.hidden;exact.setAttribute('aria-expanded',String(!l.hidden));};actions.append(exact);
  const clear=document.createElement('button');clear.type='button';clear.textContent='Clear';clear.setAttribute('aria-label','Clear '+title);clear.onclick=()=>{parts.forEach(n=>n.value='');refresh()};actions.append(clear);
  parts.forEach(n=>n.oninput=refresh);
  function refreshShare(){
   try{const value=parseDuration(input.value),stage=input.id.startsWith('stage_'),base=stage?safeSleep():86400;
    share.textContent=value===null?'Not logged':stage&&!base?'Add total sleep':pct(value/base*100)+(stage?' of sleep':' of day');
   }catch(e){share.textContent='Check time'}
  }
  meters.push({input,parts,refreshShare,sync:()=>{
   const value=parseDuration(input.value);
   parts.forEach((n,i)=>n.value=value===null?'':i===0?Math.floor(value/3600):i===1?Math.floor(value%3600/60):value%60);
   parts[2].parentElement.hidden=!value||value%60===0;exact.setAttribute('aria-expanded',String(!parts[2].parentElement.hidden));
   share.textContent=value===null?'Not logged':pct(value/86400*100)+' of day';
   if(input.id.startsWith('stage_'))share.textContent=value===null?'Not logged':pct(value/(safeSleep()||86400)*100)+' of sleep';
   refreshShare();
  }});
 }
 [...form.querySelectorAll('#timeInputs input,#stageInputs input'),$('#time_sleep')].filter(n=>n.id!=='time_family').forEach(meter);
 const originalLoad=loadDay;loadDay=function(date){originalLoad(date);meters.forEach(m=>m.sync());};
 const originalClear=$('#clearDraft').onclick;$('#clearDraft').onclick=()=>{originalClear();meters.forEach(m=>{m.input.value='';m.sync()});updateBudget()};
 const quick=document.createElement('div');quick.className='quick-values';
 [['Today',0],['Yesterday',1]].forEach(([title,days])=>{const b=document.createElement('button');b.type='button';b.textContent=title;b.onclick=()=>{const d=new Date();d.setDate(d.getDate()-days);loadDay(localDate(d))};quick.append(b)});
 fields[0].append(quick);
 const stepQuick=document.createElement('div');stepQuick.className='quick-values';
 [500,1000,2000].forEach(n=>{const b=document.createElement('button');b.type='button';b.textContent='+'+n.toLocaleString();b.setAttribute('aria-label','Add '+n+' steps');b.onclick=()=>{$('#steps').value=Number($('#steps').value||0)+n};stepQuick.append(b)});$('#steps').after(stepQuick);
 $('#steps').placeholder='e.g. 6000';$('#distance').placeholder='e.g. 4000';$('#weight').placeholder='e.g. 72.5';$('#height').placeholder='e.g. 175';$('#wellbeing').placeholder='0 = low, 10 = great';
 form.querySelectorAll('input[type=number]').forEach(n=>n.inputMode=n.step==='1'?'numeric':'decimal');
 form.addEventListener('invalid',e=>{const panel=e.target.closest('.entry-panel');if(panel)choose(panel.id.replace('panel-',''));if(e.target.parentElement.hidden)e.target.parentElement.hidden=false;const detail=e.target.closest('details');if(detail)detail.open=true;},true);
 const save=form.querySelector('button[type=submit]');save.textContent='Save my day';save.parentElement.classList.add('save-row');
 const originalSubmit=form.onsubmit;form.onsubmit=e=>{originalSubmit(e);if($('#formError').textContent){if($('#formError').textContent.includes('HH:MM:SS'))$('#formError').textContent='Check your hours, minutes and seconds. A duration must be between 0 and 24 hours.';$('#formError').scrollIntoView({block:'center',behavior:'smooth'});}else{meters.forEach(m=>m.sync());save.textContent='Saved ✓';setTimeout(()=>save.textContent='Save my day',1800)}};
 choose('sleep');meters.forEach(m=>m.sync());
})();

'''
UX_CSS = r'''

:root{--bg:#eff5f7;--paper:#ffffff;--ink:#17334a;--muted:#526777;--line:#d6e3e8;--blue:#087f78;--tint:#e3f3ef;--green:#08756b}
.dark{--bg:#101f2b;--paper:#1a2d3d;--ink:#edf7fa;--muted:#b4cbd3;--line:#385363;--blue:#65d8c4;--tint:#24483f;--green:#74ddbb}
.card{border-radius:22px;box-shadow:0 4px 20px #17334a06}.highlight{background:linear-gradient(135deg,#153f60,#087f78);color:#fff}.highlight .muted,.highlight .eyebrow{color:#d9f3ef}
button,input,select{min-height:48px}input,select,textarea{font-size:16px;border-radius:12px}button{border-radius:12px}.primary{box-shadow:0 4px 12px #087f7822}
.entry-tabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:20px 0}
.entry-tab{padding:10px 2px;font-size:14px;border:2px solid transparent;background:var(--bg)}
.entry-tab[aria-selected=true]{background:var(--tint);border-color:var(--blue);color:var(--ink)}
.entry-tab.sleep{border-bottom-color:#9571ca}.entry-tab.time{border-bottom-color:#ce8838}.entry-tab.body{border-bottom-color:#269cad}.entry-tab.notes{border-bottom-color:#6189db}
.entry-panel{border-top:3px solid #9571ca;padding-top:18px}.entry-panel.time{border-color:#ce8838}.entry-panel.body{border-color:#269cad}.entry-panel.notes{border-color:#6189db}
.entry-panel>h3{margin-bottom:18px;font-size:20px}.duration-card{padding:16px;background:var(--bg);border:1px solid var(--line);border-radius:16px;min-width:0}.duration-card .row{gap:5px;margin-bottom:14px}.duration-card .tag{font-size:12px}
.duration-parts{display:flex;gap:10px}.duration-parts label{flex:1;min-width:0;text-transform:capitalize}.duration-parts input{font-size:22px;font-weight:650;padding:10px;text-align:center}
.quick-values{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}.quick-values button{padding:7px 10px;min-height:44px;font-size:13px}
.optional-stages{margin:20px 0;border:1px solid var(--line);border-radius:14px;padding:14px}summary{cursor:pointer;min-height:44px;font-weight:650}summary span{display:block}
#dayBudget{margin:12px 0!important}#dayForm>.check{margin-top:24px;padding:16px;background:var(--bg);border-radius:14px}#dayForm>.check input{min-height:24px;width:24px;flex-shrink:0}
.save-row{display:grid;grid-template-columns:1fr auto}.save-row .primary{padding:14px 20px}
@media(max-width:760px){main{padding:18px 14px 96px}.card{padding:18px}.top{gap:12px}.top h1{font-size:27px}.sidebar{padding:12px 18px}.sidebar .sidefoot{display:none}.sidebar nav{box-shadow:0 -4px 24px #17334a10}.sidebar nav button{font-size:12px}.sidebar nav button.active{box-shadow:inset 0 3px var(--blue)}#journal .formgrid{grid-template-columns:1fr}#journal .card>.row>.tag{display:none}.entry-panel fieldset{margin-top:12px}.duration-card{padding:14px}.save-row{grid-template-columns:1fr}.save-row #clearDraft{background:transparent}.top>.actions{gap:6px}.top>.actions button{font-size:13px;padding:8px 11px}}
@media print{.entry-tabs,.save-row{display:none}}

'''

def prepare(destination):
    root = Path(__file__).resolve().parent.parent
    out = Path(destination).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name, content in FILES.items():
        file = out / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
    html = (root / "index.html").read_text(encoding="utf-8")

    # Keep version-2 backups compatible while retiring the Family category.
    html = html.replace("['family',r.time.family,r.targets.family],", "")
    html = html.replace("['family','Family target'],", "")
    html = html.replace("return Object.entries(seconds).map(", "return Object.entries(seconds).filter(([key])=>key!=='family').map(")
    html = html.replace(" return r;\n}", """ if(r.time.family!==null){r.archivedFamilySeconds=(r.archivedFamilySeconds||0)+r.time.family;r.time.other=(r.time.other||0)+r.time.family;r.time.family=null;}
 return r;
}""", 1)
    html = html.replace("validateRecord(r);const next=structuredClone(state);", "r.archivedFamilySeconds=state.records.find(x=>x.date===r.date)?.archivedFamilySeconds||0;validateRecord(r);const next=structuredClone(state);")

    assert html.count("<script>") == 1, "Review HTML script changes before packaging"
    html = html.replace("localStorage.", "appStorage.")
    html = html.replace('inputmode="numeric"', 'inputmode="text"')
    html = html.replace("<script>", "<script>\n" + BOOTSTRAP, 1)
    html = html.replace("</script>", ANDROID_JS + UX_JS + "\n</script>", 1)
    html = html.replace("Saved in this browser.", "Saved privately on this phone.")
    html = html.replace("Entries stay in this browser and are not sent to GitHub.", "Entries stay in this app and are not sent to GitHub.")
    html = html.replace("Back up before clearing browser data or changing devices.", "Back up before uninstalling, clearing app data, or changing phones.")
    html = html.replace("Could not save. Browser storage may be full or disabled.", "Could not save. Your phone storage may be full.")
    html = re.sub(r'<a href="legacy.html">.*?</a>', '<span>Android app · Offline</span>', html)
    html = html.replace("Your previous tracker and its browser data are preserved in the ", "To transfer website entries, export a version 2 backup there and restore it here. ")
    css = """
    @media(max-width:760px){
      .sidebar{padding:12px 16px;gap:0}
      .sidebar>div:nth-child(2)>.eyebrow{display:none}
      .sidebar nav{position:fixed;bottom:0;left:0;right:0;z-index:30;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;background:var(--paper);border-top:1px solid var(--line);padding:7px 4px;overflow:visible}
      .sidebar nav button{font-size:14px;min-height:48px;padding:8px 2px;text-align:center}
      main{padding-bottom:92px}
      .status{bottom:80px}
    }
    """
    html = html.replace("</style>", css + UX_CSS + "</style>", 1)
    assets = out / "app/src/main/assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "index.html").write_text(html, encoding="utf-8")
    (out / "app-script.js").write_text(html.split("<script>",1)[1].split("</script>",1)[0], encoding="utf-8")
    print(f"Prepared Android source in {out}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python android/prepare.py OUTPUT_DIRECTORY")
    prepare(sys.argv[1])
