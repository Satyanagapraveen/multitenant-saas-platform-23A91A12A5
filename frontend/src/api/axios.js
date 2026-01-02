import axios from "axios";

// Use environment variable for API URL, fallback to port 5000 (Docker backend)
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 🔐 ALWAYS attach token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
