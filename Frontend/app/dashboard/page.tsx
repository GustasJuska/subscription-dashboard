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

export default function Dashboard() {
  const [userData, setUserData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const router = useRouter();

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

      fetchWithAuth("http://localhost:8000/api/auth/subscribe/")
        .then((data) => setSubscription(data))
        .catch((err) => console.error("Error fetching subscription:", err));
    }
  }, []);

  // Dummy chart data
  const chartData = {
    labels: ["Sales", "Expenses", "Revenue"],
    datasets: [
      {
        label: "Financial Overview",
        data: [
          transactions.reduce((acc, t) => (t.type === "sale" ? acc + t.amount : acc), 0),
          transactions.reduce((acc, t) => (t.type === "expense" ? acc + t.amount : acc), 0),
          transactions.reduce((acc, t) => (t.type === "revenue" ? acc + t.amount : acc), 0),
        ],
        backgroundColor: ["#36A2EB", "#FF6384", "#4BC0C0"],
      },
    ],
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      {userData ? <p>Welcome, {userData.username}</p> : <p>Loading...</p>}

      <div className="mt-6 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-xl font-bold mb-2">Financial Overview</h2>
        <Bar data={chartData} />
      </div>

      <div className="mt-6 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-xl font-bold mb-2">Transaction History</h2>
        <table className="w-full border-collapse border border-gray-200">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">Date</th>
              <th className="border p-2">Type</th>
              <th className="border p-2">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length > 0 ? (
              transactions.map((transaction, index) => (
                <tr key={index} className="border">
                  <td className="p-2">{transaction.date}</td>
                  <td className="p-2">{transaction.type}</td>
                  <td className="p-2">${transaction.amount}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3" className="p-2 text-center">No transactions found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-6 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-xl font-bold mb-2">Subscription Status</h2>
        {subscription ? (
          <p>Plan: {subscription.plan} - Status: {subscription.isActive ? "Active" : "Inactive"}</p>
        ) : (
          <p>Loading subscription info...</p>
        )}
      </div>

      <div className="mt-6 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-xl font-bold mb-2">AI Insights</h2>
        <p>🚀 AI-powered financial insights will be added here soon!</p>
      </div>
    </div>
  );
}
