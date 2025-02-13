"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function Register() {
  const [username, setUsername] = useState(""); // ✅ Added username field
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState("free");
  
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const selectedPlan = searchParams.get("plan");
    if (selectedPlan) setPlan(selectedPlan);
  }, [searchParams]);

  const handleRegister = async () => {
    setError("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/auth/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }), // ✅ Added username in request
      });

      const data = await res.json();

      if (res.ok) {
          // ✅ Store tokens in localStorage after registration
          localStorage.setItem("accessToken", data.access);
          localStorage.setItem("refreshToken", data.refresh);
      } else {
          throw new Error(data.error || "Registration failed.");
      }

      // Redirect to checkout page
      router.push(`/checkout?plan=${plan}`);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
      <div className="bg-white p-8 rounded-lg shadow-md w-96 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Sign Up</h2>
        <p className="text-sm text-gray-600 mb-6">Register to continue with the {plan} plan.</p>
        
        {error && <p className="text-red-500 text-sm">{error}</p>}

        <input
          type="text"
          placeholder="Username"
          className="border p-2 w-full mb-2 rounded"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="email"
          placeholder="Email"
          className="border p-2 w-full mb-2 rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="border p-2 w-full mb-4 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          onClick={handleRegister}
          className={`bg-blue-600 text-white px-4 py-2 rounded w-full font-semibold ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          disabled={loading}
        >
          {loading ? "Registering..." : "Register"}
        </button>
      </div>
    </div>
  );
}
