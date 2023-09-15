import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.biotulding.R


class BuildingAdapter(
    private val buildingList: List<String>,
    private val onItemClick: (String) -> Unit
) : RecyclerView.Adapter<BuildingAdapter.BuildingViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BuildingViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.viewholder_mybuildings_home, parent, false)
        return BuildingViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: BuildingViewHolder, position: Int) {
        val buildingName = buildingList[position]
        holder.bind(buildingName)
        holder.itemView.setOnClickListener {
            onItemClick(buildingName)
        }
    }

    override fun getItemCount(): Int {
        return buildingList.size
    }

    inner class BuildingViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val BuildingNameTextView: TextView = itemView.findViewById(R.id.textView_buildingID)

        init {
            itemView.setOnClickListener {
                onItemClick(buildingList[adapterPosition])
            }
        }

        fun bind(buildingName: String) {
            BuildingNameTextView.text = buildingName
        }
    }
}
