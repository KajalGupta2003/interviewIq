import Navbar from "./components/Navbar";
import Card from "./components/Card";
import { useState, useEffect } from "react";
import { auth } from "./firebase";
import { onAuthStateChanged } from "firebase/auth";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import InterviewDetails from "./components/InterviewDetails";
import ProtectedRoute from "./components/ProtectedRoute";
function App() {

  const [user, setUser] = useState(null);

useEffect(() => {
  const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
    setUser(currentUser);
  });

  return () => unsubscribe();
}, []);
  return (
    <div className="min-h-screen bg-[#050505] text-white selection:bg-indigo-500/30">
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
      </div>

      <Navbar user={user} setUser={setUser} />
      <Routes>
        <Route
           path="/"
           element={
      <main className="flex flex-col items-center justify-center pt-32 pb-20 px-6">
        <div className="max-w-4xl w-full text-center mb-12">
          <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-[1.1] mb-6">
            Practice <span className="text-indigo-500">Smart.</span>
            <br />
            Interview <span className="text-indigo-500">Confident.</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            The AI-powered mock interview platform designed to get you hired.
          </p>
        </div>
        <Card user={user} />
      </main>
           }
           />
            <Route
        path="/dashboard"
        element={<ProtectedRoute user={user}>
      <Dashboard user={user} />
    </ProtectedRoute>}
      />
            <Route
              path="/interview/:id"
              element={<InterviewDetails />}
            />
    </Routes>
    </div>
  );
}

export default App;
