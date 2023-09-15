package com.example.biotulding

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.AppCompatSpinner
import okhttp3.*
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.io.Serializable

class NewBuildingActivity: AppCompatActivity()  {
    var roomArray = ArrayList<String>()
    private val client = OkHttpClient()
    private lateinit var layoutList: LinearLayout
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.scheda_add_newbuilding)
        layoutList = findViewById(R.id.layout_list)

        val save_btn = findViewById<TextView>(R.id.button_save_newbuilding)
        val newRoom = findViewById<EditText>(R.id.edittext_newroom)
        val add_btn = findViewById<Button>(R.id.button_addroom)
        add_btn.setOnClickListener {
            val newRoomText = newRoom.text.toString()
            roomArray.add(newRoomText)
            println(roomArray)
            newRoom.setText("")
            //val buildingName = intent.getStringExtra("NameBuilding")
      }
        save_btn.setOnClickListener {
            val NewBuildingName = findViewById<EditText>(R.id.editText_name_newbuilding).text.toString()
            println(roomArray)
            val jsonObject = JSONObject()
            jsonObject.put("building_name", NewBuildingName)
            val jsonArray = JSONArray(roomArray)
            jsonObject.put("rooms", jsonArray)
            println(jsonObject.toString())
            //Post for adding a new Building
            val name = intent.getStringExtra("name_user")
            val resource_url = intent.getStringExtra("url")
            val payload = jsonObject.toString()
            val requestBody = payload.toRequestBody()
            val request = Request.Builder()
                .post(requestBody)
                .url("$resource_url/building?type=owned&username=$name")
                .build()
            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    println("Fail")
                }
                override fun onResponse(call: Call, response: Response) {
                }
            })
            Toast.makeText(this,"NEW BUILDING ADDED", Toast.LENGTH_SHORT).show()
        }
    }

}