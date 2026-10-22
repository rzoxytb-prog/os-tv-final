package com.rose.tvos;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

public class MainActivity extends Activity {

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        setContentView(web);
        hideSystemUi();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);

        web.setBackgroundColor(0xFFC23D86);
        web.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.addJavascriptInterface(new Bridge(), "Android");
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String u = request.getUrl().toString();
                if (u.startsWith("file:")) return false;
                openLink(u);
                return true;
            }
        });
        web.loadUrl("file:///android_asset/index.html");
        web.requestFocus();
    }

    private void hideSystemUi() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    @Override
    protected void onResume() {
        super.onResume();
        hideSystemUi();
    }

    // Touche Retour de la télécommande -> Échap dans la page
    @Override
    public boolean dispatchKeyEvent(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.KEYCODE_BACK) {
            if (e.getAction() == KeyEvent.ACTION_UP) {
                web.evaluateJavascript(
                        "window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))", null);
            }
            return true;
        }
        return super.dispatchKeyEvent(e);
    }

    @Override
    public void onBackPressed() { /* le launcher ne se ferme pas */ }

    /** Ouvre l'application officielle si elle est installée, sinon le site. */
    private void openLink(String url) {
        String host = Uri.parse(url).getHost();
        if (host == null) host = "";
        String[] pkgs = null;
        if (host.contains("netflix")) pkgs = new String[]{"com.netflix.ninja"};
        else if (host.contains("primevideo") || host.contains("amazon")) pkgs = new String[]{"com.amazon.amazonvideo.livingroom"};
        else if (host.contains("disneyplus")) pkgs = new String[]{"com.disney.disneyplus"};
        else if (host.contains("youtube")) pkgs = new String[]{"com.google.android.youtube.tv"};
        else if (host.contains("spotify")) pkgs = new String[]{"com.spotify.tv.android"};
        else if (host.contains("deezer")) pkgs = new String[]{"deezer.android.tv"};
        else if (host.contains("play.google")) pkgs = new String[]{"com.android.vending"};

        PackageManager pm = getPackageManager();
        if (pkgs != null) {
            for (String p : pkgs) {
                Intent i = pm.getLeanbackLaunchIntentForPackage(p);
                if (i == null) i = pm.getLaunchIntentForPackage(p);
                if (i != null) { startActivity(i); return; }
            }
        }
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
        } catch (Exception ex) {
            Toast.makeText(this, "Aucune application pour ouvrir " + host, Toast.LENGTH_LONG).show();
        }
    }

    /** Relance l'écran d'accueil d'origine de la TV. */
    private void openStockLauncher() {
        Intent home = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME);
        for (ResolveInfo ri : getPackageManager().queryIntentActivities(home, 0)) {
            if (!ri.activityInfo.packageName.equals(getPackageName())) {
                Intent i = new Intent(home)
                        .setClassName(ri.activityInfo.packageName, ri.activityInfo.name)
                        .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
                return;
            }
        }
        Toast.makeText(this, "Aucun autre écran d'accueil trouvé", Toast.LENGTH_LONG).show();
    }

    private class Bridge {
        @JavascriptInterface
        public void open(final String url) {
            runOnUiThread(new Runnable() { public void run() { openLink(url); } });
        }
        @JavascriptInterface
        public void stock() {
            runOnUiThread(new Runnable() { public void run() { openStockLauncher(); } });
        }
    }
}
