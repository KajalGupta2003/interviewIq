import React, { useEffect, useState } from "react";

const History = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem("token");

      const res = await fetch("http://localhost:8000/interview/my", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      const data = await res.json();

      setInterviews(data.data || []);
      setLoading(false);

    } catch (err) {
      console.error("Error fetching history:", err);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center mt-10">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Interview History</h2>

      {interviews.length === 0 ? (
        <p>No interviews found</p>
      ) : (
        <div className="grid gap-4">
          {interviews.map((item, index) => (
            <div
              key={index}
              className="p-4 rounded-xl bg-white/10 backdrop-blur-md border border-white/10"
            >
              <p><strong>Score:</strong> {item.score}</p>

              <p>
                <strong>Date:</strong>{" "}
                {item.created_at
                  ? new Date(item.created_at).toLocaleString()
                  : "N/A"}
              </p>

              {/* Optional extra data */}
              {item.duration && (
                <p><strong>Duration:</strong> {item.duration}s</p>
              )}

              {item.confidence_score && (
                <p><strong>Confidence:</strong> {item.confidence_score}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;