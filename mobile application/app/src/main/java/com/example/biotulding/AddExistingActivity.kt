package com.example.biotulding

import AddExistingAdapter
import android.os.Bundle
import android.util.Log
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.ItemTouchHelper
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.*
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import java.io.IOException

class AddExistingActivity: AppCompatActivity() {
    private val client = OkHttpClient()
    var list_building = ArrayList<String>()
    var list_building_new = ArrayList<String>()
    private lateinit var recyclerView: RecyclerView
    private lateinit var buildingadapter: AddExistingAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.add_existing)
        val resource_url = intent.getStringExtra("res_url")
        val name = intent.getStringExtra("name")
        GlobalScope.launch(Dispatchers.IO) {
            try {
                println("NOME: $name")
                val response = fetchData("$resource_url/building/remainingBuildings?username=$name")
                val jsonArray = JSONArray(response)
                if (jsonArray.length() > 0) {
                    for (i in 0 until jsonArray.length()) {
                        list_building.add(jsonArray.getString(i))
                        val tmp = jsonArray.getString(i)
                        val tmp2 = tmp.split(':')
                        val tmp3 = tmp2[0]
                        list_building_new.add(tmp3)
                        val tmp4 = tmp2[1]
                    }
                }
            } catch (e: IOException) {
                println("Error")
            }
            val newbuildings_number =
            findViewById<TextView>(R.id.textView_card_new_number)
            newbuildings_number.text = list_building_new.size.toString()
        }
        recyclerView = findViewById(R.id.recview_new_building)
        buildingadapter =
            AddExistingAdapter(getSampleBuildingData(list_building_new)) { buildingName ->
                //building_name = buildingName
            }
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = buildingadapter
        val swipe = object : SwipeGesture(){
            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
                val position = viewHolder.adapterPosition
                println("AGGIUNTO")
                Toast.makeText(this@AddExistingActivity,"BUILDING FOLLOWED",Toast.LENGTH_SHORT).show()
                //PUT
                for (i in 0 until list_building.size) {
                    val tmp = list_building[i]
                    val split = tmp.split(':')
                    val name_building = split[0]
                    val id_building = split[1]
                    if (list_building_new[position] == name_building){
                        val payload = "{\"username\":\"$name\",\"building_id\":\"$id_building\"}"
                        val requestBody = payload.toRequestBody()
                        val request = Request.Builder()
                            .put(requestBody)
                            .url("$resource_url/user/building?type=observed")
                            .build()
                        client.newCall(request).enqueue(object : Callback {
                            override fun onFailure(call: Call, e: IOException) {
                                println("Fail")
                            }
                            override fun onResponse(call: Call, response: Response) {
                                println("Succes")
                            }
                        })
                        break
                    }
                }
            }
        }
        val itemTouchHelper = ItemTouchHelper(swipe)
        itemTouchHelper.attachToRecyclerView(recyclerView)
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