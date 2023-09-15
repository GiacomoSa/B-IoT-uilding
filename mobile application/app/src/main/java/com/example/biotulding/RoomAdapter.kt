import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.biotulding.R


class RoomAdapter(
    private val roomList: List<String>,
    private val onItemClick: (String) -> Unit
) : RecyclerView.Adapter<RoomAdapter.RoomViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RoomViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.viewholder_stanze, parent, false)
        return RoomViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: RoomViewHolder, position: Int) {
        val roomName = roomList[position]
        holder.bind(roomName)
        holder.itemView.setOnClickListener {
            onItemClick(roomName)
        }
    }

    override fun getItemCount(): Int {
        return roomList.size
    }

    inner class RoomViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val roomNameTextView: TextView = itemView.findViewById(R.id.textView_Nomestanza)

        init {
            itemView.setOnClickListener {
                onItemClick(roomList[adapterPosition])
            }
        }

        fun bind(roomName: String) {
            roomNameTextView.text = roomName
        }
    }
}

