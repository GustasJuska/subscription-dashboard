"use client";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function Checkout() {
  const searchParams = useSearchParams();
  const plan = searchParams.get("plan") || "free";
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 🔄 Function to Refresh Token
  const refreshToken = async () => {
    const storedRefreshToken = localStorage.getItem("refreshToken");

    if (!storedRefreshToken) {
      console.error("No refresh token available. Redirecting to login.");
      logoutUser();
      return null;
    }

    try {
      const res = await fetch("http://localhost:8000/api/auth/refresh/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: storedRefreshToken }),
      });

      if (!res.ok) throw new Error("Failed to refresh token. Redirecting to login.");

      const data = await res.json();
      localStorage.setItem("accessToken", data.access);
      return data.access; // ✅ Return refreshed token
    } catch (error) {
      console.error("Token refresh failed:", error);
      logoutUser();
      return null;
    }
  };

  // 🔄 Function to Logout User
  const logoutUser = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    window.location.href = "/login"; // Redirect to login
  };

  // 🚀 Handle Checkout Process
  const handleCheckout = async () => {
    setLoading(true);
    setError("");

    let token = localStorage.getItem("accessToken");

    if (!token) {
      token = await refreshToken();
      if (!token) return;
    }

    try {
      const res = await fetch("http://localhost:8000/api/auth/subscribe/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`, // ✅ Always send valid token
        },
        body: JSON.stringify({ plan }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Something went wrong");
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url; // ✅ Redirect to Stripe Checkout
      } else {
        alert("Subscription activated successfully!");
        window.location.href = "/dashboard"; // ✅ Redirect after free plan activation
      }
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

  // ✅ Trigger Checkout Automatically on Load
  useEffect(() => {
    handleCheckout();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        {loading ? "Redirecting to Payment..." : "Checkout"}
      </h2>
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  );
}
