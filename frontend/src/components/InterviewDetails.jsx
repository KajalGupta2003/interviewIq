import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

const InterviewDetails = () => {
  const { id } = useParams();

  const [interview, setInterview] = useState(null);

  useEffect(() => {
    const fetchInterview = async () => {
      try {
        const res = await axios.get(
          `http://localhost:8000/interview/${id}`
        );

        setInterview(res.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchInterview();
  }, [id]);

  if (!interview) {
    return (
      <div className="text-white p-10">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white p-10">
      <h1 className="text-4xl font-bold mb-8">
        Interview Report
      </h1>

      <div className="border border-gray-700 rounded-xl p-6 space-y-3">
        <p><strong>Role:</strong> {interview.role}</p>
        <p><strong>Duration:</strong> {interview.duration} min</p>
        <p><strong>Score:</strong> {interview.score}</p>
        <p><strong>Performance:</strong> {interview.summary.performance}</p>
        {interview.summary.camera && (
  <>
    <h2 className="text-2xl font-bold mt-8 mb-4">
      Camera Analysis
    </h2>

    <div className="border border-gray-700 rounded-xl p-5 space-y-3">
      <p>
        <strong>Total Blinks:</strong>{" "}
        {interview.summary.camera.total_blinks}
      </p>

      <p>
        <strong>Eye Contact:</strong>{" "}
        {interview.summary.camera.eye_contact_percent}%
      </p>

      <p>
        <strong>Confidence:</strong>{" "}
        {interview.summary.camera.confidence}
      </p>
    </div>
  </>
)}
        <p>
          <strong>Total Questions:</strong>{" "}
          {interview.summary.total_questions}
        </p>
        <h2 className="text-2xl font-bold mt-8 mb-4">
          Question-wise Analysis
        </h2>

        <div className="space-y-6">
          {interview.summary.details.map((item, index) => (
            <div
              key={index}
              className="border border-gray-700 rounded-xl p-5"
            >
              <p className="font-semibold">
                Q{index + 1}. {item.question}
              </p>

              <p className="mt-3">
                <strong>Your Answer:</strong>
              </p>

              <p className="text-gray-300">
                {item.answer}
              </p>

              <p className="mt-3">
                <strong>Score:</strong> {item.score}/10
              </p>
              <p className="mt-3">
                <strong>AI Feedback:</strong>
              </p>

              <p className="text-gray-300">
                {item.feedback}
              </p>
              {item.strengths && item.strengths.length > 0 && (
                <>
                  <p className="mt-3">
                    <strong>Strengths:</strong>
                  </p>

                  <ul className="list-disc ml-6 text-green-400">
                    {item.strengths.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </>
              )}

              {item.weaknesses && item.weaknesses.length > 0 && (
                <>
                  <p className="mt-3">
                    <strong>Weaknesses:</strong>
                  </p>

                  <ul className="list-disc ml-6 text-red-400">
                    {item.weaknesses.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </>
              )}

              {item.missed_points && item.missed_points.length > 0 && (
                <>
                  <p className="mt-3">
                    <strong>Missed Points:</strong>
                  </p>

                  <ul className="list-disc ml-6 text-yellow-400">
                    {item.missed_points.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </>
              )}
              {item.ideal_answer && (
                <>
                  <p className="mt-3">
                    <strong>Ideal Answer:</strong>
                  </p>

                  <div className="mt-2 p-4 rounded-lg bg-gray-900 border border-gray-700 text-gray-300 whitespace-pre-wrap">
                    {item.ideal_answer}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default InterviewDetails;