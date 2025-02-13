"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Function to fetch protected data
async function fetchWithAuth(url: string, options: RequestInit = {}) {
  let token = localStorage.getItem("accessToken");

  if (!token) {
    console.error("No access token found, redirecting to login.");
    window.location.href = "/login";
    return;
  }

  let headers: Record<string, string> = options.headers
    ? { ...(options.headers as Record<string, string>) }
    : {};

  headers["Authorization"] = `Bearer ${token}`;
  options.headers = headers;

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

      headers["Authorization"] = `Bearer ${data.access}`;
      options.headers = headers;
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

export default function Dashboard() {
  const [userData, setUserData] = useState(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [subscription, setSubscription] = useState<{ plan: string, is_active?: boolean } | null>(null);
  const router = useRouter();

  // Define Transaction type
  type Transaction = {
    type: "sale" | "expense" | "revenue";
    amount: number;
    date?: string;
  };

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      router.push("/login"); // Redirect if not logged in
    } else {
      fetchWithAuth("http://localhost:8000/api/auth/api/protected/")
        .then((data) => setUserData(data))
        .catch((err) => console.error("Error fetching user data:", err));

      fetchWithAuth("http://localhost:8000/api/auth/transactions/")
        .then((data) => setTransactions(data))
        .catch((err) => console.error("Error fetching transactions:", err));

      fetchWithAuth("http://localhost:8000/api/auth/subscriptions/")
        .then((data) => setSubscription(
          data.subscriptions && data.subscriptions.length > 0 ? data.subscriptions[0] : null
        ))
        .catch((err) => console.error("Error fetching subscription:", err));
    }
  }, []);

  const handleUpgrade = async (newPriceId: string) => {
    try {
      const res = await fetchWithAuth("http://localhost:8000/api/auth/upgrade/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ price_id: newPriceId }),
      });

      // Assuming the backend now returns the new plan name in "plan"
      const data = res;
      alert(`Subscription upgraded to ${data.plan} successfully!`);
      setSubscription({ ...subscription, plan: data.plan });
    } catch (error) {
      console.error("Upgrade Error:", error);
    }
  };

  const handleCancel = async () => {
    try {
      const res = await fetchWithAuth("http://localhost:8000/api/auth/cancel/", {
        method: "POST",
      });

      const data = res;
      if (data.message) {
        alert("Subscription canceled.");
        setSubscription(null);
      } else {
        alert(data.error);
      }
    } catch (error) {
      console.error("Cancel Error:", error);
    }
  };

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-extrabold text-gray-900">Dashboard</h1>
      {subscription ? (
        <div>
          {/* Display the subscription plan directly */}
          <p><strong>Plan:</strong> {subscription.plan || "Unknown Plan"}</p>
          <p><strong>Status:</strong> {subscription.is_active ? "Active ✅" : "Inactive ❌"}</p>
          {/* Pass a valid Stripe price id to the upgrade handler */}
          <button onClick={() => handleUpgrade("price_1Qndfv2cwYcZLwewDpwXyzAbc")} className="btn btn-primary">
            Upgrade
          </button>
          <button onClick={handleCancel} className="btn btn-danger ml-4">
            Cancel
          </button>
        </div>
      ) : (
        <p>No active subscription.</p>
      )}
    </div>
  );
}
