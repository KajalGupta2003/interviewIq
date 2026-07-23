
import { auth, provider } from "../firebase";
import { signInWithPopup, signOut } from "firebase/auth";
import axios from "axios";
import { Link } from "react-router-dom";

const Navbar = ({ user, setUser }) => {
  
  const handleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      

      

      await axios.post( `${import.meta.env.VITE_API_URL}/save_user`, {
        name: result.user.displayName,
        email: result.user.email,
        photo: result.user.photoURL,
      });
      console.log("User:", result.user);
      console.log("User saved successfully");
    } catch (error) {
      console.error(error);
      alert(error.message);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setUser(null);
  };

  return (
    <nav className="px-8 py-5 flex justify-between items-center backdrop-blur-md bg-white/5 border-b border-white/10">
      <div className="text-2xl font-semibold tracking-wide">
        InterviewIQ
      </div>

      {user ? (
        <div className="flex items-center gap-4">
          <Link
  to="/dashboard"
  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 transition"
>
  Dashboard
</Link>
         <img
  src={user.photoURL}
  alt="profile"
  className="w-10 h-10 rounded-full border border-white"
  referrerPolicy="no-referrer"
  onError={(e) => {
    console.log("Image Error");
    console.log(user.photoURL);

    // fallback image
    e.target.src = "https://ui-avatars.com/api/?name=" + encodeURIComponent(user.displayName);
  }}
/>

          <span className="text-sm">{user.displayName}</span>

          <button
            onClick={handleLogout}
            className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 transition"
          >
            Logout
          </button>
        </div>
      ) : (
        <button
          onClick={handleLogin}
          className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 transition"
        >
          Login with Google
        </button>
      )}
    </nav>
  );
};

export default Navbar;