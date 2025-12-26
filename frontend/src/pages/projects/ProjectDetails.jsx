import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../api/axios";
import { useAuth } from "../../context/AuthContext";
import CreateTaskModal from "../../tasks/CreateTaskModal";
import EditTaskModal from "../../tasks/EditTaskModal";
import EditProjectModal from "./EditProjectModal";
import KanbanBoard from "../../components/KanbanBoard";

function ProjectDetails() {
  const { projectId } = useParams();
  const { user } = useAuth();

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [showEditProject, setShowEditProject] = useState(false);
  const [viewMode, setViewMode] = useState("kanban"); // "kanban" or "list"

  // 🔁 Move fetch logic outside useEffect so it can be reused
  const fetchProjectData = async () => {
    try {
      const [projectRes, tasksRes] = await Promise.all([
        api.get(`/projects/${projectId}`),
        api.get(`/projects/${projectId}/tasks`),
      ]);

      setProject(projectRes.data.data);
      setTasks(tasksRes.data.data.tasks || []);
    } catch (err) {
      console.error("Failed to load project details", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  if (loading) return <p className="p-6">Loading project...</p>;
  if (!project) return <p className="p-6">Project not found</p>;

  return (
    <div className="p-6 space-y-6">
      {/* Project Info */}
      <div className="bg-white p-6 rounded shadow">
        <div className="flex justify-between">
          <div>
            <h1 className="text-2xl font-bold">{project.name}</h1>
            <p className="text-gray-600">{project.description}</p>
            <span className="text-sm text-gray-400">
              Status: {project.status}
            </span>
          </div>

          {user?.role === "tenant_admin" && (
            <button
              onClick={() => setShowEditProject(true)}
              className="text-blue-600 hover:underline"
            >
              Edit Project
            </button>
          )}
        </div>
      </div>

      {/* Tasks Section */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold">Tasks</h2>
            
            {/* View Toggle */}
            <div className="flex bg-gray-200 rounded-lg p-1">
              <button
                onClick={() => setViewMode("kanban")}
                className={`px-3 py-1 rounded text-sm ${
                  viewMode === "kanban"
                    ? "bg-white shadow font-medium"
                    : "text-gray-600 hover:text-gray-800"
                }`}
              >
                📋 Board
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`px-3 py-1 rounded text-sm ${
                  viewMode === "list"
                    ? "bg-white shadow font-medium"
                    : "text-gray-600 hover:text-gray-800"
                }`}
              >
                📝 List
              </button>
            </div>
          </div>

          {user?.role === "tenant_admin" && (
            <button
              onClick={() => setShowCreateTask(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded"
            >
              + New Task
            </button>
          )}
        </div>

        {tasks.length === 0 ? (
          <div className="bg-white p-6 rounded shadow">
            <p className="text-gray-500">No tasks yet. Create one to get started!</p>
          </div>
        ) : viewMode === "kanban" ? (
          <KanbanBoard
            tasks={tasks}
            onTaskUpdate={fetchProjectData}
            isAdmin={user?.role === "tenant_admin"}
          />
        ) : (
          <div className="bg-white p-6 rounded shadow space-y-3">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="border p-4 rounded flex justify-between items-center"
              >
                <div>
                  <h3 className="font-semibold">{task.title}</h3>
                  <p className="text-sm text-gray-500">Status: {task.status}</p>
                </div>

                {user?.role === "tenant_admin" && (
                  <button
                    onClick={() => setEditTask(task)}
                    className="text-blue-600 hover:underline"
                  >
                    Edit
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Task Modal */}
      {showCreateTask && (
        <CreateTaskModal
          projectId={projectId}
          onClose={() => setShowCreateTask(false)}
          onSuccess={fetchProjectData}
        />
      )}

      {/* Edit Task Modal */}
      {editTask && (
        <EditTaskModal
          task={editTask}
          onClose={() => setEditTask(null)}
          onSuccess={fetchProjectData}
        />
      )}

      {/* Edit Project Modal */}
      {showEditProject && project && (
        <EditProjectModal
          project={project}
          onClose={() => setShowEditProject(false)}
          onSuccess={fetchProjectData}
        />
      )}
    </div>
  );
}

export default ProjectDetails;