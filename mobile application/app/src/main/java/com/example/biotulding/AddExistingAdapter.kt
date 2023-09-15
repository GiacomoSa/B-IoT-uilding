import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.biotulding.R


class AddExistingAdapter(
    private val buildingList: List<String>,
    private val onItemClick: (String) -> Unit
) : RecyclerView.Adapter<AddExistingAdapter.AddExistingViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AddExistingViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.viewholder_new, parent, false)
        return AddExistingViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: AddExistingViewHolder, position: Int) {
        val buildingName = buildingList[position]
        holder.bind(buildingName)
        holder.itemView.setOnClickListener {
            onItemClick(buildingName)
        }
    }

    override fun getItemCount(): Int {
        return buildingList.size
    }

    inner class AddExistingViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val BuildingNameTextView_new: TextView = itemView.findViewById(R.id.textView_buildingID_new)

        init {
            itemView.setOnClickListener {
                onItemClick(buildingList[adapterPosition])
            }
        }

        fun bind(buildingName: String) {
            BuildingNameTextView_new.text = buildingName
        }
    }
}