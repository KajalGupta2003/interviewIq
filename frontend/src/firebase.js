import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyATtTzgx7qxj7nvKldDXmgBR8UOcJki23o",
  authDomain: "interviewiq-42cff.firebaseapp.com",
  projectId: "interviewiq-42cff",
  storageBucket: "interviewiq-42cff.firebasestorage.app",
  messagingSenderId: "140332360513",
  appId: "1:140332360513:web:1a2ec2d9588da360adb7c0",
  measurementId: "G-T8RVZCSG2Y",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const provider = new GoogleAuthProvider();