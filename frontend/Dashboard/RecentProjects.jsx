import { Link } from "react-router-dom";

function RecentProjects({ projects, isAdmin }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold">Recent Projects</h3>
        {isAdmin && (
          <Link
            to="/projects"
            className="text-blue-600 text-sm hover:underline"
          >
            View All / Manage
          </Link>
        )}
      </div>

      {projects.length === 0 ? (
        <p className="text-gray-500">No projects found.</p>
      ) : (
        <ul className="space-y-2">
          {projects.map((project) => (
            <li
              key={project.id}
              className="flex justify-between items-center border-b pb-2"
            >
              <div>
                <span className="font-medium">{project.name}</span>
                <p className="text-xs text-gray-400">{project.description}</p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  project.status === "completed"
                    ? "bg-green-100 text-green-700"
                    : project.status === "in_progress"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {project.status}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default RecentProjects;