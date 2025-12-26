import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-gray-800 text-white px-6 py-3 flex justify-between items-center">
      <h1 className="font-bold text-lg">MultiTenant SaaS</h1>

      <div className="flex items-center gap-4">
        <Link to="/dashboard" className="hover:underline">
          Dashboard
        </Link>

        <Link to="/projects" className="hover:underline">
          Projects
        </Link>

        {user?.role === "tenant_admin" && (
          <Link to="/users" className="hover:underline">
            Users
          </Link>
        )}

        <span className="text-sm text-gray-300">
          {user?.fullName} ({user?.role})
        </span>

        <button
          onClick={logout}
          className="bg-red-500 px-3 py-1 rounded text-sm"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;