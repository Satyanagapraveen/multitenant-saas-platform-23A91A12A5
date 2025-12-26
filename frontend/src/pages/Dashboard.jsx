import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";
import StatsCards from "../../Dashboard/StatsCards";
import RecentProjects from "../../Dashboard/RecentProjects";
import MyTasks from "../../Dashboard/MyTasks";

function Dashboard() {
  const { user, loading } = useAuth();
  const isAdmin = user?.role === "tenant_admin";

  const [stats, setStats] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [pageLoading, setPageLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const [projectsRes, tasksRes] = await Promise.all([
        api.get("/projects"),
        api.get("/tasks"), // Backend auto-filters by logged-in user
      ]);

      const projectsData = projectsRes.data?.data?.projects || [];
      const tasksData = tasksRes.data?.data || [];

      setProjects(projectsData.slice(0, 5));
      setTasks(tasksData);

      setStats({
        totalProjects: projectsData.length,
        totalTasks: tasksData.length,
        completedTasks: tasksData.filter(
          (t) => t.status === "completed"
        ).length,
        pendingTasks: tasksData.filter(
          (t) => t.status !== "completed"
        ).length,
      });
    } catch (err) {
      console.error("Dashboard load failed", err);
    } finally {
      setPageLoading(false);
    }
  };

  useEffect(() => {
    if (loading || !user) return;
    fetchDashboardData();
  }, [loading, user]);

  if (loading || pageLoading) {
    return <p className="p-6">Loading dashboard...</p>;
  }

  return (
    <div className="space-y-6">
      {/* Header with Admin Button */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        {isAdmin && (
          <Link
            to="/projects"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + Manage Projects
          </Link>
        )}
      </div>

      <StatsCards stats={stats} />
      <RecentProjects projects={projects} isAdmin={isAdmin} />
      <MyTasks tasks={tasks} onStatusChange={fetchDashboardData} />
    </div>
  );
}

export default Dashboard;