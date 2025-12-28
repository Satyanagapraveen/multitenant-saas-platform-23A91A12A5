import { Routes, Route } from "react-router-dom";
import Register from "./auth/Register";
import Login from "./auth/Login";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import ProjectsList from "./pages/projects/ProjectsList";
import AppLayout from "./layouts/AppLayout";
import ProjectDetails from "./pages/projects/ProjectDetails";
import UsersList from "./pages/users/UsersList";
import LandingPage from "./pages/LandingPage";

function App() {
  return (
    <Routes>
  {/* PUBLIC */}
  <Route path="/" element={<LandingPage />} />
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  {/* PROTECTED */}
  <Route
    path="/dashboard"
    element={
      <ProtectedRoute>
        <AppLayout>
          <Dashboard />
        </AppLayout>
      </ProtectedRoute>
    }
  />

  <Route
    path="/projects"
    element={
      <ProtectedRoute>
        <AppLayout>
          <ProjectsList />
        </AppLayout>
      </ProtectedRoute>
    }
  />

  <Route
    path="/projects/:projectId"
    element={
      <ProtectedRoute>
        <AppLayout>
          <ProjectDetails />
        </AppLayout>
      </ProtectedRoute>
    }
  />

  <Route
    path="/users"
    element={
      <ProtectedRoute>
        <AppLayout>
          <UsersList />
        </AppLayout>
      </ProtectedRoute>
    }
  />
</Routes>

  );
}

export default App;