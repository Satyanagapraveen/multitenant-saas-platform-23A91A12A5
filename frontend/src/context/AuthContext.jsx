import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // 🔹 Load from localStorage ONCE
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const storedToken = localStorage.getItem("token");

    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setToken(storedToken);
      api.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
    }

    setLoading(false);
  }, []);

  // 🔹 Login
  const login = (payload) => {
    const cleanUser = {
      id: payload.id,
      email: payload.email,
      fullName: payload.fullName,
      role: payload.role, // 🔥 THIS IS CRITICAL
      tenantId: payload.tenantId,
    };

    setUser(cleanUser);
    setToken(payload.token);

    localStorage.setItem("user", JSON.stringify(cleanUser));
    localStorage.setItem("token", payload.token);

    api.defaults.headers.common["Authorization"] = `Bearer ${payload.token}`;
  };

  // 🔹 Logout
  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    delete api.defaults.headers.common["Authorization"];
    navigate("/login");
  };

  const value = useMemo(
    () => ({ user, token, loading, login, logout }),
    [user, token, loading]
  );

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
