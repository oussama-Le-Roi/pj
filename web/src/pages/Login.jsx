import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'

export default function Login() {
  const { login, loginAsAdmin, user, ADMIN_EMAIL } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e) => {
    e?.preventDefault()
    setLoading(true)
    try { const u = await login(email || undefined); if(u?.isAdmin) nav('/admin'); else nav('/account') } catch (err) { alert(err.message) } finally { setLoading(false) }
  }

  const handleAdmin = async () => {
    setLoading(true)
    try { await loginAsAdmin(); nav('/admin') } catch (e) { alert(e.message) } finally { setLoading(false) }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-[440px] bg-white rounded-[28px] border p-8">
        <div className="text-center">
          <img src="/logo.png" alt="logo" className="h-12 mx-auto" />
          <h1 className="text-[28px] font-black mt-4">Welcome to GadgetsN.Store</h1>
          <p className="text-sm opacity-60 mt-1">Login to manage orders, reviews & wishlist</p>
        </div>

        <form onSubmit={handleLogin} className="mt-8 space-y-3">
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email address" className="w-full border rounded-full px-5 py-3 text-sm outline-none focus:border-black" />
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password (demo mode any password works)" className="w-full border rounded-full px-5 py-3 text-sm outline-none focus:border-black" />
          <button disabled={loading} className="w-full bg-black text-white rounded-full py-3 font-bold text-sm">{loading?'Loading...':'Login / Sign Up'}</button>
        </form>

        <div className="mt-3 grid grid-cols-2 gap-2">
          <button onClick={handleLogin} className="border rounded-full py-2.5 text-sm font-semibold flex items-center justify-center gap-2"><img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-4 h-4"/> Continue with Google</button>
          <button onClick={handleAdmin} className="bg-[#a3ff12] rounded-full py-2.5 text-sm font-bold">Admin Login Only</button>
        </div>

        <div className="mt-6 p-3 bg-zinc-50 rounded-xl text-[11px]">
          <b>Admin Demo:</b> Use <code>{ADMIN_EMAIL}</code> to access full dashboard. Firebase Google Auth implemented via <code>src/lib/firebase.js</code>. Replace env vars with real Firebase config for production.
        </div>

        <div className="mt-6 text-center text-xs opacity-60">No account? It will be auto-created. <Link to="/" className="underline">Back to store</Link></div>

        {user && <div className="mt-4 p-3 bg-green-50 text-green-800 rounded-xl text-sm">Logged in as {user.email} {user.isAdmin && "(ADMIN)"}</div>}
      </div>
    </div>
  )
}
