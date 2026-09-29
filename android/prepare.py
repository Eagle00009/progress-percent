"""Prepare the offline Android project on a GitHub-hosted Linux runner.

The reviewed HTML app is packaged inside the APK, never fetched from a website.
Generated files live only in RUNNER_TEMP; source templates stay in GitHub.
"""
from pathlib import Path
import json, os, re, sys, subprocess

FILES = json.loads(r'''{
 "settings.gradle": "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\ndependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\nrootProject.name = 'ProgressPercent'\ninclude ':app'\n",
 "build.gradle": "plugins { id 'com.android.application' version '8.11.1' apply false; id 'org.jetbrains.kotlin.android' version '2.1.20' apply false }\n",
 "gradle.properties": "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx3g -Dfile.encoding=UTF-8\n",
 "app/build.gradle": "plugins { id 'com.android.application'; id 'org.jetbrains.kotlin.android' }\nandroid {\n namespace 'com.jeevesh.progress'\n compileSdk 36\n defaultConfig {\n  applicationId 'com.jeevesh.progress'\n  minSdk 26\n  targetSdk 36\n  versionCode Integer.parseInt(System.getenv('GITHUB_RUN_NUMBER') ?: '1')\n  versionName '1.2.0-preview'\n  testInstrumentationRunner 'androidx.test.runner.AndroidJUnitRunner'\n }\n signingConfigs { debug { storeFile file(System.getProperty('user.home') + '/.android/debug.keystore'); storePassword 'android'; keyAlias 'androiddebugkey'; keyPassword 'android' } }\n kotlinOptions { jvmTarget = '17' }\n buildFeatures { buildConfig true }\n buildTypes { release { minifyEnabled false; signingConfig signingConfigs.debug } }\n compileOptions { sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }\n lint { abortOnError true }\n}\ndependencies {\n implementation 'androidx.activity:activity-ktx:1.10.1'\n implementation 'androidx.health.connect:connect-client:1.1.0'\n implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0'\n implementation 'androidx.webkit:webkit:1.14.0'\n androidTestImplementation 'androidx.test.ext:junit:1.2.1'\n androidTestImplementation 'androidx.test:core:1.6.1'\n androidTestImplementation 'androidx.test:runner:1.6.2'\n}\n",
 "app/src/main/AndroidManifest.xml": "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n <uses-permission android:name=\"android.permission.health.READ_STEPS\"/>\n <uses-permission android:name=\"android.permission.health.READ_DISTANCE\"/>\n <uses-permission android:name=\"android.permission.health.READ_SLEEP\"/>\n <uses-permission android:name=\"android.permission.health.READ_HEART_RATE\"/>\n <uses-permission android:name=\"android.permission.health.READ_RESTING_HEART_RATE\"/>\n <uses-permission android:name=\"android.permission.health.READ_ACTIVE_CALORIES_BURNED\"/>\n <uses-permission android:name=\"android.permission.health.READ_TOTAL_CALORIES_BURNED\"/>\n <uses-permission android:name=\"android.permission.health.READ_EXERCISE\"/>\n <uses-permission android:name=\"android.permission.health.READ_WEIGHT\"/>\n <uses-permission android:name=\"android.permission.health.READ_HEIGHT\"/>\n <uses-permission android:name=\"android.permission.health.READ_OXYGEN_SATURATION\"/>\n <uses-permission android:name=\"android.permission.health.READ_HEALTH_DATA_HISTORY\"/>\n <queries><package android:name=\"com.google.android.apps.healthdata\"/></queries>\n <application android:label=\"Progress %\" android:icon=\"@drawable/ic_launcher\" android:roundIcon=\"@drawable/ic_launcher\" android:theme=\"@style/AppTheme\" android:allowBackup=\"false\" android:usesCleartextTraffic=\"false\" android:supportsRtl=\"true\">\n  <activity android:name=\".MainActivity\" android:exported=\"true\" android:configChanges=\"orientation|screenSize|keyboardHidden\" android:windowSoftInputMode=\"adjustResize\">\n   <intent-filter><action android:name=\"android.intent.action.MAIN\"/><category android:name=\"android.intent.category.LAUNCHER\"/></intent-filter>\n  </activity>\n <activity android:name=\".HealthPrivacyActivity\" android:exported=\"true\">\n <intent-filter><action android:name=\"androidx.health.ACTION_SHOW_PERMISSIONS_RATIONALE\"/></intent-filter>\n </activity>\n <activity-alias android:name=\".ViewPermissionUsageActivity\" android:exported=\"true\" android:targetActivity=\".HealthPrivacyActivity\" android:permission=\"android.permission.START_VIEW_PERMISSION_USAGE\">\n <intent-filter><action android:name=\"android.intent.action.VIEW_PERMISSION_USAGE\"/><category android:name=\"android.intent.category.HEALTH_PERMISSIONS\"/></intent-filter>\n </activity-alias>\n </application>\n</manifest>\n",
 "app/src/main/res/values/styles.xml": "<resources><style name=\"AppTheme\" parent=\"android:style/Theme.Material.Light.NoActionBar\">\n <item name=\"android:fontFamily\">sans</item><item name=\"android:colorAccent\">#087F78</item>\n <item name=\"android:windowLightStatusBar\">true</item><item name=\"android:statusBarColor\">#EFF5F7</item>\n <item name=\"android:navigationBarColor\">#FFFFFF</item><item name=\"android:windowActionModeOverlay\">true</item>\n <item name=\"android:windowBackground\">#EFF5F7</item>\n</style></resources>\n",
 "app/src/main/res/drawable/ic_launcher.xml": "<vector xmlns:android=\"http://schemas.android.com/apk/res/android\" android:width=\"108dp\" android:height=\"108dp\" android:viewportWidth=\"108\" android:viewportHeight=\"108\">\n <path android:fillColor=\"#087F78\" android:pathData=\"M0,0h108v108h-108z\"/>\n <path android:strokeColor=\"#FFFFFF\" android:strokeWidth=\"8\" android:strokeLineCap=\"round\" android:pathData=\"M36,77L72,31\"/>\n <path android:fillColor=\"#FFFFFF\" android:pathData=\"M36,25a12,12 0,1 0,0 24a12,12 0,1 0,0 -24M72,59a12,12 0,1 0,0 24a12,12 0,1 0,0 -24\"/>\n <path android:fillColor=\"#087F78\" android:pathData=\"M36,32a5,5 0,1 0,0 10a5,5 0,1 0,0 -10M72,66a5,5 0,1 0,0 10a5,5 0,1 0,0 -10\"/>\n</vector>\n",
 "app/src/main/java/com/jeevesh/progress/MainActivity.java": "package com.jeevesh.progress;\n\nimport android.app.*;\nimport android.content.*;\nimport android.graphics.Color;\nimport android.net.Uri;\nimport android.os.*;\nimport android.print.*;\nimport android.util.AtomicFile;\nimport android.view.*;\nimport android.webkit.*;\nimport android.widget.*;\nimport androidx.webkit.WebViewAssetLoader;\nimport java.io.*;\nimport java.nio.charset.StandardCharsets;\nimport java.util.concurrent.Executors;\nimport org.json.*;\n\npublic class MainActivity extends androidx.activity.ComponentActivity {\n    private FitImport health;\n    private static final String APP = \"https://appassets.androidplatform.net/assets/index.html\";\n    private static final int EXPORT = 10, IMPORT = 11, MAX = 15000000;\n    private WebView web;\n    private AtomicFile data;\n    private String pendingExport;\n    private boolean pickerOpen;\n    private final java.util.concurrent.ExecutorService io = Executors.newSingleThreadExecutor();\n\n    public WebView getWebView() { return web; }\n\n    @Override public void onCreate(Bundle state) {\n        super.onCreate(state);\n        health = new FitImport(this);\n        data = new AtomicFile(new File(getFilesDir(), \"progress-v2.json\"));\n        FrameLayout root = new FrameLayout(this);\n        root.setBackgroundColor(Color.rgb(243,245,250));\n        web = new WebView(this);\n        root.addView(web, new FrameLayout.LayoutParams(-1,-1));\n        setContentView(root);\n        root.setOnApplyWindowInsetsListener((v,insets) -> {\n            if (Build.VERSION.SDK_INT >= 30) {\n                android.graphics.Insets safe = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.ime() | WindowInsets.Type.displayCutout());\n                v.setPadding(safe.left,safe.top,safe.right,safe.bottom);\n                return WindowInsets.CONSUMED;\n            }\n            v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());\n            return insets.consumeSystemWindowInsets();\n        });\n        root.requestApplyInsets();\n        WebSettings settings = web.getSettings();\n        settings.setJavaScriptEnabled(true);\n        settings.setDomStorageEnabled(true);\n        settings.setAllowFileAccess(false);\n        settings.setAllowContentAccess(false);\n        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);\n        settings.setSupportMultipleWindows(false);\n        settings.setJavaScriptCanOpenWindowsAutomatically(false);\n        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG);\n        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()\n            .addPathHandler(\"/assets/\", new WebViewAssetLoader.AssetsPathHandler(this)).build();\n        web.setWebViewClient(new WebViewClient() {\n            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {\n                Uri url = request.getUrl();\n                if (APP.equals(url.toString())) {\n                    WebResourceResponse response = loader.shouldInterceptRequest(url);\n                    if (response != null) return response;\n                }\n                return new WebResourceResponse(\"text/plain\",\"UTF-8\",403,\"Blocked\",null,new ByteArrayInputStream(new byte[0]));\n            }\n            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {\n                return !APP.equals(request.getUrl().toString());\n            }\n            @Override public void onReceivedError(WebView view,WebResourceRequest request,WebResourceError error) {\n                if(request.isForMainFrame()) message(\"Could not open the app. Please restart it or update Android System WebView.\");\n            }\n        });\n        web.setWebChromeClient(new WebChromeClient() {\n            @Override public boolean onJsAlert(WebView view,String url,String text,JsResult result) {\n                new AlertDialog.Builder(MainActivity.this).setTitle(\"Progress %\").setMessage(text)\n                    .setPositiveButton(\"OK\",(d,w)->result.confirm()).setOnCancelListener(d->result.cancel()).show();\n                return true;\n            }\n            @Override public boolean onJsConfirm(WebView view,String url,String text,JsResult result) {\n                new AlertDialog.Builder(MainActivity.this).setTitle(\"Progress %\").setMessage(text)\n                    .setPositiveButton(\"Continue\",(d,w)->result.confirm())\n                    .setNegativeButton(\"Cancel\",(d,w)->result.cancel()).setOnCancelListener(d->result.cancel()).show();\n                return true;\n            }\n        });\n        web.addJavascriptInterface(new NativeStore(),\"ProgressAndroid\");\n        web.loadUrl(APP);\n        if (Build.VERSION.SDK_INT >= 33) {\n            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,this::goBack);\n        }\n    }\n\n    private void goBack() {\n        web.evaluateJavascript(\"(function(){if(typeof view!=='undefined'&&view!=='dashboard'){show('dashboard');return true;}return false;})()\",\n            result -> { if(!\"true\".equals(result)) finish(); });\n    }\n    @Override public void onBackPressed() { goBack(); }\n\n    private void message(String text) {\n        runOnUiThread(() -> Toast.makeText(this,text,Toast.LENGTH_LONG).show());\n    }\n    private static String readLimited(InputStream input) throws IOException {\n        if(input==null) throw new IOException(\"No input\");\n        ByteArrayOutputStream out=new ByteArrayOutputStream();\n        byte[] buffer=new byte[8192];\n        int n;\n        while((n=input.read(buffer))!=-1) {\n            if(out.size()+n>MAX) throw new IOException(\"Backup exceeds 15 MB\");\n            out.write(buffer,0,n);\n        }\n        return out.toString(StandardCharsets.UTF_8.name());\n    }\n    public class NativeStore {\n        @JavascriptInterface public void importFit(String date) { runOnUiThread(()->health.read(date)); }\n        @JavascriptInterface public void connectFit() { runOnUiThread(()->health.connect()); }\n        @JavascriptInterface public void healthSettings() { runOnUiThread(()->health.settings()); }\n        @JavascriptInterface public synchronized String readState() {\n            try(FileInputStream input=data.openRead()) { return readLimited(input); }\n            catch(FileNotFoundException e) { return null; }\n            catch(Exception e) { return \"{unreadable\"; } // Let the UI preserve rather than overwrite damaged data.\n        }\n        @JavascriptInterface public synchronized boolean writeState(String json) {\n            if(json==null||json.getBytes(StandardCharsets.UTF_8).length>MAX) return false;\n            FileOutputStream output=null;\n            try {\n                JSONObject parsed=new JSONObject(json);\n                if(parsed.getInt(\"version\")!=2) return false;\n                output=data.startWrite();\n                output.write(json.getBytes(StandardCharsets.UTF_8));\n                data.finishWrite(output);\n                return true;\n            } catch(Exception e) { if(output!=null)data.failWrite(output); return false; }\n        }\n        @JavascriptInterface public void exportBackup(String json,String filename) {\n            if(json==null||json.getBytes(StandardCharsets.UTF_8).length>MAX) {message(\"Backup is too large.\");return;}\n            runOnUiThread(()->{\n                if(pickerOpen) { message(\"Finish the current file selection first.\"); return; }\n                pendingExport=json; pickerOpen=true;\n                Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE)\n                    .setType(\"application/json\").putExtra(Intent.EXTRA_TITLE,\"progress-percent-backup.json\");\n                try { startActivityForResult(intent,EXPORT); }\n                catch(ActivityNotFoundException e) { pendingExport=null;pickerOpen=false;message(\"No file picker is available.\"); }\n            });\n        }\n        @JavascriptInterface public void restoreBackup() {\n            runOnUiThread(()->{\n                if(pickerOpen) {message(\"Finish the current file selection first.\");return;}\n                pickerOpen=true;\n                Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType(\"*/*\");\n                try {startActivityForResult(intent,IMPORT);}\n                catch(ActivityNotFoundException e) {pickerOpen=false;message(\"No file picker is available.\");}\n            });\n        }\n        @JavascriptInterface public void printReport() {\n            runOnUiThread(()->{\n                PrintManager manager=(PrintManager)getSystemService(PRINT_SERVICE);\n                if(manager!=null) manager.print(\"Progress report\",web.createPrintDocumentAdapter(\"Progress report\"),new PrintAttributes.Builder().build());\n            });\n        }\n    }\n    @Override protected void onActivityResult(int request,int result,Intent intent) {\n        super.onActivityResult(request,result,intent);\n        if(request!=EXPORT&&request!=IMPORT)return;\n        pickerOpen=false;\n        if(result!=RESULT_OK||intent==null||intent.getData()==null) {\n            pendingExport=null; message(\"File selection cancelled.\"); return;\n        }\n        Uri uri=intent.getData();\n        if(request==EXPORT) {\n            String payload=pendingExport;pendingExport=null;\n            if(payload==null) {message(\"Please export your backup again.\");return;}\n            io.execute(()->{\n                try(OutputStream output=getContentResolver().openOutputStream(uri,\"wt\")) {\n                    if(output==null)throw new IOException(\"No output\");\n                    output.write(payload.getBytes(StandardCharsets.UTF_8));\n                    message(\"Backup saved.\");\n                } catch(Exception e) {message(\"Backup could not be saved. Please try another location.\");}\n            });\n        } else {\n            io.execute(()->{\n                try(InputStream input=getContentResolver().openInputStream(uri)) {\n                    String json=readLimited(input);\n                    runOnUiThread(()->web.evaluateJavascript(\"window.restoreAndroidBackup(\"+JSONObject.quote(json)+\")\",null));\n                } catch(Exception e) {message(\"Could not read this backup. Choose a JSON backup under 15 MB.\");}\n            });\n        }\n    }\n    @Override protected void onPause() {super.onPause();web.onPause();}\n    @Override protected void onResume() {super.onResume();if(web!=null)web.onResume();}\n    @Override protected void onDestroy() {\n        if(web!=null){web.removeJavascriptInterface(\"ProgressAndroid\");web.destroy();}\n        io.shutdown();super.onDestroy();\n    }\n}\n",
 "app/src/androidTest/java/com/jeevesh/progress/ProgressTest.java": "package com.jeevesh.progress;\n\nimport androidx.test.core.app.ActivityScenario;\nimport androidx.test.ext.junit.runners.AndroidJUnit4;\nimport org.junit.Test;\nimport org.junit.runner.RunWith;\nimport static org.junit.Assert.*;\nimport java.util.concurrent.*;\nimport java.util.concurrent.atomic.AtomicReference;\n\n@RunWith(AndroidJUnit4.class)\npublic class ProgressTest {\n    private String js(ActivityScenario<MainActivity> activity,String code) throws Exception {\n        CountDownLatch latch=new CountDownLatch(1);\n        AtomicReference<String> answer=new AtomicReference<>();\n        activity.onActivity(a->a.getWebView().evaluateJavascript(code,result->{answer.set(result);latch.countDown();}));\n        assertTrue(\"JavaScript callback timeout\",latch.await(20,TimeUnit.SECONDS));\n        return answer.get();\n    }\n    private void ready(ActivityScenario<MainActivity> activity) throws Exception {\n        for(int i=0;i<100;i++){\n            if(\"true\".equals(js(activity,\"typeof state !== 'undefined' && !!document.querySelector('#prevWeek')\")))return;\n            Thread.sleep(100);\n        }\n        fail(\"Offline dashboard did not load\");\n    }\n    @Test public void offlineJournalPersistsAndReportsWork() throws Exception {\n        try(ActivityScenario<MainActivity> activity=ActivityScenario.launch(MainActivity.class)){\n            ready(activity);\n            assertEquals(\"true\",js(activity,\"document.querySelector('#pageTitle').textContent === 'Weekly overview'\"));\n            assertEquals(\"true\",js(activity,\"normal(7.2,10) === 72 && difference(72,70) === 2 && normal(null,10) === null\"));\n            assertEquals(\"true\",js(activity,\"monday('2026-01-01') === '2025-12-29'\"));\n            assertEquals(\"true\",js(activity,\"$('#time_family').parentElement.hidden && $('#targetFamily').parentElement.hidden && !$('#dashboard').textContent.includes('Family target')\"));\n            js(activity,\"show('journal'); loadDay(); document.querySelector('#time_sleep_hours').value='8'; document.querySelector('#time_sleep_hours').dispatchEvent(new Event('input')); $('#time_sleep_seconds').value='1'; $('#time_sleep_seconds').dispatchEvent(new Event('input'));\");\n            js(activity,\"$('#tab-body').click(); $('#steps').value='6000'; $('#tab-sleep').click();\");\n            assertEquals(\"true\",js(activity,\"$('#time_sleep').value==='08:00:01' && $('#steps').value==='6000' && !$('#panel-sleep').hidden && $('#panel-body').hidden\"));\n            js(activity,\"$('#clearDraft').click();\");\n            assertEquals(\"true\",js(activity,\"$('#time_sleep').value==='' && $('#time_sleep_hours').value===''\"));\n            js(activity,\"$('#tab-time').click(); $('#time_work_minutes').value='60'; $('#time_work_minutes').dispatchEvent(new Event('input')); $('#tab-sleep').click(); $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"!$('#panel-time').hidden && state.records.length===0\"));\n            js(activity,\"loadDay(); $('#tab-sleep').click();\");\n            js(activity,\"$('#stage_deep_hours').value='1'; $('#stage_deep_hours').dispatchEvent(new Event('input'));\");\n            assertEquals(\"true\",js(activity,\"$('#stage_deep').parentElement.querySelector('.tag').textContent==='Add total sleep'\"));\n            js(activity,\"$('#time_sleep_hours').value='8'; $('#time_sleep_hours').dispatchEvent(new Event('input'));\");\n            assertEquals(\"true\",js(activity,\"$('#stage_deep').parentElement.querySelector('.tag').textContent==='12.5% of sleep'\"));\n\n            js(activity,\"show('journal'); loadDay(); $('#time_sleep').value='08:00:01'; $('#time_work').value='08:00:00'; $('#steps').value='6000'; $('#distance').value='4000'; $('#weight').value='72.125'; $('#height').value='175.1'; $('#complete').checked=true; $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"state.records.length === 1 && state.records[0].time.sleep === 28801 && state.records[0].weight === 72125 && state.records[0].height === 1751\"));\n            js(activity,\"$('#time_work').value='24:00:00'; $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"$('#formError').textContent.includes('exceed 24 hours') && state.records[0].time.work === 28800\"));\n            js(activity,\"$('#time_work').value='08:00:00'; $('#stage_deep').value='09:00:00'; $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"$('#formError').textContent.includes('cannot exceed')\"));\n            activity.recreate(); ready(activity);\n            assertEquals(\"true\",js(activity,\"state.records.length===1 && state.records[0].time.sleep===28801\"));\n            js(activity,\"show('lifetime')\");\n            assertEquals(\"true\",js(activity,\"$('#lifetime').textContent.includes('33.3%') && $('#lifetime').textContent.includes('23.33 years')\"));\n            js(activity,\"show('health')\");\n            assertEquals(\"true\",js(activity,\"$('#health').textContent.includes('72.125') && $('#health').textContent.includes('175.1')\"));\n            js(activity,\"$('#demoBtn').click(); show('dashboard')\");\n            assertEquals(\"true\",js(activity,\"demo && state.records.length === 28 && state.records.every(r=>r.time.family===null && r.archivedFamilySeconds===3600 && r.time.other===5400) && !scores(state.records[0]).some(s=>s.id==='family') && !projection(state.records,70).some(s=>s.key==='family')\"));\n            js(activity,\"$('#demoBtn').click()\");\n            assertEquals(\"true\",js(activity,\"!demo && state.records.length===1\"));\n            js(activity,\"show('settings'); $('#age').value='28'; $('#profileForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"state.profile.age===28\"));\n            activity.recreate(); ready(activity);\n            assertEquals(\"true\",js(activity,\"state.profile.age===28 && state.records.length===1\"));\n            js(activity,\"show('settings'); $('#age').value='30'; $('#lifespan').value='90'; $('#profileForm').requestSubmit(); show('lifetime');\");\n            assertEquals(\"true\",js(activity,\"$('#lifetime').textContent.includes('90 years, one day at a time') && $('#lifetime').textContent.includes('30 years sleeping') && !$('#lifetime').textContent.includes('23.33 years') && $('#lifetime').textContent.includes('Remaining 60 years')\"));\n            js(activity,\"show('journal');loadDay(); window.receiveFitData({date:localDate(),source:'Google Fit via Health Connect',zone:'Asia/Kolkata',data:{steps:9999,sleep:18000,heartRate:70,activeCalories:400,totalCalories:2100},notices:[]}); $('#fitApply').click(); $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"state.records[0].steps===6000 && state.records[0].time.sleep===28801 && state.records[0].health.data.heartRate===70 && state.records[0].health.data.totalCalories===2100\"));\n            activity.recreate(); ready(activity);\n            assertEquals(\"true\",js(activity,\"state.profile.lifespan===90 && state.records[0].health.data.activeCalories===400\"));\n            js(activity,\"show('journal'); loadDay(); window.receiveFitData({date:localDate(),data:{steps:12345}}); document.querySelector('[data-fit-key=\\\"steps\\\"]').checked=true; $('#fitApply').click(); $('#dayForm').requestSubmit();\");\n            assertEquals(\"true\",js(activity,\"state.records[0].steps===12345 && state.records[0].time.sleep===28801\"));\n            assertEquals(\"true\",js(activity,\"(()=>{const old=shift(localDate(),-90),empty=shift(localDate(),-91),imports=[{date:old,data:{steps:4000,sleep:25200,heartRate:65}},{date:empty,data:{}},{date:localDate(),data:{steps:5,heartRate:75}}];const once=mergeFitHistory(state,imports),twice=mergeFitHistory(once,imports);return state.records.length===1&&twice.records.length===2&&twice.records.find(r=>r.date===localDate()).steps===12345&&twice.records.find(r=>r.date===old).steps===4000&&!twice.records.find(r=>r.date===old).complete&&twice.records.find(r=>r.date===old).health.data.heartRate===65})()\"));\n        }\n    }\n}\n",
 "app/src/main/java/com/jeevesh/progress/HealthPrivacyActivity.java": "package com.jeevesh.progress;\nimport android.app.Activity;\nimport android.os.Bundle;\nimport android.widget.*;\npublic class HealthPrivacyActivity extends Activity {\n @Override public void onCreate(Bundle state){super.onCreate(state);TextView text=new TextView(this);text.setPadding(32,40,32,40);text.setTextSize(18);text.setText(\"Health data in Progress %\\n\\nWith your permission, Progress % reads Google Fit records shared through Health Connect: sleep, steps, distance, calories, heart rate, workouts, body measurements and oxygen saturation.\\n\\nYou choose a day and review the import before saving. Missing data stays missing. Manual fields are never replaced without selecting them. Data is stored privately on this phone and can be included in a backup you export. The app does not send health data to GitHub or a server and does not write to Google Fit or Health Connect.\\n\\nRevoke access in Health Connect at any time. Previously saved entries remain until you delete app data or uninstall. Exported backups remain in your chosen location. These are tracking measurements, not a medical diagnosis.\");ScrollView scroll=new ScrollView(this);scroll.addView(text);setContentView(scroll);}\n}",
 "app/src/main/java/com/jeevesh/progress/FitImport.kt": "package com.jeevesh.progress\n\nimport android.content.Intent\nimport android.net.Uri\nimport androidx.health.connect.client.HealthConnectFeatures\nimport androidx.health.connect.client.HealthConnectClient\nimport androidx.health.connect.client.PermissionController\nimport androidx.health.connect.client.permission.HealthPermission\nimport androidx.health.connect.client.records.*\nimport androidx.health.connect.client.records.metadata.DataOrigin\nimport androidx.health.connect.client.request.*\nimport androidx.health.connect.client.time.TimeRangeFilter\nimport androidx.lifecycle.lifecycleScope\nimport kotlinx.coroutines.launch\nimport kotlinx.coroutines.CancellationException\nimport org.json.JSONObject\nimport org.json.JSONArray\nimport java.time.*\nimport kotlin.reflect.KClass\n\n/** Read-only Google Fit import. No credentials, network calls or health writes. */\nclass FitImport(private val activity: MainActivity) {\n private val types = listOf(StepsRecord::class, DistanceRecord::class, SleepSessionRecord::class,\n  HeartRateRecord::class, RestingHeartRateRecord::class, ActiveCaloriesBurnedRecord::class,\n  TotalCaloriesBurnedRecord::class, ExerciseSessionRecord::class, WeightRecord::class,\n  HeightRecord::class, OxygenSaturationRecord::class)\n private val permissions = types.map { HealthPermission.getReadPermission(it) }.toSet()\n private val origins = setOf(DataOrigin(\"com.google.android.apps.fitness\"))\n private var busy = false\n private val launcher = activity.registerForActivityResult(PermissionController.createRequestPermissionResultContract()) { granted ->\n  message(if (granted.isEmpty()) \"No health permissions granted. Manual entry is still available.\"\n   else \"Connected. Choose a date and tap Import from Google Fit. Only granted data types will be read.\")\n }\n private fun message(text: String) = send(JSONObject().put(\"message\",text))\n private fun send(value: JSONObject) {\n  if (!activity.isFinishing && !activity.isDestroyed)\n   activity.webView.evaluateJavascript(\"window.receiveFitData(\"+value.toString()+\")\",null)\n }\n private fun available(): Boolean {\n  return when(HealthConnectClient.getSdkStatus(activity)) {\n   HealthConnectClient.SDK_AVAILABLE -> true\n   HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> { message(\"Install or update Health Connect, then turn on Sync Fit with Health Connect in Google Fit settings.\");false }\n   else -> {message(\"Health Connect is unavailable on this device. Android 9 or newer is required; manual entry still works.\");false}\n  }\n }\n fun connect() {\n  if (!available()) return\n  try {\n   val client=HealthConnectClient.getOrCreate(activity)\n   val history=client.features.getFeatureStatus(HealthConnectFeatures.FEATURE_READ_HEALTH_DATA_HISTORY)==HealthConnectFeatures.FEATURE_STATUS_AVAILABLE\n   launcher.launch(if(history)permissions+HealthPermission.PERMISSION_READ_HEALTH_DATA_HISTORY else permissions)\n  } catch(e: Exception) {message(\"Could not open health permissions. Open Health Connect settings and allow Progress % to read your data.\")}\n }\n fun settings() {\n  try {\n   val intent=if(HealthConnectClient.getSdkStatus(activity)==HealthConnectClient.SDK_AVAILABLE)\n    Intent(HealthConnectClient.ACTION_HEALTH_CONNECT_SETTINGS)\n   else Intent(Intent.ACTION_VIEW,Uri.parse(\"https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata\"))\n   activity.startActivity(intent)\n  }catch(e:Exception){message(\"Open Health Connect from your phone Settings. In Google Fit, enable Sync Fit with Health Connect.\")}\n }\n private suspend fun <T:Record> all(client:HealthConnectClient, type:KClass<T>, range:TimeRangeFilter):List<T> {\n  val result=mutableListOf<T>();var token:String?=null\n  do {\n   val page=client.readRecords(ReadRecordsRequest(type,range,dataOriginFilter=origins,pageSize=1000,pageToken=token))\n   result.addAll(page.records);token=page.pageToken\n   check(result.size<=20000){\"Too many records for one day\"}\n  }while(token!=null)\n  return result\n }\n fun read(dateText:String) {\n  if(busy){message(\"An import is already running.\");return}\n  if(!available())return\n  val date=try{LocalDate.parse(dateText)}catch(e:Exception){message(\"Choose a valid date.\");return}\n  if(date>LocalDate.now()){message(\"Choose a date no later than today.\");return}\n  busy=true\n  activity.lifecycleScope.launch {\n   try {\n    val client=HealthConnectClient.getOrCreate(activity)\n    val granted=client.permissionController.getGrantedPermissions()\n    if(granted.intersect(permissions).isEmpty()){message(\"Connect Google Fit first and grant read permissions.\");return@launch}\n    val zone=ZoneId.systemDefault()\n    val start=date.atStartOfDay(zone).toInstant();val end=date.plusDays(1).atStartOfDay(zone).toInstant()\n    val range=TimeRangeFilter.between(start,end)\n    val out=JSONObject().put(\"date\",dateText).put(\"source\",\"Google Fit via Health Connect\")\n      .put(\"zone\",zone.id).put(\"syncedAt\",Instant.now().toString())\n    val data=JSONObject();val notices=JSONArray()\n    if(date<LocalDate.now().minusDays(29)&&HealthPermission.PERMISSION_READ_HEALTH_DATA_HISTORY !in granted)\n     notices.put(\"Older history may be restricted. Tap Connect and allow Access past data in Health Connect if your device supports it.\")\n    suspend fun readType(type:KClass<out Record>, label:String, block:suspend ()->Unit) {\n     if(HealthPermission.getReadPermission(type) !in granted){notices.put(\"$label: permission not granted\");return}\n     try{block()}catch(e:CancellationException){throw e}catch(e:Exception){notices.put(\"$label: could not read. Check permissions and try again.\")}\n    }\n    readType(StepsRecord::class,\"Steps\") {\n     val a=client.aggregate(AggregateRequest(setOf(StepsRecord.COUNT_TOTAL),range,origins))\n     a[StepsRecord.COUNT_TOTAL]?.let{data.put(\"steps\",it)}\n    }\n    readType(DistanceRecord::class,\"Distance\") {\n     val a=client.aggregate(AggregateRequest(setOf(DistanceRecord.DISTANCE_TOTAL),range,origins))\n     a[DistanceRecord.DISTANCE_TOTAL]?.let{data.put(\"distance\",it.inMeters)}\n    }\n    readType(ActiveCaloriesBurnedRecord::class,\"Active calories\"){\n     val a=client.aggregate(AggregateRequest(setOf(ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL),range,origins))\n     a[ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL]?.let{data.put(\"activeCalories\",it.inKilocalories)}\n    }\n    readType(TotalCaloriesBurnedRecord::class,\"Total calories\"){\n     val a=client.aggregate(AggregateRequest(setOf(TotalCaloriesBurnedRecord.ENERGY_TOTAL),range,origins))\n     a[TotalCaloriesBurnedRecord.ENERGY_TOTAL]?.let{data.put(\"totalCalories\",it.inKilocalories)}\n    }\n    readType(HeartRateRecord::class,\"Heart rate\"){\n     val a=client.aggregate(AggregateRequest(setOf(HeartRateRecord.BPM_AVG,HeartRateRecord.BPM_MIN,HeartRateRecord.BPM_MAX),range,origins))\n     a[HeartRateRecord.BPM_AVG]?.let{data.put(\"heartRate\",it)}\n     a[HeartRateRecord.BPM_MIN]?.let{data.put(\"heartRateMin\",it)}\n     a[HeartRateRecord.BPM_MAX]?.let{data.put(\"heartRateMax\",it)}\n    }\n    readType(RestingHeartRateRecord::class,\"Resting heart rate\"){\n     all(client,RestingHeartRateRecord::class,range).maxByOrNull{it.time}?.let{data.put(\"restingHeartRate\",it.beatsPerMinute)}\n    }\n    readType(WeightRecord::class,\"Weight\"){\n     all(client,WeightRecord::class,range).maxByOrNull{it.time}?.let{data.put(\"weight\",it.weight.inGrams)}\n    }\n    readType(HeightRecord::class,\"Height\"){\n     all(client,HeightRecord::class,range).maxByOrNull{it.time}?.let{data.put(\"height\",it.height.inMeters*1000)}\n    }\n    readType(OxygenSaturationRecord::class,\"Oxygen saturation\"){\n     all(client,OxygenSaturationRecord::class,range).maxByOrNull{it.time}?.let{data.put(\"oxygen\",it.percentage.value)}\n    }\n    // Union clipped intervals prevents duplicate sessions adding the same seconds twice.\n    fun seconds(intervals:List<Pair<Instant,Instant>>):Long {\n     val clipped=intervals.map{maxOf(start,it.first) to minOf(end,it.second)}.filter{it.second>it.first}.sortedBy{it.first}\n     var total=0L;var left:Instant?=null;var right:Instant?=null\n     for((s,e) in clipped){if(right==null){left=s;right=e}else if(s<=right){right=maxOf(right,e)}else{total+=Duration.between(left,right).seconds;left=s;right=e}}\n     if(right!=null)total+=Duration.between(left,right).seconds\n     return total\n    }\n    readType(SleepSessionRecord::class,\"Sleep\"){\n     val records=all(client,SleepSessionRecord::class,range)\n     if(records.isNotEmpty()){\n      val stages=records.flatMap{it.stages}\n      val asleep=stages.filter{it.stage in setOf(2,4,5,6)}\n      val total=if(asleep.isNotEmpty())seconds(asleep.map{it.startTime to it.endTime})\n        else seconds(records.map{it.startTime to it.endTime})-seconds(stages.filter{it.stage in setOf(1,3,7)}.map{it.startTime to it.endTime})\n      data.put(\"sleep\",total.coerceAtLeast(0))\n      for((name,type) in listOf(\"deep\" to 5,\"light\" to 4,\"rem\" to 6)){\n       val matching=stages.filter{it.stage==type};if(matching.isNotEmpty())data.put(name,seconds(matching.map{it.startTime to it.endTime}))\n      }\n      if(asleep.isEmpty())notices.put(\"Sleep uses session duration minus reported awake time; sleep stages were not shared.\")\n     }\n    }\n    readType(ExerciseSessionRecord::class,\"Workouts\"){\n     val records=all(client,ExerciseSessionRecord::class,range)\n     if(records.isNotEmpty()){\n      val list=JSONArray()\n      records.distinctBy{it.startTime.toString()+it.endTime.toString()+it.exerciseType}.forEach{\n       list.put(JSONObject().put(\"name\",it.title?:\"Workout\").put(\"type\",it.exerciseType)\n        .put(\"start\",it.startTime.toString()).put(\"end\",it.endTime.toString())\n        .put(\"seconds\",Duration.between(maxOf(start,it.startTime),minOf(end,it.endTime)).seconds.coerceAtLeast(0)))\n      }\n      data.put(\"workouts\",list)\n     }\n    }\n    out.put(\"data\",data).put(\"notices\",notices)\n    send(out)\n   }catch(e:CancellationException){throw e}catch(e:Exception){message(\"Import failed. Your saved entries were not changed. Check Health Connect permissions and try again.\")}\n   finally{busy=false}\n  }\n }\n}\n"
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

FIT_JS = r'''

(() => {
 const form=$('#dayForm'),box=document.createElement('article');box.className='note';box.style.marginBottom='18px';
 box.innerHTML='<h3>Google Fit</h3><p class="small">In Google Fit: Profile → Settings → turn on Sync Fit with Health Connect. Allow Fit to write data, then allow Progress % to read it. This app reads Google Fit only.</p><div class="actions" style="margin-top:12px"><button type="button" id="fitConnect">Connect</button><button type="button" id="fitRead">Import selected day</button><button type="button" id="fitSettings">Health Connect settings</button></div><p id="fitStatus" role="status" class="small" style="margin-top:10px">On-demand import. Use Connect to allow past-data access where supported. Other fields stay manual.</p><div id="fitPreview"></div><div id="fitSaved"></div>';
 form.before(box);
 const history=document.createElement('details');history.style.marginTop='12px';
 history.innerHTML='<summary>Import previous data</summary><p class="small">Choose up to 31 days at a time, including older months. Only data shared by Google Fit is available. Existing manual values are kept. Missing days stay empty. New historical entries use your current targets and remain unfinished.</p><div class="formgrid"><label>From<input type="date" id="fitFrom"></label><label>Through<input type="date" id="fitTo"></label></div><div class="actions" style="margin-top:12px"><button type="button" id="fitHistory">Read date range</button><button type="button" id="fitCancel" hidden>Cancel</button></div><div id="fitHistoryPreview"></div>';
 box.append(history);$('#fitFrom').value=shift(localDate(),-6);$('#fitTo').value=localDate();$('#fitFrom').max=$('#fitTo').max=localDate();

 const mapping={steps:['Steps','#steps',1],distance:['Distance (all activities)','#distance',1],weight:['Weight','#weight',1000],height:['Height','#height',10],sleep:['Sleep','#time_sleep',0],deep:['Deep sleep','#stage_deep',0],light:['Light sleep','#stage_light',0],rem:['REM sleep','#stage_rem',0]};
 let candidate=null;
 let batch=null;
 const fingerprint=()=>JSON.stringify([...form.querySelectorAll('input,textarea')].map(n=>[n.id,n.value,n.checked]));let baseline=fingerprint();
 const units={steps:'steps',distance:'m',weight:'g',height:'mm',sleep:'seconds',deep:'seconds',light:'seconds',rem:'seconds',activeCalories:'kcal active',totalCalories:'kcal total',heartRate:'bpm average',heartRateMin:'bpm minimum',heartRateMax:'bpm maximum',restingHeartRate:'bpm resting',oxygen:'% SpO₂'};
 const labels={activeCalories:'Active calories',totalCalories:'Total calories',heartRate:'Heart rate',heartRateMin:'Minimum heart rate',heartRateMax:'Maximum heart rate',restingHeartRate:'Resting heart rate',oxygen:'Oxygen saturation'};
 function safeHealth(h){
  if(!h||typeof h!=='object'||!h.data||typeof h.date!=='string')throw Error('Invalid health import.');
  const max={steps:200000,distance:1000000,weight:1000000,height:3000,sleep:86400,deep:86400,light:86400,rem:86400,activeCalories:100000,totalCalories:100000,heartRate:300,heartRateMin:300,heartRateMax:300,restingHeartRate:300,oxygen:100};
  for(const [k,v] of Object.entries(h.data)){if(k==='workouts'){if(!Array.isArray(v)||v.length>1000||v.some(x=>!Number.isFinite(x.seconds)||x.seconds<0||x.seconds>90000||typeof x.name!=='string'))throw Error('Invalid workout data.');continue}
   if(!(k in max)||!Number.isFinite(v)||v<0||v>max[k])throw Error('Invalid '+k+' measurement.');
  }
  return structuredClone(h);
 }
 function details(h){if(!h)return '';return '<p class="small muted">Google Fit · '+esc(h.date)+' · '+esc(h.zone||'')+'</p>'+Object.entries(h.data).map(([k,v])=>k==='workouts'?'<p>'+v.length+' workouts: '+v.map(w=>esc(w.name)+' ('+num(w.seconds/60,1)+' min)').join(', ')+'</p>':'<p><strong>'+esc(mapping[k]?.[0]||labels[k]||k)+':</strong> '+num(v,3)+' '+esc(units[k]||'')+'</p>').join('')+'<p class="small muted">Active and total calories are separate and must not be added together. Workouts are not added to your time budget automatically.</p>'}
 function saved(){ $('#fitSaved').innerHTML=window.pendingHealthDraft?'<details><summary>Imported health details</summary>'+details(window.pendingHealthDraft)+'</details>':''; }
 $('#fitConnect').onclick=()=>{if(demo){toast('Exit demo to connect.');return}ProgressAndroid.connectFit()};
 $('#fitSettings').onclick=()=>ProgressAndroid.healthSettings();
 $('#fitRead').onclick=()=>{if(batch){toast('Wait for the history import to finish.');return}if(demo){toast('Exit demo to import your data.');return}if(!$('#entryDate').value){toast('Choose a date first.');return}$('#fitStatus').textContent='Reading Google Fit data for '+$('#entryDate').value+'…';ProgressAndroid.importFit($('#entryDate').value)};
 window.receiveFitData=result=>{
  if(batch){handleBatch(result);return}
  if(result.message){$('#fitStatus').textContent=result.message;return}
  try{
   candidate=safeHealth(result);
   if(demo||candidate.date!==$('#entryDate').value){candidate=null;$('#fitStatus').textContent='The selected day changed. Import again for the current day.';return}
   const keys=Object.keys(candidate.data);
   $('#fitStatus').textContent=keys.length?'Review this import. Select fields to fill, then apply and Save my day.':'No Google Fit data shared for this date. Check Fit’s Health Connect write permissions, sync Fit, then try again. Missing values are not zero.';
   $('#fitPreview').innerHTML=details(candidate)+(candidate.notices?.length?'<p class="small">'+candidate.notices.map(esc).join('<br>')+'</p>':'')+
     (keys.length?'<p class="small">Blank fields are selected by default. Select a filled field only if you want to replace it.</p>'+keys.filter(k=>mapping[k]).map(k=>'<label class="check"><input type="checkbox" data-fit-key="'+k+'" '+($(mapping[k][1]).value===''?'checked':'')+'>Apply '+esc(mapping[k][0])+'</label>').join('')+'<button type="button" id="fitApply" style="margin-top:12px">Apply to this day</button>':'');
   if($('#fitApply'))$('#fitApply').onclick=()=>{try{apply()}catch(e){$('#fitStatus').textContent='Check the entered durations before applying this import.'}};
  }catch(e){$('#fitStatus').textContent=e.message}
 };
 function apply(){
  if(!candidate||candidate.date!==$('#entryDate').value||demo)return;
  const chosen=[...box.querySelectorAll('[data-fit-key]:checked')].map(e=>e.dataset.fitKey);
  // Validate a prospective form before touching manual values.
  const values=Object.fromEntries(ACTIVITIES.map(k=>[k,parseDuration($('#time_'+k).value)]));
  const stages=Object.fromEntries(['deep','light','rem'].map(k=>[k,parseDuration($('#stage_'+k).value)]));
  if(chosen.includes('sleep'))values.sleep=Math.round(candidate.data.sleep);
  for(const k of ['deep','light','rem'])if(chosen.includes(k))stages[k]=Math.round(candidate.data[k]);
  if(Object.values(values).reduce((a,b)=>a+(b||0),0)>86400||Object.values(stages).reduce((a,b)=>a+(b||0),0)>(values.sleep||0)){ $('#fitStatus').textContent='These values conflict with your day total or sleep stages. Adjust your manual entry or selection first.';return}
  chosen.forEach(k=>{
   const [label,id,divisor]=mapping[k],raw=candidate.data[k],value=divisor?Math.round(raw)/divisor:duration(Math.round(raw));
   $(id).value=value;
   if(!divisor){const sec=Math.round(raw);for(const [suffix,v] of [['hours',Math.floor(sec/3600)],['minutes',Math.floor(sec%3600/60)],['seconds',sec%60]])$(id+'_'+suffix).value=v;$(id+'_hours').dispatchEvent(new Event('input'))}
  });
  window.pendingHealthDraft={...structuredClone(candidate),data:{...(window.pendingHealthDraft?.data||{}),...structuredClone(candidate.data)}};saved();updateBudget();$('#fitPreview').innerHTML='';$('#fitStatus').textContent='Applied to the form. Review your day and tap Save my day. Manual fields you did not select were kept.';
 }
 const previousLoad=loadDay;loadDay=function(date){previousLoad(date);candidate=null;window.pendingHealthDraft=structuredClone(state.records.find(r=>r.date===$('#entryDate').value)?.health||null);$('#fitPreview').innerHTML='';saved();baseline=fingerprint()};
 const clear=$('#clearDraft').onclick;$('#clearDraft').onclick=()=>{clear();window.pendingHealthDraft=null;candidate=null;$('#fitPreview').innerHTML='';saved()};

 // Pure merge: date-keyed records, fill missing daily fields, keep manual values, never double-add.
 window.mergeFitHistory=(current,imports)=>{
  const next=structuredClone(current),byDate=new Map(next.records.map(r=>[r.date,r]));
  for(const raw of imports){
   const h=safeHealth(raw);if(!Object.keys(h.data).length)continue;
   let r=byDate.get(h.date);
   if(!r)r={date:h.date,time:Object.fromEntries(ACTIVITIES.map(k=>[k,null])),stages:{deep:null,light:null,rem:null},steps:null,distance:null,weight:null,height:null,wellbeing:null,targets:structuredClone(next.profile.targets),custom:next.goals.map(g=>({...g,value:null})),note:'',complete:false};
   r.health={...h,data:{...(r.health?.data||{}),...h.data}};
   for(const k of ['steps','distance','weight','height'])if(r[k]==null&&h.data[k]!=null)r[k]=Math.round(h.data[k]);
   if(r.time.sleep==null&&h.data.sleep!=null){
    const total=Object.values(r.time).reduce((s,v)=>s+(v||0),0);
    if(total+Math.round(h.data.sleep)<=86400)r.time.sleep=Math.round(h.data.sleep);
   }
   for(const k of ['deep','light','rem'])if(r.stages[k]==null&&h.data[k]!=null){
    const total=Object.values(r.stages).reduce((s,v)=>s+(v||0),0);
    if(total+Math.round(h.data[k])<=(r.time.sleep||0))r.stages[k]=Math.round(h.data[k]);
   }
   validateRecord(r);byDate.set(r.date,r);
  }
  next.records=[...byDate.values()];validateState(next);return next;
 };
 function finishBatch(){
  const finished=batch;batch=null;$('#fitCancel').hidden=true;$('#fitHistory').disabled=false;
  const withData=finished.results.filter(h=>Object.keys(h.data).length);
  $('#fitStatus').textContent='Read '+finished.results.length+' days; '+withData.length+' have shared Google Fit data. No entries saved yet.';
  $('#fitHistoryPreview').innerHTML=finished.results.map(h=>'<p>'+esc(h.date)+' · '+Object.keys(h.data).length+' data fields'+(h.notices?.length?' · '+esc(h.notices.join(' / ')):'')+'</p>').join('')+(withData.length?'<button type="button" id="fitSaveHistory">Save imported history</button>':'');
  if($('#fitSaveHistory'))$('#fitSaveHistory').onclick=()=>{
   try{
    if(fingerprint()!==baseline)throw Error('Save your current journal draft before saving imported history.');
    persist(window.mergeFitHistory(state,withData));const date=$('#entryDate').value;loadDay(date);renderRecent();$('#fitHistoryPreview').innerHTML='';$('#fitStatus').textContent='History saved. Existing manual values were kept. Re-importing will not duplicate dates.';
   }catch(e){$('#fitStatus').textContent=e.message}
  };
 }
 function handleBatch(result){
  if(batch.cancelled){batch=null;$('#fitCancel').hidden=true;$('#fitHistory').disabled=false;$('#fitStatus').textContent='History import cancelled. No entries changed.';return}
  if(result.message){batch=null;$('#fitCancel').hidden=true;$('#fitHistory').disabled=false;$('#fitStatus').textContent=result.message+' No history entries saved.';return}
  try{
   const h=safeHealth(result);
   if(h.date!==batch.dates[batch.results.length])throw Error('Unexpected import date. Try the range again.');
   batch.results.push(h);
   if(batch.results.length===batch.dates.length){finishBatch();return}
   $('#fitStatus').textContent='Reading previous data: '+batch.results.length+' / '+batch.dates.length+' days. Keep the app open.';
   setTimeout(()=>{if(batch)ProgressAndroid.importFit(batch.dates[batch.results.length])},750);
  }catch(e){batch=null;$('#fitHistory').disabled=false;$('#fitCancel').hidden=true;$('#fitStatus').textContent=e.message}
 }
 $('#fitHistory').onclick=()=>{
  if(demo){toast('Exit demo to import history.');return}
  if(fingerprint()!==baseline){$('#fitStatus').textContent='Save your current journal draft before reading history.';return}
  const from=$('#fitFrom').value,to=$('#fitTo').value;
  if(!from||!to||from>to||to>localDate()){ $('#fitStatus').textContent='Choose a valid past date range.';return}
  const dates=[];for(let day=from;day<=to&&dates.length<32;day=shift(day,1))dates.push(day);
  if(dates.length>31){$('#fitStatus').textContent='Choose up to 31 days per batch. You can then import another month.';return}
  batch={dates,results:[],cancelled:false};$('#fitHistory').disabled=true;$('#fitCancel').hidden=false;$('#fitHistoryPreview').innerHTML='';$('#fitStatus').textContent='Reading previous data…';ProgressAndroid.importFit(dates[0]);
 };
 $('#fitCancel').onclick=()=>{if(batch)batch.cancelled=true;$('#fitStatus').textContent='Cancelling after the current read…'};
 const saveWithHealth=form.onsubmit;form.onsubmit=e=>{saveWithHealth(e);if(!$('#formError').textContent)baseline=fingerprint()};

 const originalRenderHealth=renderHealth;renderHealth=function(){originalRenderHealth();const latest=state.records.filter(r=>r.health).sort((a,b)=>b.date.localeCompare(a.date))[0];if(latest){const c=document.createElement('article');c.className='card';c.innerHTML='<h2>Latest imported health data</h2>'+details(latest.health);$('#health').append(c)}};
 const previousValidation=validateRecord;validateRecord=function(r){if(r.health)r.health=safeHealth(r.health);return previousValidation(r)};
 window.pendingHealthDraft=structuredClone(state.records.find(r=>r.date===$('#entryDate').value)?.health||null);saved();
})();

'''

def prepare(destination):
    root = Path(__file__).resolve().parent.parent
    out = Path(destination).resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Explicit path: AGP's default moved, so caching ~/.android alone was ineffective.
    signing_key = Path.home() / ".android" / "debug.keystore"
    signing_key.parent.mkdir(parents=True, exist_ok=True)
    if not signing_key.exists():
        subprocess.run(["keytool", "-genkeypair", "-keystore", str(signing_key),
                        "-storepass", "android", "-alias", "androiddebugkey",
                        "-keypass", "android", "-keyalg", "RSA", "-keysize", "2048",
                        "-validity", "10000", "-dname", "CN=Progress Percent Preview",
                        "-storetype", "JKS", "-noprompt"], check=True)
    print("Using persistent preview signing key at the GitHub Actions cache path")
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

    html = html.replace("validateRecord(r);const next=structuredClone(state);", "if(window.pendingHealthDraft)r.health=structuredClone(window.pendingHealthDraft);validateRecord(r);const next=structuredClone(state);")
    html = html.replace("Walking distance (metres)", "Distance (metres; all activities)")
    html = html.replace("70 years, one day at a time", "'+p.lifespan+' years, one day at a time")
    html = html.replace("23.33 years sleeping", "'+num(p.lifespan/3,2)+' years sleeping")
    html = html.replace("8 hours every day for 70 years.", "8 hours every day for '+p.lifespan+' years.")
    html = html.replace("About 8,522.33 days", "About '+num(p.lifespan/3*365.2425,2)+' days")
    html = html.replace("23.33 years of work", "'+num(p.lifespan/3,2)+' years of work")
    html = html.replace("<th>From now</th>", "<th>Remaining '+(remaining==null?'':num(remaining))+' years</th>")
    html = html.replace("Your editable assumption", "Uses your saved planning lifespan")

    html = html.replace("localStorage.", "appStorage.")
    html = html.replace('inputmode="numeric"', 'inputmode="text"')
    html = html.replace("<script>", "<script>\n" + BOOTSTRAP, 1)
    html = html.replace("</script>", ANDROID_JS + UX_JS + FIT_JS + "\n</script>", 1)
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
