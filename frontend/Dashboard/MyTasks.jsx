import api from "../src/api/axios";

function MyTasks({ tasks, onStatusChange }) {
  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await api.patch(`/tasks/${taskId}/status`, { status: newStatus });
      if (onStatusChange) onStatusChange(); // refresh data
    } catch (err) {
      console.error("Failed to update task status", err);
      alert("Failed to update status");
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-700";
      case "in_progress":
        return "bg-yellow-100 text-yellow-700";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  return (
    <div className="bg-white shadow rounded p-4">
      <h3 className="text-lg font-bold mb-3">My Tasks</h3>

      {tasks.length === 0 ? (
        <p className="text-gray-500">No tasks assigned.</p>
      ) : (
        <ul className="space-y-3">
          {tasks.map((task) => (
            <li
              key={task.id}
              className="flex justify-between items-center border-b pb-2"
            >
              <div>
                <span className="font-medium">{task.title}</span>
                {task.project?.name && (
                  <p className="text-xs text-gray-400">{task.project.name}</p>
                )}
              </div>

              <select
                value={task.status}
                onChange={(e) => handleStatusChange(task.id, e.target.value)}
                className={`text-sm px-2 py-1 rounded border cursor-pointer ${getStatusColor(task.status)}`}
              >
                <option value="todo">Todo</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MyTasks;
