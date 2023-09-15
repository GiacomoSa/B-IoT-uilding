package com.example.biotulding

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import com.example.biotulding.MainActivity
import com.example.biotulding.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONArray
import java.io.IOException

class LoginActivity: AppCompatActivity()  {
    private val client = OkHttpClient()
    var resource_url : String = ""
    var catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    var listUser : JSONArray = JSONArray()
    var listDevice : JSONArray = JSONArray()
    @RequiresApi(33)
    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)
        setContentView(R.layout.singin_activity)


        val login_btn = findViewById<Button>(R.id.login_btn)

        val singn_up_btn = findViewById<TextView>(R.id.sign_up_text)

        val username = findViewById<EditText>(R.id.username_text)
        val password = findViewById<EditText>(R.id.password_text)
        if (username.text.isEmpty() || password.text.isEmpty()){
            Toast.makeText(this,"Please fill all the fields", Toast.LENGTH_SHORT).show()
        }


        val url = "http://10.0.2.2:9096/RC/getAllRCs"

        //First Get
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = fetchData(url)
                println("xxx")
                println(response)
                val jsonArray = JSONArray(response)
                if (jsonArray.length() > 0) {
                    for (i in 0 until jsonArray.length()) {
                        val Object = jsonArray.getJSONObject(i)
                        if (Object.getString("catalog_name")==catalog_name){
                            appHost = Object.getString("app_host")
                            port = Object.getString("port")
                        }
                        break
                    }
                    println("Port: $port")
                    println("App Host: $appHost")
                    resource_url = "$appHost:$port"
                    println("Resource: $resource_url")
                }
            } catch (e: IOException) {
                println("Error")
            }
        }




        Thread.sleep(500)
        //Second Get
        GlobalScope.launch(Dispatchers.IO) {
            try {
                println(resource_url)
                val response = fetchData("$resource_url/user?id=all")
                listUser = JSONArray(response)
                println(response)
            } catch (e: IOException) {
                println("Error")
            }
        }
        //Third Get
        Thread.sleep(1000)
        GlobalScope.launch(Dispatchers.IO) {
            try {
                println(resource_url)
                val response = fetchData("$resource_url/resource?id=all")
                listDevice = JSONArray(response)
                println(response)
            } catch (e: IOException) {
                println("Error")
            }
        }


        //Sign Up button
        singn_up_btn.setOnClickListener{
            val intent = Intent(this,SignUpActivity::class.java)
            startActivity(intent)
        }
        //LogIn Button
        login_btn.setOnClickListener{
            var flag = false
            val usernameinput = username.text.toString()
            val passwordinput= password.text.toString()
            for (i in 0 until listUser.length()) {
                val Object = listUser.getJSONObject(i)
                if (Object.getString("username")==usernameinput){

                    flag = true
                    if (Object.getString("pw")==passwordinput){
                        val intent = Intent(this, MainActivity::class.java)
                        intent.putExtra("name", usernameinput)
                        //intent.putExtra("res_url",resource_url)
                        startActivity(intent)
                        Toast.makeText(baseContext, "Succes", Toast.LENGTH_SHORT).show()
                        break
                    }
                }

            }
            if (!flag){
                Toast.makeText(baseContext, "Username not correct", Toast.LENGTH_SHORT).show()
            }

        }
    }
        @Throws(IOException::class)
        private fun fetchData(url: String): String {
            val request = Request.Builder()
                .url(url)
                .build()

            client.newCall(request).execute().use { response ->
                return response.body?.string() ?: ""
            }

        }
}
