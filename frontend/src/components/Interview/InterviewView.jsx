import Button from "../UI/Button";
import ProgressBar from "../UI/ProgressBar";
import ScoreBadge from "../UI/ScoreBadge";

const InterviewView = ({
  stage,
  question,
  questionNum,
  totalQuestions,
  isSpeaking,
  transcript,
  feedback,
  scores,
  error,
  summary,
  // Actions
  onStopAndSubmit,
  onStartListening,
  onRetry,
  onNext,
  onStopInterview,
}) => {
  // We don't need manual scoreColor logic here anymore because ScoreBadge handles it!

  return (
    <div className="w-full max-w-lg bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
      {/* ── 1. Progress Component ── */}
      <ProgressBar current={questionNum} total={totalQuestions} />

      {/* ── 2. Question Box ── */}
      <div className="bg-black/30 rounded-xl p-5 my-6 border border-white/10 min-h-[80px]">
        {isSpeaking && (
          <div className="flex items-center gap-2 text-indigo-400 text-xs mb-2">
            <span className="animate-pulse">🔊</span> Speaking...
          </div>
        )}
        <p className="text-white leading-relaxed font-medium">
          {question || "Loading question..."}
        </p>
      </div>

      {/* ── 3. Live Transcript ── */}
      {(stage === "listening" ||
        stage === "result" ||
        stage === "evaluating") && (
          <div className="bg-black/20 rounded-xl p-4 mb-5 border border-white/5 min-h-[60px]">
            <p className="text-xs text-gray-500 mb-1">Your answer:</p>
            <p className="text-gray-300 text-sm italic leading-relaxed">
              {transcript || (stage === "listening" ? "Listening..." : "—")}
            </p>
          </div>
        )}

      {/* ── 4. Evaluation Result  ── */}

      {stage === "result" && feedback && (
        <div className="bg-black/30 rounded-xl p-4 mb-5 border border-white/10 animate-in fade-in zoom-in duration-300">

          <div className="flex items-center gap-3 mb-3">
            <ScoreBadge score={feedback.score} />
            <span className="text-sm text-gray-300">
              {feedback.feedback}
            </span>
          </div>

          {/* Strengths */}
          {feedback.strengths?.length > 0 && (
            <div className="mb-3">
              <p className="text-xs text-green-400 font-bold uppercase mb-1">
                Strengths
              </p>

              {feedback.strengths.map((item, i) => (
                <p key={i} className="text-xs text-green-300">
                  • {item}
                </p>
              ))}
            </div>
          )}

          {/* Weaknesses */}
          {feedback.weaknesses?.length > 0 && (
            <div className="mb-3">
              <p className="text-xs text-red-400 font-bold uppercase mb-1">
                Weaknesses
              </p>

              {feedback.weaknesses.map((item, i) => (
                <p key={i} className="text-xs text-red-300">
                  • {item}
                </p>
              ))}
            </div>
          )}

          {/* Missed Points */}
          {feedback.missed_points?.length > 0 && (
            <div className="mb-3">
              <p className="text-xs text-yellow-400 font-bold uppercase mb-1">
                Missed Points
              </p>

              {feedback.missed_points.map((item, i) => (
                <p key={i} className="text-xs text-yellow-300">
                  • {item}
                </p>
              ))}
            </div>
          )}

          {/* Ideal Answer */}
          {feedback.ideal_answer && (
            <div className="border-t border-white/10 pt-3">
              <p className="text-xs text-cyan-400 font-bold uppercase mb-1">
                Ideal Answer
              </p>

              <p className="text-sm text-gray-300 leading-relaxed">
                {feedback.ideal_answer}
              </p>
            </div>
          )}
        </div>
      )}
      {error && (
        <p className="text-red-400 text-sm mb-3 bg-red-400/10 p-2 rounded">
          {error}
        </p>
      )}

      {/* ── 5. Dynamic Action Buttons ── */}
      <div className="flex gap-3 mt-4">
        {(stage === "listening" || (stage === "asking" && error)) && (
          <Button
            variant={transcript.trim() ? "danger" : "ghost"}
            onClick={onStopAndSubmit}
            className="w-full"
          >
            {transcript.trim()
              ? "🎙 Stop & Submit"
              : "No Speech Detected (Cancel)"}
          </Button>
        )}

        {stage === "evaluating" && (
          <Button disabled isLoading={true} className="w-full" />
        )}

        {stage === "result" && (
          <>
            <Button variant="ghost" onClick={onRetry} className="flex-1">
              🔁 Retry
            </Button>
            <Button onClick={onNext} className="flex-1">
              {summary ? "See Summary →" : "Next Question →"}
            </Button>
          </>
        )}

        {stage === "asking" && !isSpeaking && !error && (
          <Button
            variant="success"
            onClick={onStartListening}
            className="w-full"
          >
            🎙 Start Answering
          </Button>
        )}
      </div>
      <div className="mt-5 pt-4 border-t border-white/10">
        <Button
          variant="danger"
          onClick={onStopInterview}
          className="w-full"
        >
          End Interview
        </Button>
      </div>
    </div>
  );
};

export default InterviewView;
