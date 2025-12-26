import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/axios";
import { useAuth } from "../../context/AuthContext";
import CreateProjectModal from "./CreateProjectModal";
import EditProjectModal from "./EditProjectModal";

function ProjectsList() {
  const { user } = useAuth();
  const isAdmin = user?.role === "tenant_admin";

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editProject, setEditProject] = useState(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects");
      setProjects(res.data.data.projects || []);
    } catch (err) {
      console.error("Failed to load projects", err);
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (id) => {
    if (!window.confirm("Delete this project?")) return;
    await api.delete(`/projects/${id}`);
    fetchProjects();
  };

  if (loading) return <p className="p-6">Loading projects...</p>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Projects</h2>

        {isAdmin && (
          <button
            onClick={() => setShowCreate(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            + New Project
          </button>
        )}
      </div>

      {projects.length === 0 ? (
        <p>No projects found.</p>
      ) : (
        <div className="grid gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white p-4 rounded shadow flex justify-between items-center"
            >
              <Link to={`/projects/${project.id}`} className="flex-1">
                <h3 className="font-semibold hover:text-blue-600">{project.name}</h3>
                <p className="text-sm text-gray-500">{project.description}</p>
                <span className="text-xs text-gray-400">
                  Status: {project.status}
                </span>
              </Link>

              <div className="flex gap-3 ml-4">
                <Link
                  to={`/projects/${project.id}`}
                  className="text-green-600 hover:underline"
                >
                  View
                </Link>

                {isAdmin && (
                  <>
                    <button
                      onClick={() => setEditProject(project)}
                      className="text-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteProject(project.id)}
                      className="text-red-600"
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateProjectModal
          onClose={() => setShowCreate(false)}
          onSuccess={fetchProjects}
        />
      )}

      {editProject && (
        <EditProjectModal
          project={editProject}
          onClose={() => setEditProject(null)}
          onSuccess={fetchProjects}
        />
      )}
    </div>
  );
}

export default ProjectsList;
