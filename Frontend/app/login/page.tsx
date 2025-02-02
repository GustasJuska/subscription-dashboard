"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem("accessToken");

  if (!token) {
    console.error("No access token found, redirecting to login.");
    window.location.href = "/login";
    return;
  }

  options.headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
  };

  let res = await fetch(url, options);

  if (res.status === 401) {
    console.log("Access token expired, refreshing...");
    const refreshRes = await fetch("http://localhost:8000/api/auth/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: localStorage.getItem("refreshToken") }),
    });

    if (refreshRes.ok) {
      const data = await refreshRes.json();
      console.log("New access token received:", data.access);
      localStorage.setItem("accessToken", data.access);

      options.headers.Authorization = `Bearer ${data.access}`;
      res = await fetch(url, options);
    } else {
      console.error("Refresh token expired. Logging out...");
      localStorage.clear();
      window.location.href = "/login";
      return;
    }
  }

  return res.json();
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // New loading state
  const router = useRouter();

  const handleLogin = async () => {
    setError("");
    setLoading(true); // Start loading

    try {
      const res = await fetch("http://localhost:8000/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        throw new Error("Invalid email or password");
      }

      const data = await res.json();
      console.log("Login Success:", data);

      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);

      router.push("/dashboard");
    } catch (err) {
      console.error("Login Error:", err);
      setError("Invalid email or password");
    } finally {
      setLoading(false); // End loading
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-80">
        <h2 className="text-2xl font-bold mb-4">Login</h2>
        {error && <p className="text-red-500">{error}</p>}
        <input
          type="email"
          className="border p-2 w-full mb-2"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          className="border p-2 w-full mb-4"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className={`bg-blue-500 text-white p-2 w-full ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </div>
    </div>
  );
}