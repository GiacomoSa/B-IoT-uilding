package com.example.biotulding
import android.app.ProgressDialog
import android.content.Intent
import android.os.Bundle
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.ActionBar
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.AppCompatButton
import com.example.biotulding.MainActivity
import com.example.biotulding.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.*
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import java.io.IOException

class SignUpActivity: AppCompatActivity() {
    //ActionBar
    private lateinit var actionBar: ActionBar
    private val client = OkHttpClient()
    var flag = true
    var resource_url : String = ""
    var catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.signup_activity)
        val login = findViewById<TextView>(R.id.sign_in_textView)
        login.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }
        val signup_btn = findViewById<AppCompatButton>(R.id.sign_button)
        signup_btn.setOnClickListener {
            performSignup()
            if (flag) {
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
                Toast.makeText(baseContext, "Succes", Toast.LENGTH_SHORT).show()
            }
        }

    }

    private fun performSignup() {
        val name = findViewById<EditText>(R.id.nameUser_text)
        val email = findViewById<EditText>(R.id.email_text)
        val password = findViewById<EditText>(R.id.password_text)
        val inputname = name.text.toString()
        val inputemail = email.text.toString()
        val inputpassword = password.text.toString()

        if (name.text.isEmpty() || email.text.isEmpty() || password.text.isEmpty()) {
            Toast.makeText(baseContext, "Please fill all the fields", Toast.LENGTH_SHORT).show()
        }
        val url = "http://10.0.2.2:9096/RC/getAllRCs"

        //GET
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
                    resource_url = "$appHost:$port"
                }
            } catch (e: IOException) {
                println("Error")
            }
        }

        //POST
          Thread.sleep(500)
          val payload = "{\"username\":\"$inputname\",\"email\":\"$inputemail\",\"pw\":\"$inputpassword\",\"buildings\":[]}"
          val requestBody = payload.toRequestBody()
          val request = Request.Builder()
              .post(requestBody)
              .url("$resource_url/user")
              .build()
          client.newCall(request).enqueue(object : Callback {
              override fun onFailure(call: Call, e: IOException) {
                  println("Fail")
              }
              override fun onResponse(call: Call, response: Response) {
                  if (!response.isSuccessful) {
                      flag = false
                      println("User already existing")
                  }
              }
          })
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
