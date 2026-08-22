import React, { useState, useEffect } from "react";
import { GoogleLogin, googleLogout } from "@react-oauth/google";
import axios from "axios";

const Navbar = () => {
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);

  // ✅ Load user from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Handle Google Login
  const handleSuccess = async (credentialResponse) => {
  const token = credentialResponse.credential;

  try {
    const res = await axios.post(
      "http://localhost:8000/auth/google-login",
      null,
      { params: { token } }
    );

    // ✅ Store BOTH user + JWT token
    localStorage.setItem("user", JSON.stringify(res.data.user));
    localStorage.setItem("token", res.data.access_token);

    setUser(res.data.user);
    setShowLogin(false);

  } catch (err) {
    console.error("Login error:", err);
  }
};

  //  Handle Logout
  const handleLogout = () => {
    googleLogout(); // logout from google session
    localStorage.removeItem("user"); // remove from storage
    localStorage.removeItem("token"); // remove token from storage
    setUser(null); // update UI
  };

  return (
    <nav className="px-8 py-5 flex justify-between items-center backdrop-blur-md bg-white/5 border-b border-white/10 relative">
      
      <div className="text-2xl font-semibold tracking-wide">
        InterviewIQ
      </div>

      {user ? (
        <div className="flex items-center gap-3">
          <img
            src={user.picture}
            alt="user"
            className="w-8 h-8 rounded-full"
          />
          <span className="text-white">{user.name}</span>

          {/* 🔴 Logout Button */}
          <button
            onClick={handleLogout}
            className="ml-3 px-4 py-1 rounded-lg bg-red-500 hover:bg-red-400 text-white transition"
          >
            Logout
          </button>
        </div>
      ) : (
        <div className="relative">
          <button
            onClick={() => setShowLogin((prev) => !prev)}
            className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 transition"
          >
            Login
          </button>

          {showLogin && (
            <div className="absolute right-0 mt-2 bg-white p-3 rounded-lg shadow z-50">
              <GoogleLogin
                onSuccess={handleSuccess}
                onError={() => console.log("Login Failed")}
              />
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;