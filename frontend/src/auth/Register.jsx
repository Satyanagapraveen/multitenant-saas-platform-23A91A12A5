import { useForm } from "react-hook-form";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Register() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");

  const onSubmit = async (data) => {
    if (data.password !== data.confirmPassword) {
      setApiError("Passwords do not match");
      return;
    }

    setApiError("");
    setSuccess("");
    setLoading(true);

    try {
      await api.post("/auth/register-tenant", {
        tenantName: data.tenantName,
        subdomain: data.subdomain,
        adminEmail: data.adminEmail,
        adminFullName: data.adminFullName,
        adminPassword: data.password,
      });

      setSuccess("Registration successful. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setApiError(
        err.response?.data?.message ||
          "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6">
          Register Organization
        </h2>

        {apiError && (
          <div className="bg-red-100 text-red-700 p-2 rounded mb-4">
            {apiError}
          </div>
        )}

        {success && (
          <div className="bg-green-100 text-green-700 p-2 rounded mb-4">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <input
            {...register("tenantName", { required: true })}
            placeholder="Organization Name"
            className="w-full border p-2 rounded"
          />
          {errors.tenantName && (
            <p className="text-sm text-red-500">Organization name is required</p>
          )}

          <div>
            <input
              {...register("subdomain", { required: true })}
              placeholder="Subdomain"
              className="w-full border p-2 rounded"
            />
            <p className="text-xs text-gray-500 mt-1">
              your-org.yourapp.com
            </p>
          </div>

          <input
            {...register("adminFullName", { required: true })}
            placeholder="Admin Full Name"
            className="w-full border p-2 rounded"
          />
          {errors.adminFullName && (
            <p className="text-sm text-red-500">Admin name is required</p>
          )}

          <input
            type="email"
            {...register("adminEmail", { required: true })}
            placeholder="Admin Email"
            className="w-full border p-2 rounded"
          />
          {errors.adminEmail && (
            <p className="text-sm text-red-500">Email is required</p>
          )}

          <input
            type="password"
            {...register("password", { required: true, minLength: 8 })}
            placeholder="Password"
            className="w-full border p-2 rounded"
          />
          {errors.password && (
            <p className="text-sm text-red-500">
              Password must be at least 8 characters
            </p>
          )}

          <input
            type="password"
            {...register("confirmPassword", { required: true })}
            placeholder="Confirm Password"
            className="w-full border p-2 rounded"
          />

          <div className="flex items-center gap-2">
            <input type="checkbox" required />
            <span className="text-sm">
              I agree to Terms & Conditions
            </span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="text-center mt-4 text-sm">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;
