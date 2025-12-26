 import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  if (loading) return null; // or spinner
  return token ? children : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
