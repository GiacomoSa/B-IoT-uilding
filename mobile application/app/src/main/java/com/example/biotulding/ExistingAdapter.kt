import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.biotulding.R


class ExistingAdapter(
    private val buildingList: List<String>,
    private val onItemClick: (String) -> Unit
) : RecyclerView.Adapter<ExistingAdapter.ExistingViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ExistingViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.viewholder_existing, parent, false)
        return ExistingViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: ExistingViewHolder, position: Int) {
        val buildingName = buildingList[position]
        holder.bind(buildingName)
        holder.itemView.setOnClickListener {
            onItemClick(buildingName)
        }
    }

    override fun getItemCount(): Int {
        return buildingList.size
    }

    inner class ExistingViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val BuildingNameTextView_ex: TextView = itemView.findViewById(R.id.textView_buildingID_ex)

        init {
            itemView.setOnClickListener {
                onItemClick(buildingList[adapterPosition])
            }
        }

        fun bind(buildingName: String) {
            BuildingNameTextView_ex.text = buildingName
        }
    }
}