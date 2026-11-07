package com.agrovators.agrirover;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {

    private static final String PREFS_NAME = "AgriRoverPrefs";
    private static final String KEY_LAPTOP_URL = "laptop_url";
    private static final String DEFAULT_LAPTOP_URL = "http://192.168.93.173:5001/";
    private static final String STANDALONE_URL = "file:///android_asset/index.html";

    private WebView mWebView;
    private FrameLayout mRootLayout;
    private LinearLayout mErrorLayout;
    private TextView mErrorText;
    private SharedPreferences mPrefs;
    private long mLastBackPressTime = 0;

    public class WebAppInterface {
        Context mContext;

        WebAppInterface(Context c) {
            mContext = c;
        }

        @JavascriptInterface
        public void sendCommand(final String urlString) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        URL url = new URL(urlString);
                        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                        conn.setRequestMethod("GET");
                        conn.setConnectTimeout(600);
                        conn.setReadTimeout(600);
                        conn.getResponseCode();
                        conn.disconnect();
                    } catch (Exception ignored) {
                    }
                }
            }).start();
        }

        @JavascriptInterface
        public String fetchUrl(final String urlString) {
            try {
                URL url = new URL(urlString);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(1200);
                conn.setReadTimeout(1200);
                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    sb.append(line);
                }
                reader.close();
                conn.disconnect();
                return sb.toString();
            } catch (Exception e) {
                return null;
            }
        }

        @JavascriptInterface
        public void showToast(final String message) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show();
                }
            });
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        mPrefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);

        mRootLayout = new FrameLayout(this);
        mRootLayout.setBackgroundColor(Color.parseColor("#0f1612"));

        mWebView = new WebView(this);
        mWebView.setBackgroundColor(Color.parseColor("#0f1612"));
        FrameLayout.LayoutParams webViewParams = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        );
        mWebView.setLayoutParams(webViewParams);

        configureWebSettings();

        mWebView.addJavascriptInterface(new WebAppInterface(this), "Android");

        mWebView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                callback.invoke(origin, true, false);
            }
        });

        mWebView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                hideError();
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                if (failingUrl != null && failingUrl.startsWith("http")) {
                    showError("Cannot connect to Laptop Server at:\n" + failingUrl + "\n\nMake sure your laptop is turned on, running app.py, and connected to the 'phone1' hotspot.");
                }
            }
        });

        mRootLayout.addView(mWebView);

        setupFloatingButtons();
        setupErrorOverlay();

        setContentView(mRootLayout);

        // Load the full-power Laptop AI server by default!
        loadLaptopDashboard();
    }

    private void configureWebSettings() {
        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
    }

    private void setupFloatingButtons() {
        Button btnSettings = new Button(this);
        btnSettings.setText("⚙ IP");
        btnSettings.setTextColor(Color.WHITE);
        btnSettings.setBackgroundColor(Color.argb(160, 40, 167, 69));
        btnSettings.setTextSize(11);
        FrameLayout.LayoutParams btnParams = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.WRAP_CONTENT,
            FrameLayout.LayoutParams.WRAP_CONTENT
        );
        btnParams.gravity = Gravity.TOP | Gravity.END;
        btnParams.setMargins(0, 12, 12, 0);
        btnSettings.setLayoutParams(btnParams);
        btnSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showConfigDialog();
            }
        });
        mRootLayout.addView(btnSettings);
    }

    private void setupErrorOverlay() {
        mErrorLayout = new LinearLayout(this);
        mErrorLayout.setOrientation(LinearLayout.VERTICAL);
        mErrorLayout.setGravity(Gravity.CENTER);
        mErrorLayout.setBackgroundColor(Color.parseColor("#0f1612"));
        mErrorLayout.setPadding(32, 32, 32, 32);
        FrameLayout.LayoutParams errParams = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        );
        mErrorLayout.setLayoutParams(errParams);
        mErrorLayout.setVisibility(View.GONE);

        mErrorText = new TextView(this);
        mErrorText.setTextColor(Color.parseColor("#e8f0ec"));
        mErrorText.setTextSize(15);
        mErrorText.setGravity(Gravity.CENTER);
        mErrorLayout.addView(mErrorText);

        Button btnRetry = new Button(this);
        btnRetry.setText("🔄 Retry Laptop Connection");
        btnRetry.setBackgroundColor(Color.parseColor("#28a745"));
        btnRetry.setTextColor(Color.WHITE);
        LinearLayout.LayoutParams btnRetryParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        );
        btnRetryParams.setMargins(0, 24, 0, 10);
        btnRetry.setLayoutParams(btnRetryParams);
        btnRetry.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideError();
                loadLaptopDashboard();
            }
        });
        mErrorLayout.addView(btnRetry);

        Button btnDirectMode = new Button(this);
        btnDirectMode.setText("📱 Open Direct ESP32 Mode (Laptop OFF)");
        btnDirectMode.setBackgroundColor(Color.parseColor("#17a2b8"));
        btnDirectMode.setTextColor(Color.WHITE);
        btnDirectMode.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideError();
                mWebView.loadUrl(STANDALONE_URL);
            }
        });
        mErrorLayout.addView(btnDirectMode);

        Button btnChangeIp = new Button(this);
        btnChangeIp.setText("⚙ Change Laptop IP");
        btnChangeIp.setBackgroundColor(Color.parseColor("#495057"));
        btnChangeIp.setTextColor(Color.WHITE);
        LinearLayout.LayoutParams btnIpParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        );
        btnIpParams.setMargins(0, 10, 0, 0);
        btnChangeIp.setLayoutParams(btnIpParams);
        btnChangeIp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showConfigDialog();
            }
        });
        mErrorLayout.addView(btnChangeIp);

        mRootLayout.addView(mErrorLayout);
    }

    private void loadLaptopDashboard() {
        String url = mPrefs.getString(KEY_LAPTOP_URL, DEFAULT_LAPTOP_URL);
        mWebView.loadUrl(url);
    }

    private void showError(String msg) {
        mErrorText.setText(msg);
        mErrorLayout.setVisibility(View.VISIBLE);
    }

    private void hideError() {
        mErrorLayout.setVisibility(View.GONE);
    }

    private void showConfigDialog() {
        final EditText input = new EditText(this);
        String currentUrl = mPrefs.getString(KEY_LAPTOP_URL, DEFAULT_LAPTOP_URL);
        input.setText(currentUrl);

        new AlertDialog.Builder(this)
            .setTitle("Rover Dashboard Mode")
            .setMessage("Enter Laptop Server URL (runs full AI & OpenCV models):")
            .setView(input)
            .setPositiveButton("Connect Laptop", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    String newUrl = input.getText().toString().trim();
                    if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
                        newUrl = "http://" + newUrl;
                    }
                    if (!newUrl.endsWith("/")) {
                        newUrl += "/";
                    }
                    mPrefs.edit().putString(KEY_LAPTOP_URL, newUrl).apply();
                    hideError();
                    mWebView.loadUrl(newUrl);
                    Toast.makeText(MainActivity.this, "Connecting to Laptop: " + newUrl, Toast.LENGTH_SHORT).show();
                }
            })
            .setNeutralButton("Direct Mode (No Laptop)", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    hideError();
                    mWebView.loadUrl(STANDALONE_URL);
                }
            })
            .setNegativeButton("Cancel", null)
            .show();
    }

    @Override
    public void onBackPressed() {
        if (mWebView.canGoBack()) {
            mWebView.goBack();
        } else {
            if (System.currentTimeMillis() - mLastBackPressTime < 2000) {
                super.onBackPressed();
            } else {
                mLastBackPressTime = System.currentTimeMillis();
                Toast.makeText(this, "Press back again to exit AgriRover", Toast.LENGTH_SHORT).show();
            }
        }
    }
}
