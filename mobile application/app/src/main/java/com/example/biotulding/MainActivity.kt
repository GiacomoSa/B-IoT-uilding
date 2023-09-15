package com.example.biotulding

import BuildingAdapter
import android.content.DialogInterface
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

class MainActivity : AppCompatActivity() {
    private val client = OkHttpClient()
    private lateinit var recyclerView: RecyclerView
    private lateinit var buildingadapter: BuildingAdapter
    var list_buildings_owned  = ArrayList<String>()
    var list_buildings_observed  = ArrayList<String>()
    var list_name_building_owned = ArrayList<String>()
    var list_name_building_observed = ArrayList<String>()
    var building_name = ""
    var resource_url = ""
    var catalog_name : String = "B(IoT)uilding"
    var appHost: String = ""
    var port: String = ""
    var name_usr = ""
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.main_mybuilding)
        val url = "http://10.0.2.2:9096/RC/getAllRCs"
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


        Thread.sleep(100)
        recyclerView = findViewById(R.id.recview_mybuildings)
        recyclerView.layoutManager = LinearLayoutManager(this)
        val name = intent.getStringExtra("name")
        if (name != null) {
            name_usr = name
        }
        println("nome:$name")
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = fetchData("$resource_url/building/ofUser?username=$name")
                val response_object = JSONObject(response)
                val owned_bildings = response_object.getJSONArray("owned_buildings")
                val observed_buildings = response_object.getJSONArray("observed_buildings")
                //val buildings = JSONArray(response)
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
            val mybuildings_number = findViewById<TextView>(R.id.textView_card_mybuildings_number)
            mybuildings_number.text = list_buildings_owned.size.toString()
            val following_number = findViewById<TextView>(R.id.textView_card_following_number)
            following_number.text = list_buildings_observed.size.toString()
        }

        var name_building = ""
        Thread.sleep(200)
        buildingadapter = BuildingAdapter(getSampleBuildingData(list_name_building_owned)) { buildingName ->
            building_name = buildingName
            val intent = Intent(this, ShowRoomActivity::class.java)
            for (i in 0 until list_buildings_owned.size){
                val tmp = list_buildings_owned[i]
                val tmp2 = tmp.split(':')
                val tmp3 = tmp2[0]
                name_building=tmp3
                val tmp4 = tmp2[1]
                if (tmp3 == building_name){
                    intent.putExtra("building_complete",tmp)
                    intent.putExtra("id", tmp4)

                }
                break
            }
            intent.putStringArrayListExtra("Building_owned",list_buildings_owned)
            intent.putStringArrayListExtra("Building_obs",list_buildings_observed)
            startActivity(intent)
        }

        recyclerView.adapter = buildingadapter

        val addNew_btn =findViewById<TextView>(R.id.textView_addbuilding)
        addNew_btn.setOnClickListener {
            val intent = Intent(this, NewBuildingActivity::class.java)
            intent.putExtra("name_user",name)
            intent.putExtra("url",resource_url)
            startActivity(intent)
        }
        val add_existing = findViewById<ImageView>(R.id.imageView_occhio)
        add_existing.setOnClickListener {
            val intent = Intent(this, ExistingBuildingActivity::class.java)
            intent.putStringArrayListExtra("Building_obs",list_buildings_observed)
            intent.putExtra("name_user",name)
            intent.putExtra("url",resource_url)
            intent.putExtra("name_building",name_building)
            startActivity(intent)
        }
        val delete_profile = findViewById<ImageView>(R.id.imageView_delete)
        delete_profile.setOnClickListener {
            showConfirmationDialog()
        }

    }
    private fun showConfirmationDialog() {
        val builder = AlertDialog.Builder(this)

        builder.setTitle("Confirm account elimination")
        builder.setMessage("Are you sure you want to delete the account?")

        builder.setPositiveButton("Yes") { _: DialogInterface, _: Int ->
            println(name_usr)
            val request = Request.Builder()
                .delete()
                .url("$resource_url/user?id=$name_usr")
                .build()
            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    println("Fail")
                }
                override fun onResponse(call: Call, response: Response) {
                }
            })
            val intent = Intent(this,LoginActivity::class.java)
            startActivity(intent)
        }

        builder.setNegativeButton("No") { _: DialogInterface, _: Int ->
        }

        builder.show()
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