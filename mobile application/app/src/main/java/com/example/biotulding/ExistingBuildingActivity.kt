package com.example.biotulding

import ExistingAdapter
import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

class ExistingBuildingActivity: AppCompatActivity() {
    private val client = OkHttpClient()
    private lateinit var recyclerView: RecyclerView
    private lateinit var buildingadapter: ExistingAdapter
    var list_buildings_owned  = ArrayList<String>()
    var list_buildings_observed  = ArrayList<String>()
    var list_name_building_owned = ArrayList<String>()
    var list_name_building_observed = ArrayList<String>()
    var list_building = ArrayList<String>()
    var building_name = ""
    var resource_url = ""
    var catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.followed_building)
        val url = "http://10.0.2.2:9096/RC/getAllRCs"
        //First Get
            GlobalScope.launch(Dispatchers.IO) {
                try {
                    val response = fetchData(url)
                    val jsonArray = JSONArray(response)
                    if (jsonArray.length() > 0) {
                        for (i in 0 until jsonArray.length()) {
                            val Object = jsonArray.getJSONObject(i)
                            if (Object.getString("catalog_name") == catalog_name) {
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


            Thread.sleep(100)
            recyclerView = findViewById(R.id.recview_followed_building)
            val name = intent.getStringExtra("name_user")
            println("nome:$name")
            ExistingBuildingActivity().runOnUiThread {
                GlobalScope.launch(Dispatchers.IO) {
                    try {
                        val response = fetchData("$resource_url/building/ofUser?username=$name")
                        val response_object = JSONObject(response)
                        val owned_bildings = response_object.getJSONArray("owned_buildings")
                        val observed_buildings = response_object.getJSONArray("observed_buildings")
                        for (i in 0 until owned_bildings.length()) {
                            list_buildings_owned.add(owned_bildings.getString(i))
                            val tmp = owned_bildings.getString(i)
                            val tmp2 = tmp.split(':')
                            val tmp3 = tmp2[0]
                            list_name_building_owned.add(tmp3)
                            println(list_name_building_owned)
                        }
                        for (i in 0 until observed_buildings.length()) {
                            list_buildings_observed.add(observed_buildings.getString(i))
                            val tmp = observed_buildings.getString(i)
                            val tmp2 = tmp.split(':')
                            val tmp3 = tmp2[0]
                            list_name_building_observed.add(tmp3)
                            println(list_name_building_observed)
                        }


                        println(response)
                    } catch (e: IOException) {
                        println("Error")
                    }
                    val mybuildings_number =
                        findViewById<TextView>(R.id.textView_card_mybuildings_number_2)
                    mybuildings_number.text = list_buildings_owned.size.toString()
                    val following_number =
                        findViewById<TextView>(R.id.textView_card_following_number_2)
                    following_number.text = list_buildings_observed.size.toString()

                }


                buildingadapter =
                    ExistingAdapter(getSampleBuildingData(list_name_building_observed)) { buildingName ->
                        building_name = buildingName
                    }
                recyclerView.layoutManager = LinearLayoutManager(this)
                recyclerView.adapter = buildingadapter
                Thread.sleep(200)

                GlobalScope.launch(Dispatchers.IO) {
                    try {
                        println("NOME: $name")
                        val response = fetchData("$resource_url/building/remainingBuildings?username=$name")
                        println(response)
                        val jsonArray = JSONArray(response)
                        println(jsonArray)
                        if (jsonArray.length() > 0) {
                            for (i in 0 until jsonArray.length()) {
                                list_building.add(jsonArray.getString(i))
                                val tmp = jsonArray.getString(i)
                                val tmp2 = tmp.split(':')
                                val tmp3 = tmp2[0]
                                val tmp4 = tmp2[1]
                                //list_name_building.add(tmp3)
                            }
                        }
                    } catch (e: IOException) {
                        println("Error")
                    }
                }

                val btn_existin = findViewById<TextView>(R.id.textView_addexisting)
                val buildingName = intent.getStringExtra("name_building")
                btn_existin.setOnClickListener {
                    val intent = Intent(this, AddExistingActivity::class.java)
                    intent.putExtra("res_url",resource_url)
                    intent.putExtra("name",name)
                    intent.putExtra("buildingname",buildingName)
                    startActivity(intent)
                }
            }

    }
    private fun getSampleBuildingData(customList: List<String>): List<String> {
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