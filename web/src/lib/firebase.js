import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

// Firebase config - replace with your real config from Firebase Console
// For now we use env variables, fallback to demo mode if missing
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "demo-api-key",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "gadgetsn-store.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "gadgetsn-store",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "gadgetsn-store.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:123456789:web:abcdef"
}

let app, auth, googleProvider
try {
  app = initializeApp(firebaseConfig)
  auth = getAuth(app)
  googleProvider = new GoogleAuthProvider()
} catch (e) {
  console.warn("Firebase init failed, using mock mode", e)
  auth = null
  googleProvider = null
}

export { auth, googleProvider }
export const ADMIN_EMAIL = "oussamabriedj2001@gmail.com"
export const isAdminEmail = (email) => email?.toLowerCase() === ADMIN_EMAIL.toLowerCase()
