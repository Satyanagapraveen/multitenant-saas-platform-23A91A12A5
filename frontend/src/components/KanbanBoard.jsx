import { useState, useEffect } from "react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import api from "../api/axios";

const COLUMNS = {
  todo: { title: "To Do", color: "bg-gray-100", borderColor: "border-gray-300" },
  in_progress: { title: "In Progress", color: "bg-yellow-50", borderColor: "border-yellow-300" },
  completed: { title: "Completed", color: "bg-green-50", borderColor: "border-green-300" },
};

function KanbanBoard({ tasks: initialTasks, onTaskUpdate, isAdmin }) {
  const [columns, setColumns] = useState({
    todo: [],
    in_progress: [],
    completed: [],
  });

  // Organize tasks into columns
  useEffect(() => {
    const organized = {
      todo: [],
      in_progress: [],
      completed: [],
    };

    initialTasks.forEach((task) => {
      if (organized[task.status]) {
        organized[task.status].push(task);
      }
    });

    setColumns(organized);
  }, [initialTasks]);

  const handleDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    // Dropped outside
    if (!destination) return;

    // Same position
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return;
    }

    const sourceCol = source.droppableId;
    const destCol = destination.droppableId;

    // Find the task
    const task = columns[sourceCol].find((t) => t.id === draggableId);
    if (!task) return;

    // Optimistic update
    const newColumns = { ...columns };
    
    // Remove from source
    newColumns[sourceCol] = newColumns[sourceCol].filter((t) => t.id !== draggableId);
    
    // Add to destination
    const updatedTask = { ...task, status: destCol };
    newColumns[destCol] = [
      ...newColumns[destCol].slice(0, destination.index),
      updatedTask,
      ...newColumns[destCol].slice(destination.index),
    ];

    setColumns(newColumns);

    // API call to update status
    try {
      await api.patch(`/tasks/${draggableId}/status`, { status: destCol });
      if (onTaskUpdate) onTaskUpdate();
    } catch (err) {
      console.error("Failed to update task status", err);
      // Revert on error
      setColumns(columns);
      alert("Failed to update task. You may not have permission.");
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      high: "bg-red-100 text-red-700",
      medium: "bg-yellow-100 text-yellow-700",
      low: "bg-blue-100 text-blue-700",
    };
    return colors[priority] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="text-lg font-bold mb-4">Task Board</h3>
      
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(COLUMNS).map(([columnId, columnInfo]) => (
            <div
              key={columnId}
              className={`${columnInfo.color} rounded-lg p-3 border-2 ${columnInfo.borderColor}`}
            >
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-gray-700">{columnInfo.title}</h4>
                <span className="bg-white px-2 py-1 rounded text-sm font-medium">
                  {columns[columnId].length}
                </span>
              </div>

              <Droppable droppableId={columnId}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`min-h-[200px] space-y-2 ${
                      snapshot.isDraggingOver ? "bg-blue-50 rounded" : ""
                    }`}
                  >
                    {columns[columnId].map((task, index) => (
                      <Draggable
                        key={task.id}
                        draggableId={task.id}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`bg-white p-3 rounded shadow-sm border cursor-grab ${
                              snapshot.isDragging
                                ? "shadow-lg ring-2 ring-blue-400"
                                : "hover:shadow-md"
                            }`}
                          >
                            <h5 className="font-medium text-gray-800 mb-1">
                              {task.title}
                            </h5>
                            
                            {task.description && (
                              <p className="text-xs text-gray-500 mb-2 line-clamp-2">
                                {task.description}
                              </p>
                            )}

                            <div className="flex flex-wrap gap-1 items-center">
                              <span
                                className={`text-xs px-2 py-0.5 rounded ${getPriorityBadge(
                                  task.priority
                                )}`}
                              >
                                {task.priority}
                              </span>

                              {task.assigned_to && (
                                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                                  {task.assigned_to.full_name?.split(" ")[0] || "Assigned"}
                                </span>
                              )}

                              {task.due_date && (
                                <span className="text-xs text-gray-400">
                                  📅 {task.due_date}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
}

export default KanbanBoard;
