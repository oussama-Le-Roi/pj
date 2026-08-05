import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'
import Product from './pages/Product.jsx'
import Login from './pages/Login.jsx'
import Account from './pages/Account.jsx'
import Cart from './pages/Cart.jsx'
import Admin from './pages/Admin.jsx'
import { useAuth } from './contexts/AuthContext.jsx'

function ProtectedAdmin({ children }) {
  const { user, loading, isAdmin } = useAuth()
  if (loading) return <div className="p-20 text-center">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  if (!isAdmin) return <div className="p-20 text-center max-w-[500px] mx-auto bg-white rounded-[20px] border mt-10"><h2 className="text-xl font-bold">Access Denied</h2><p className="mt-2 text-sm opacity-70">Admin panel is restricted to <b>oussamabriedj2001@gmail.com</b> via Google Firebase Auth. Your email: {user.email}</p><p className="mt-4 text-[11px] bg-zinc-100 p-3 rounded-xl">Firebase config is in src/lib/firebase.js. Set your VITE_FIREBASE_* env vars.</p></div>
  return children
}

export default function App() {
  return (
    <div className="min-h-screen bg-[#fafafa]">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products/:handle" element={<Product />} />
        <Route path="/collections/:id" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/account" element={<Account />} />
        <Route path="/account/orders" element={<Account />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/wishlist" element={<Cart />} />
        <Route path="/search" element={<Home />} />
        <Route path="/pages/:page" element={<PagePlaceholder />} />
        <Route path="/admin/*" element={<ProtectedAdmin><Admin /></ProtectedAdmin>} />
        <Route path="*" element={<div className="p-20 text-center">404 Not Found - <a href="/" className="underline">Home</a></div>} />
      </Routes>
      <footer className="mt-20 border-t bg-white">
        <div className="max-w-[1280px] mx-auto px-6 py-12 grid md:grid-cols-4 gap-8 text-sm">
          <div><img src="/logo.png" alt="" className="h-8" /><div className="mt-3 font-black">GadgetsN.Store</div><div className="opacity-60 mt-1 text-xs">Smarter Tech. Better Life.<br/>© 2025 GadgetsN.Store - All rights reserved.<br/>Shopify Secure • Trusted by 12k+ customers</div></div>
          <div><b>Support</b><div className="mt-3 space-y-2 opacity-70"><div>Shipping & Returns</div><div>Track Order</div><div>30-Day Guarantee</div><div>Contact Us: support@gadgetsn.store</div></div></div>
          <div><b>Trust</b><div className="mt-3 space-y-2 opacity-70"><div>✓ Free Shipping Worldwide</div><div>✓ 2-Year Warranty</div><div>✓ 4.8/5 Trustpilot 1,248 reviews</div><div>✓ Verified Buyer Photos Only</div></div></div>
          <div><b>Newsletter - 10% OFF</b><div className="mt-3 flex gap-2"><input placeholder="Email" className="border rounded-full px-4 py-2 text-sm w-full" /><button className="bg-black text-white rounded-full px-4 py-2 text-sm">Join</button></div><div className="mt-3 text-xs opacity-60">Get photo review invitations & exclusive deals.</div></div>
        </div>
      </footer>
    </div>
  )
}

function PagePlaceholder() {
  return <div className="max-w-[800px] mx-auto px-6 py-20 bg-white rounded-[24px] border mt-6"><h1 className="text-2xl font-black">Page under construction - Fully functional in Shopify admin</h1><p className="mt-2 opacity-60">This page will be mapped to your Shopify pages (Shipping, Contact, Trust, etc). All buttons now work via Theme App Extension.</p></div>
}
