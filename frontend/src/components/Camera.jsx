import { useEffect, useRef } from "react";

function Camera({ isActive, setSessionData }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);

  // 🎯 Capture frame
  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return null;

    const ctx = canvas.getContext("2d");

    // Ensure video is ready
    if (video.videoWidth === 0 || video.videoHeight === 0) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0);

    return canvas.toDataURL("image/jpeg"); // base64
  };

  useEffect(() => {
    let interval = null;

    async function startCamera() {
      if (streamRef.current) return;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });

        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        // Send frames every 2 seconds
        interval = setInterval(() => {
          const frame = captureFrame();
          if (!frame) return;

          fetch(`${import.meta.env.VITE_API_URL}/analyze`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: frame }),
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("Backend:", data);

              //  Store safely
              const newPoint = {
                time: Date.now(),
                eye_contact: data.eye_contact || "Unknown",
                blink: data.blink || false,
              };

              //  Keep only last 100 entries
              setSessionData((prev) => {
                const updated = [...prev, newPoint];
                return updated.slice(-100);
              });
            })
            .catch((err) => console.error("API Error:", err));
        }, 2000);
      } catch (err) {
        console.error("Camera access denied or error:", err);
      }
    }

    function stopCamera() {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }

      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    }

    if (isActive) {
      startCamera();
    } else {
      stopCamera();
    }

    return () => stopCamera();
  }, [isActive, setSessionData]);

  return isActive ? (
    <div className="mt-6 flex flex-col items-center">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-[400px] rounded-xl border border-white/10"
      />

      {/* Hidden canvas for frame capture */}
      <canvas ref={canvasRef} style={{ display: "none" }} />

      <p className="text-xs text-gray-400 mt-2">Camera Active</p>
    </div>
  ) : null;
}

export default Camera;
