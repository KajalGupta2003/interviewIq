import { useState, useRef, useEffect } from "react";
import axios from "axios";

export const STAGE = {
  SETUP: "setup",
  ASKING: "asking",
  LISTENING: "listening",
  EVALUATING: "evaluating",
  RESULT: "result",
  FINISHED: "finished",
};

export const useInterview = () => {
  const [stage, setStage] = useState(STAGE.SETUP);
  const [sessionId, setSessionId] = useState(null);
  const [data, setData] = useState({
    question: "",
    questionNum: 1,
    totalQuestions: 0,
    transcript: "",
    feedback: null,
    scores: [],
    summary: null,
    isSpeaking: false,
    error: "",
    answered: [],
  });

  const recognitionRef = useRef(null);
  const transcriptRef = useRef("");
  const audioRef = useRef(null);
  const currentQuestionRef = useRef(""); // Fix: avoid stale closure in submitAnswer

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      if (recognitionRef.current) recognitionRef.current.abort();
      if (audioRef.current) audioRef.current.pause();
    };
  }, []);

  // ── 1. Audio Logic (ElevenLabs via Backend, with Browser TTS fallback) ──
  const playAudio = async (text, onEnd) => {
    try {
      if (audioRef.current) audioRef.current.pause();

      const response = await fetch("http://localhost:8000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error("Voice generation failed");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        URL.revokeObjectURL(url); // Fix: free memory after playback
        setData((prev) => ({ ...prev, isSpeaking: false }));
        if (onEnd) onEnd();
      };

      await audio.play();
    } catch (err) {
      console.error("ElevenLabs failed, falling back to Browser TTS", err);
      const utter = new SpeechSynthesisUtterance(text);
      utter.onend = () => {
        setData((prev) => ({ ...prev, isSpeaking: false })); // Fix: reset isSpeaking on fallback too
        if (onEnd) onEnd();
      };
      window.speechSynthesis.speak(utter);
    }
  };

  // ── 2. Interview Actions ──
  const startInterview = async (formData) => {
    setData((prev) => ({ ...prev, error: "" }));
    try {
      const res = await axios.post(
        "http://localhost:8000/start_interview",
        formData,
      );
      setSessionId(res.data.session_id);

      // Guard: check first_question exists before proceeding
      if (!res.data.first_question) {
        setData((prev) => ({
          ...prev,
          error: "Could not generate questions. Please try again.",
        }));
        setStage(STAGE.SETUP);
        return;
      }

      setData((prev) => ({
        ...prev,
        totalQuestions: res.data.total_questions,
      }));
      askQuestion(res.data.first_question, 1);
    } catch (err) {
      const msg = err.response?.data?.detail || "Backend connection failed.";
      setData((prev) => ({ ...prev, error: msg }));
      setStage(STAGE.SETUP);
    }
  };

  const askQuestion = (q, num) => {
    currentQuestionRef.current = q; // Fix: keep question in ref for submitAnswer
    setStage(STAGE.ASKING);
    setData((prev) => ({
      ...prev,
      question: q,
      questionNum: num,
      transcript: "",
      feedback: null,
      isSpeaking: true,
      error: "",
    }));
    transcriptRef.current = "";

    playAudio(q, () => {
      startListening();
    });
  };

  const startListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {}
    }

    setStage(STAGE.LISTENING);
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setData((prev) => ({
        ...prev,
        error: "Speech recognition not supported.",
      }));
      return;
    }

    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = true;

    rec.onresult = (e) => {
      let full = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join("");
      setData((prev) => ({ ...prev, transcript: full, error: "" }));
      transcriptRef.current = full;
    };

    recognitionRef.current = rec;
    rec.start();
  };

  const submitAnswer = async () => {
    if (recognitionRef.current) recognitionRef.current.stop();

    const answer = transcriptRef.current.trim();

    if (!answer) {
      setData((prev) => ({
        ...prev,
        error: "I didn't catch that. Please try speaking again!",
      }));
      // setStage(STAGE.ASKING);
      startListening();
      return;
    }

    setStage(STAGE.EVALUATING);
    try {
      const res = await axios.post("http://localhost:8000/submit_answer", {
        session_id:sessionId,
        question: currentQuestionRef.current,
        answer,
      });
      console.log(res.data);

      setData((prev) => ({
        ...prev,
        feedback: res.data.score,
        scores: [...prev.scores, res.data.score.score],
        summary: res.data.summary || prev.summary,
        nextQuestion: res.data.next_question || null, // ✅ store it
        answered: [
          ...(prev.answered || []),
          {
            question: currentQuestionRef.current,
            answer,
            score: res.data.score.score,
            feedback: res.data.score.feedback,
            strengths: res.data.score.strengths || [],
            weaknesses: res.data.score.weaknesses || [],
            missed_points: res.data.score.missed_points || [],
            ideal_answer: res.data.score.ideal_answer || "",
          },
        ],
      }));

      setStage(STAGE.RESULT);
    } catch (err) {
      setData((prev) => ({
        ...prev,
        error: "Evaluation failed. Please try again.",
      }));
      setStage(STAGE.LISTENING);
    }
  };

  return {
    stage,
    setStage,
    data,
    setData,
    startInterview,
    submitAnswer,
    askQuestion,
    startListening,
  };
};
