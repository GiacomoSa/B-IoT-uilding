package com.example.biotulding

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.AppCompatSpinner
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.*
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

class AddSensorActivity: AppCompatActivity() {
    private val client = OkHttpClient()
    var resource_url : String = ""
    val catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    var sensor_list = ArrayList<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.add_sensor_layout)
        val url = "http://10.0.2.2:9096/RC/getAllRCs"
        val spinner = findViewById<AppCompatSpinner>(R.id.spinner_sensori)
        val buildingID = intent.getStringExtra("buildingID")
        val roomID = intent.getStringExtra("roomID")
        val save_btn = findViewById<TextView>(R.id.textView_save)
        //First GEt
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = fetchData(url)
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
        //Second get
        Thread.sleep(100)
        GlobalScope.launch(Dispatchers.IO) {
            println("Room:$roomID")
            println("Building:$buildingID")
            try {
                val response = fetchData("$resource_url/sensor/missing?building_id=$buildingID&room_id=$roomID&catalog_id=$catalog_name")
                val jsonArray = JSONArray(response)
                println(jsonArray)
                for (i in 0 until jsonArray.length()) {
                    sensor_list.add(jsonArray.getString(i))
                    println("rimanenti:$sensor_list")
                }
            } catch (e: IOException) {
                Toast.makeText(baseContext,"No new sensor to add", Toast.LENGTH_SHORT)
            }
            runOnUiThread {
                val adapter = ArrayAdapter(this@AddSensorActivity, android.R.layout.simple_spinner_item, sensor_list)
                adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
                spinner.adapter = adapter
            }
        }

        spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val selectedItem = sensor_list[position]
                println(selectedItem)
                save_btn.setOnClickListener {
                    //POST
                    val jsonObject = JSONObject()
                    jsonObject.put("sensor_measure", selectedItem)
                    jsonObject.put("building_id", buildingID)
                    jsonObject.put("room_id", roomID)
                    jsonObject.put("catalog_id", catalog_name)
                    val payload = jsonObject.toString()
                    val requestBody = payload.toRequestBody()
                    val request = Request.Builder()
                        .post(requestBody)
                        .url("$resource_url/sensor")
                        .build()
                    client.newCall(request).enqueue(object : Callback {
                        override fun onFailure(call: Call, e: IOException) {
                            println("Fail")
                        }
                        override fun onResponse(call: Call, response: Response) {
                            println("Success")
                        }
                    })
                    val intent = Intent(this@AddSensorActivity,ShowRoomActivity::class.java)
                    startActivity(intent)
                }

            }

            override fun onNothingSelected(parent: AdapterView<*>?) {
            }
        }
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