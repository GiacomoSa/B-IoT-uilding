package com.example.biotulding

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONArray
import java.io.IOException

class ShowSensorActivityObs: AppCompatActivity() {
    private val client = OkHttpClient()
    var resource_url : String = ""
    var catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    var connector_url : String = ""
    var sensor_list = ArrayList<String>()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.sensor_obs)


        val url = "http://10.0.2.2:9096/RC/getAllRCs"
        val roomid = intent.getStringExtra("roomName")
        println("Room:$roomid")
        val building_id = intent.getStringExtra("building_id")
        println("Building:$building_id")
        //First Get
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
                    println("Port: $port")
                    println("App Host: $appHost")
                    resource_url = "$appHost:$port"
                    println("Resource: $resource_url")
                }
            } catch (e: IOException) {
                println("Error")
            }
        }

        //Second get
        Thread.sleep(100)
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = fetchData("$resource_url/resource?id=all")
                val jsonArray = JSONArray(response)
                for (i in 0 until jsonArray.length()) {
                    val jsonObject = jsonArray.getJSONObject(i)
                    if (jsonObject.getString("catalog_id") == catalog_name) {
                        val connectorAppHost = jsonObject.getString("app_host")
                        val connectorPort = jsonObject.getString("port")
                        connector_url = "$connectorAppHost:$connectorPort"
                        break
                    }
                }
            } catch (e: IOException) {
                println("Error")
            }
        }

        //Third Get
        Thread.sleep(200)
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = fetchData("$connector_url/Data/sensor?building_id=$building_id&room_id=$roomid")
                val jsonArray = JSONArray(response)
                println("Mammt")
                println(jsonArray)
                for (i in 0 until jsonArray.length()) {
                    sensor_list.add(jsonArray.getString(i))
                }
            } catch (e: IOException) {
                println("Error")
            }
        }
        Thread.sleep(300)
        println(sensor_list)
        //For the list of sensors
        val recyclerView: RecyclerView = findViewById(R.id.recview_mysensors)
        recyclerView.layoutManager = GridLayoutManager(this,2)
        recyclerView.adapter = SensorAdapter(getSampleSensor(sensor_list)){ sensorName ->
        }

        val statistic_btn = findViewById<FloatingActionButton>(R.id.circularButton_thingspeak_obs)
        statistic_btn.setOnClickListener{
            val intent = Intent(this, ThingSpeakActivity::class.java)
            startActivity(intent)
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

    private fun getSampleSensor(customList: List<String>): List<String> {
        return customList
    }
}