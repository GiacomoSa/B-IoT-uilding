package com.example.biotulding

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException

class ThingSpeakActivity:AppCompatActivity() {
    private lateinit var webView: WebView
    private val client = OkHttpClient()


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.link_to_web)
        webView = findViewById(R.id.webView)
        val resource_url = intent.getStringExtra("url").toString()
        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webView.webViewClient = WebViewClient()
        println("Response: $resource_url")
        webView.loadUrl(resource_url)
        // Open the web on the app
        //


    }
    @Throws(IOException::class)
    fun fetchData(url: String): String {
        val request = Request.Builder()
            .url(url)
            .build()
        client.newCall(request).execute().use { response ->
            return response.body?.string() ?:""
        }

    }
}