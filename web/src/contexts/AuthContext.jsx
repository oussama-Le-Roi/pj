import { createContext, useContext, useEffect, useState } from 'react'
import { auth, googleProvider, isAdminEmail, ADMIN_EMAIL } from '../lib/firebase'
import { signInWithPopup, signOut, onAuthStateChanged } from 'firebase/auth'

const AuthContext = createContext(null)

export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('gadgetsn_user')
    return saved ? JSON.parse(saved) : null
  })
  const [loading, setLoading] = useState(true)
  const [isFirebaseConfigured, setIsFirebaseConfigured] = useState(true)

  useEffect(() => {
    // Try Firebase auth listener, fallback to localStorage if demo mode
    if (!auth || import.meta.env.VITE_FIREBASE_API_KEY === undefined && !import.meta.env.VITE_FIREBASE_API_KEY) {
      // Check if real Firebase config present
      if (!import.meta.env.VITE_FIREBASE_API_KEY) {
        setIsFirebaseConfigured(false)
      }
      setLoading(false)
      return
    }
    const unsub = onAuthStateChanged(auth, (fbUser) => {
      if (fbUser) {
        const u = {
          id: fbUser.uid,
          email: fbUser.email,
          name: fbUser.displayName,
          photo: fbUser.photoURL,
          isAdmin: isAdminEmail(fbUser.email)
        }
        setUser(u)
        localStorage.setItem('gadgetsn_user', JSON.stringify(u))
      }
      setLoading(false)
    }, () => setLoading(false))
    return () => unsub()
  }, [])

  const login = async (mockEmail) => {
    // If Firebase is configured, use Google popup
    if (auth && googleProvider && isFirebaseConfigured) {
      try {
        const res = await signInWithPopup(auth, googleProvider)
        const fbUser = res.user
        // Only allow admin email for dashboard, but any user can login for customer account
        const u = {
          id: fbUser.uid,
          email: fbUser.email,
          name: fbUser.displayName || fbUser.email.split('@')[0],
          photo: fbUser.photoURL,
          isAdmin: isAdminEmail(fbUser.email)
        }
        setUser(u)
        localStorage.setItem('gadgetsn_user', JSON.stringify(u))
        return u
      } catch (e) {
        console.error(e)
        throw e
      }
    } else {
      // DEMO MODE - simulate login
      const email = mockEmail || prompt("Demo mode - Enter email (use oussamabriedj2001@gmail.com for admin):") || ""
      if (!email) throw new Error("Email required")
      const u = {
        id: "demo-" + email,
        email,
        name: email.split('@')[0],
        photo: `https://api.dicebear.com/7.x/initials/svg?seed=${email}`,
        isAdmin: isAdminEmail(email)
      }
      setUser(u)
      localStorage.setItem('gadgetsn_user', JSON.stringify(u))
      return u
    }
  }

  const loginAsAdmin = () => login(ADMIN_EMAIL)

  const logout = async () => {
    if (auth) { try { await signOut(auth) } catch {} }
    setUser(null)
    localStorage.removeItem('gadgetsn_user')
  }

  const value = { user, loading, login, loginAsAdmin, logout, isAdmin: user?.isAdmin || false, isFirebaseConfigured, ADMIN_EMAIL }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
