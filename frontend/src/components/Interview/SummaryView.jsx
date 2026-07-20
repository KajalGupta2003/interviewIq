import Button from "../UI/Button";
import ScoreBadge from "../UI/ScoreBadge";

const SummaryView = ({ summary, user }) => {
  const avg = summary.average_score;
  const cam = summary.camera;
  return (
    <div className="w-full max-w-lg bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
      <h2 className="text-2xl font-bold text-center text-white mb-2">
        Interview Complete 🎉
      </h2>
      <p className="text-center text-gray-400 mb-6 text-sm">
        Here's your performance analysis
      </p>

      {/* ── 1. Big Score Hero Section ── */}
      <div className="flex justify-center mb-10">
        <div className="text-center group">
          <div className="relative inline-block">
            {/* Large Score Display using ScoreBadge logic but custom sizing */}
            <p
              className={`text-8xl font-black tracking-tighter transition-transform group-hover:scale-110 duration-500 
               ${avg >= 8 ? "text-green-400" : avg >= 5 ? "text-yellow-400" : "text-red-400"}`}
            >
              {avg}
            </p>
            <div className="absolute -inset-2 bg-indigo-500/10 blur-2xl rounded-full -z-10" />
          </div>
          <p className="text-gray-500 text-[10px] uppercase tracking-[0.2em] mt-2 font-bold">
            Average Score / 10
          </p>
          <p
            className={`mt-3 inline-block px-4 py-1 rounded-full text-xs font-bold uppercase border
            ${avg >= 8
                ? "bg-green-400/10 border-green-400/20 text-green-400"
                : avg >= 5
                  ? "bg-yellow-400/10 border-yellow-400/20 text-yellow-400"
                  : "bg-red-400/10 border-red-500/20 text-red-400"
              }`}
          >
            {summary.performance}
          </p>
        </div>
      </div>
      {cam && (
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-black/40 rounded-xl p-4 border border-white/5 text-center">
            <p className="text-[9px] text-gray-500 uppercase font-black mb-1">
              Confidence
            </p>
            <p
              className={`text-lg font-bold
              ${cam.confidence === "High"
                  ? "text-green-400"
                  : cam.confidence === "Medium"
                    ? "text-yellow-400"
                    : "text-red-400"
                }`}
            >
              {cam.confidence}
            </p>
          </div>
          <div className="bg-black/40 rounded-xl p-4 border border-white/5 text-center">
            <p className="text-[9px] text-gray-500 uppercase font-black mb-1">
              Eye Contact
            </p>
            <p
              className={`text-lg font-bold
              ${cam.eye_contact_percent >= 70
                  ? "text-green-400"
                  : cam.eye_contact_percent >= 40
                    ? "text-yellow-400"
                    : "text-red-400"
                }`}
            >
              {cam.eye_contact_percent}%
            </p>
          </div>

          <div className="bg-black/40 rounded-xl p-4 border border-white/5 text-center">
            <p className="text-[9px] text-gray-500 uppercase font-black mb-1">
              Blinks
            </p>
            <p className="text-lg font-bold text-blue-400">
              {cam.total_blinks}
            </p>
          </div>
        </div>
      )}
      {/* ── 2. Detailed Breakdown ── */}
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
        {summary.details.map((d, i) => (
          <div
            key={i}
            className="bg-black/40 rounded-xl p-5 border border-white/5 hover:border-indigo-500/30 transition-all duration-300 group"
          >
            <div className="flex justify-between items-center mb-4">
              <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">
                Question {i + 1}
              </span>
              <ScoreBadge score={d.score} />
            </div>

            <p className="text-sm text-gray-200 mb-4 font-medium leading-relaxed">
              {d.question}
            </p>

            <div className="space-y-3">
              {/* User Answer Block */}
              <div className="bg-white/5 rounded-lg p-3 border-l-2 border-indigo-500">
                <p className="text-[9px] text-gray-500 uppercase font-black mb-1">
                  Your Response
                </p>
                <p className="text-xs text-gray-300 italic leading-relaxed">
                  "{d.answer}"
                </p>
              </div>

              {/* Feedback Block */}
              <div className="bg-indigo-500/5 rounded-lg p-3 border border-white/5">
                <p className="text-[9px] text-indigo-400 uppercase font-black mb-1">
                  Analysis
                </p>
                <p className="text-xs text-gray-300 leading-relaxed">
                  {d.feedback}
                </p>
              </div>
            </div>

            {/* Missed Points Section */}
            {d.missed_points?.length > 0 && (
              <div className="mt-4 pt-3 border-t border-white/5">
                <p className="text-[9px] text-red-400 font-black mb-2 uppercase tracking-tighter">
                  Improvement Areas:
                </p>
                <div className="space-y-1.5">
                  {d.missed_points.map((mp, j) => (
                    <div
                      key={j}
                      className="flex items-start gap-2 text-[11px] text-gray-400"
                    >
                      <span className="text-red-500 mt-0.5">•</span>
                      <span className="leading-snug">{mp}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      {user ? (
        <div className="mt-6 p-4 rounded-xl bg-green-500/10 border border-green-500/20">
          <p className="text-green-400 text-sm text-center font-medium">
            ✅ Interview saved successfully. You can view it anytime from your Dashboard.
          </p>
        </div>
      ) : (
        <div className="mt-6 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-yellow-400 text-sm text-center font-medium">
            ⚠️ This interview was not saved because you're using Guest Mode.
            <br />
            Login with Google to save future interviews and access them from your Dashboard.
          </p>
        </div>
      )}
      {/* ── 3. Restart Button using Atomic Button ── */}
      <Button
        onClick={() => window.location.reload()}
        variant="primary"
        className="w-full mt-8 py-4 text-sm"
      >
        New Practice Session 🔄
      </Button>
    </div>
  );
};

export default SummaryView;
