package com.example.biotulding
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.biotulding.R

class SensorAdapter(
    private val sensorList: List<String>,
    private val onItemClick: (String) -> Unit
)
    : RecyclerView.Adapter<SensorAdapter.SensorViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SensorViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.viewholder_sensors, parent, false)
        return SensorViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: SensorViewHolder, position: Int) {
        val sensorName = sensorList[position]
        holder.bind(sensorName)
        holder.itemView.setOnClickListener {
            onItemClick(sensorName)
        }

        val split = sensorName.split(':')
        val sensor = split[0]
        val value = split[1]
        holder.sensorNameTextView.text = sensor
        holder.sensorValueTextView.text = value
        if (sensor == "temperature"){
            holder.imageView.setImageResource(R.drawable.icon_temp)
        }
        else if (sensor == "humidity"){
            holder.imageView.setImageResource(R.drawable.icon_humidity)
        }
        else if (sensor == "particulate"){
            holder.imageView.setImageResource(R.drawable.icon_particulate)
        }
        else if (sensor == "motion"){
            holder.imageView.setImageResource(R.drawable.icon_motion)
        }

    }

    override fun getItemCount(): Int {
        return sensorList.size
    }

    inner class SensorViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val imageView: ImageView = itemView.findViewById(R.id.imageView_sensor)
        val sensorNameTextView: TextView = itemView.findViewById(R.id.textView_type_sensor)
        val sensorValueTextView: TextView = itemView.findViewById(R.id.textView_sensor_value)
        init {
            itemView.setOnClickListener {
                onItemClick(sensorList[adapterPosition])
            }
        }

        fun bind(sensorName: String) {
            sensorNameTextView.text = sensorName
        }
    }
}