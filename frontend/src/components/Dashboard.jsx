import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const Dashboard = ({ user }) => {
  const [interviews, setInterviews] = useState([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("latest");

  useEffect(() => {
    const fetchInterviews = async () => {
      if (!user) return;

      try {
        const res = await axios.get(
          `${import.meta.env.VITE_API_URL}/user_interviews/${user.email}`
        );

        setInterviews(res.data.interviews);
      } catch (err) {
        console.error(err);
      }
    };

    fetchInterviews();
  }, [user]);

  const totalInterviews = interviews.length;

  const averageScore =
    totalInterviews > 0
      ? (
        interviews.reduce((sum, item) => sum + item.score, 0) /
        totalInterviews
      ).toFixed(2)
      : 0;

  const bestScore =
    totalInterviews > 0
      ? Math.max(...interviews.map((item) => item.score))
      : 0;

  const lastInterview =
    totalInterviews > 0
      ? interviews[interviews.length - 1]
      : null;

  const chartData = interviews.map((item, index) => ({
    interview: `#${index + 1}`,
    score: item.score,
  }));
  const filteredInterviews = [...interviews]
    .filter((item) =>
      item.role.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "highest") {
        return b.score - a.score;
      }

      if (sortBy === "lowest") {
        return a.score - b.score;
      }

      return (
        new Date(b.completedAt) -
        new Date(a.completedAt)
      );
    });

  return (
    <div className="min-h-screen bg-[#050505] text-white p-10">
      <h1 className="text-4xl font-bold mb-8">
        Welcome, {user?.displayName}
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400">Total Interviews</p>
          <h2 className="text-3xl font-bold mt-2">
            {totalInterviews}
          </h2>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400">Average Score</p>
          <h2 className="text-3xl font-bold mt-2 text-indigo-400">
            {averageScore}
          </h2>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400">Best Score</p>
          <h2 className="text-3xl font-bold mt-2 text-green-400">
            {bestScore}
          </h2>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400">Last Interview</p>

          {lastInterview ? (
            <>
              <h2 className="text-xl font-bold mt-2">
                {lastInterview.role}
              </h2>

              <p className="text-gray-400">
                {lastInterview.score}/10
              </p>
            </>
          ) : (
            <p>No Interview</p>
          )}
        </div>

      </div>


      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 mb-10">
        <h2 className="text-2xl font-bold mb-6">
          Performance Trend
        </h2>

        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="interview" stroke="#ccc" />
              <YAxis stroke="#ccc" domain={[0, 10]} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#6366f1"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mb-6">

        <input
          type="text"
          placeholder="Search by role..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 flex-1"
        />

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2"
        >
          <option value="latest">Latest</option>
          <option value="highest">Highest Score</option>
          <option value="lowest">Lowest Score</option>
        </select>

      </div>
      <h2 className="text-2xl mb-4">Interview History</h2>

      {interviews.length === 0 ? (
        <p>No interviews found.</p>
      ) : (
        <div className="space-y-4">
          {filteredInterviews.map((item, index) => (
            <div
              key={index}
              className="border border-gray-700 rounded-xl p-5"
            >
              <p><strong>Role:</strong> {item.role}</p>
              <p><strong>Duration:</strong> {item.duration} min</p>
              <p><strong>Score:</strong> {item.score}</p>
              <p><strong>Performance:</strong> {item.summary.performance}</p>
              <Link
                to={`/interview/${item._id}`}
                className="inline-block mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg transition"
              >
                View Details
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;