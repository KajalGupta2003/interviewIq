import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const Dashboard = ({ user }) => {
  const [interviews, setInterviews] = useState([]);

  useEffect(() => {
    const fetchInterviews = async () => {
      if (!user) return;

      try {
        const res = await axios.get(
          `http://localhost:8000/user_interviews/${user.email}`
        );

        setInterviews(res.data.interviews);
      } catch (err) {
        console.error(err);
      }
    };

    fetchInterviews();
  }, [user]);

  return (
    <div className="min-h-screen bg-[#050505] text-white p-10">
      <h1 className="text-4xl font-bold mb-8">
        Welcome, {user?.displayName}
      </h1>

      <h2 className="text-2xl mb-4">Interview History</h2>

      {interviews.length === 0 ? (
        <p>No interviews found.</p>
      ) : (
        <div className="space-y-4">
          {interviews.map((item, index) => (
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