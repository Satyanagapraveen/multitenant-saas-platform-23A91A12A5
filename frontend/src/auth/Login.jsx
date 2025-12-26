import { useForm } from "react-hook-form";
import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

function Login() {
  const { register, handleSubmit } = useForm();
  const navigate = useNavigate();
  const { login, token, loading: authLoading } = useAuth();

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Redirect if already logged in
  useEffect(() => {
    if (!authLoading && token) {
      navigate("/dashboard", { replace: true });
    }
  }, [token, authLoading, navigate]);

  const onSubmit = async (data) => {
    setLoading(true);
    setErrorMsg("");

    try {
      const res = await api.post("/auth/login", {
        email: data.email,
        password: data.password,
        tenantSubdomain: data.tenantSubdomain,
      });

      login(res.data.data);
      navigate("/dashboard");
    } catch (err) {
      setErrorMsg(err.response?.data?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  // Don't render login form if already logged in
  if (token) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="bg-white p-8 rounded shadow-md w-full max-w-md"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>

        {errorMsg && (
          <p className="bg-red-100 text-red-700 p-2 mb-3 rounded">
            {errorMsg}
          </p>
        )}

        <input
          {...register("email", { required: true })}
          placeholder="Email"
          type="email"
          className="input"
        />

        <input
          {...register("password", { required: true })}
          placeholder="Password"
          type="password"
          className="input mt-3"
        />

        <input
          {...register("tenantSubdomain", { required: true })}
          placeholder="Tenant Subdomain"
          className="input mt-3"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 mt-4 rounded hover:bg-blue-700"
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="text-center mt-4 text-sm">
          Don't have an account?{" "}
          <Link to="/register" className="text-blue-600 underline">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}

export default Login;
