"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem("accessToken");

  if (!token) {
      console.error("No access token found, redirecting to login.");
      window.location.href = "/login"; // Redirect if no token
      return;
  }

  // Set Authorization header
  options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
  };

  let res = await fetch(url, options);

  // If access token expired (401), try refreshing it
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

          // Retry the original request with the new token
          options.headers.Authorization = `Bearer ${data.access}`;
          res = await fetch(url, options);
      } else {
          console.error("Refresh token expired. Logging out...");
          localStorage.clear();
          window.location.href = "/login"; // Redirect to login
          return;
      }
  }

  return res.json();
}

export default function Dashboard() {
  const [userData, setUserData] = useState(null);
  const router = useRouter();

  useEffect(() => {
      const token = localStorage.getItem("accessToken");

      if (!token) {
          router.push("/login"); // Redirect if not logged in
      } else {
          fetchWithAuth("http://localhost:8000/api/auth/protected/")
              .then((data) => setUserData(data))
              .catch((err) => console.error("Error fetching protected data:", err));
      }
  }, []);

  return (
      <div className="p-6">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          {userData ? <p>Welcome, {userData.message}</p> : <p>Loading...</p>}
      </div>
  );
}