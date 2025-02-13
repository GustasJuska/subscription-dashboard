"use client";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  const handleSelectPlan = (plan: string) => {
    router.push(`/register?plan=${plan}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
      {/* Title */}
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
        Choose the best plan for your SaaS business
      </h1>
      <p className="text-lg text-gray-700 mb-8">
        Get insights, manage finances, and scale with ease.
      </p>

      <div className="flex gap-6">
        {/* Basic Plan */}
        <div className="bg-white p-6 rounded-lg shadow-md w-80 border border-gray-200 transition duration-300 hover:shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-900">Basic</h2>
          <p className="text-4xl font-bold text-gray-900">£0.00</p>
          <p className="text-gray-700">No monthly fees</p>
          <ul className="mt-4 text-base text-gray-700">
            <li>✔ Access to basic analytics dashboard</li>
            <li>✔ Track up to 10 transactions</li>
            <li>✔ Generate simple financial reports</li>
            <li>✔ Community support</li>
          </ul>
          <button 
            onClick={() => handleSelectPlan("basic")} 
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded w-full font-semibold">
            Get started
          </button>
        </div>

        {/* Pro Plan */}
        <div className="bg-white p-6 rounded-lg shadow-md w-80 border border-gray-200 transition duration-300 hover:shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-900">Pro</h2>
          <p className="text-4xl font-bold text-gray-900">£9.99</p>
          <p className="text-gray-700">Per month</p>
          <ul className="mt-4 text-base text-gray-700">
            <li>✔ Unlimited transactions</li>
            <li>✔ Generate standard reports</li>
            <li>✔ Connect multiple bank accounts</li>
            <li>✔ Email notifications for financial insights</li>
          </ul>
          <button 
            onClick={() => handleSelectPlan("pro")} 
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded w-full font-semibold">
            Try for free
          </button>
        </div>

        {/* Enterprise Plan */}
        <div className="bg-white p-6 rounded-lg shadow-md w-80 border border-gray-200 transition duration-300 hover:shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-900">Enterprise</h2>
          <p className="text-4xl font-bold text-gray-900">£29.99</p>
          <p className="text-gray-700">Per month</p>
          <ul className="mt-4 text-base text-gray-700">
            <li>✔ Advanced analytics dashboard</li>
            <li>✔ AI-powered financial forecasting</li>
            <li>✔ Custom reports & tax preparation</li>
            <li>✔ Priority support & dedicated account manager</li>
          </ul>
          <button 
            onClick={() => handleSelectPlan("enterprise")} 
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded w-full font-semibold">
            Try for free
          </button>
        </div>
      </div>
    </div>
  );
}
