package com.example.biotulding

import RoomAdapter
import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

class ShowRoomActivity: AppCompatActivity() {
    private lateinit var roomAdapter: RoomAdapter
    private val client = OkHttpClient()
    var list_buildings  = listOf<String>()
    var resource_url : String = ""
    var catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.stanze_buildings)

        val url = "http://10.0.2.2:9096/RC/getAllRCs"
        val recyclerView: RecyclerView = findViewById(R.id.recyclerView)

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

        //Second Get
        val building_id = intent.getStringExtra("id")
        val building_complete = intent.getStringExtra("building_complete")
        //Second Get
        var rooms_list = listOf<String>()
        Thread.sleep(200)
        GlobalScope.launch(Dispatchers.IO) {
            try {
                println("$resource_url/building?id=$building_id")
                val response = fetchData("$resource_url/building?id=$building_id")
                println(response)
                val jsonObject = JSONObject(response)
                val rooms = jsonObject.getJSONArray("rooms")
                val list_room = ArrayList<String>()
                for (i in 0 until rooms.length()) {
                    list_room.add(rooms.getString(i))
                }
                rooms_list = list_room
            } catch (e: IOException) {
                println("Error")
            }

        }
        println(rooms_list)
        val list_building_obs = intent.getStringArrayListExtra("Building_obs")
        val list_building_owned = intent.getStringArrayListExtra("Building_owned")
        var flag = ""
        ShowRoomActivity().runOnUiThread{
            roomAdapter = RoomAdapter(getSampleRoomData(rooms_list)) { roomName ->
                for (i in 0 until list_building_owned!!.size){
                    val tmp = list_building_owned[i]
                    val tmp2 = tmp.split(':')
                    val tmp3 = tmp2[0]
                    val tmp4 = tmp2[1]
                    if (tmp4 == building_id){
                        flag = "owned"
                        break
                    }

                }
                for (i in 0 until list_building_obs!!.size){
                    val tmp = list_building_obs[i]
                    val tmp2 = tmp.split(':')
                    val tmp3 = tmp2[0]
                    val tmp4 = tmp2[1]
                    if (tmp4 == building_id){
                        flag = "obs"
                        break
                    }
                }
                if (flag == "owned"){
                    val intent = Intent(this, ShowSensorActivityOwned::class.java)
                    intent.putExtra("roomName", roomName)
                    intent.putExtra("building_id",building_id)
                    startActivity(intent)
                }
                else if (flag == "obs"){
                    val intent = Intent(this, ShowSensorActivityObs::class.java)
                    intent.putExtra("roomName", roomName)
                    intent.putExtra("building_id",building_id)
                    startActivity(intent)
                }
            }
            recyclerView.layoutManager = GridLayoutManager(this,2)
            recyclerView.adapter = roomAdapter

        }

    }

    private fun getSampleRoomData(customList: List<String>): List<String> {
        return customList
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