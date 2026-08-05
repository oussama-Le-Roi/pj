import { Link, useNavigate } from 'react-router-dom'
import { ShoppingBag, Heart, User, Search, Menu, LogOut, LayoutDashboard, Globe } from 'lucide-react'
import { useCart } from '../contexts/CartContext'
import { useAuth } from '../contexts/AuthContext'
import { useState } from 'react'

export default function Navbar() {
  const { count, wishlist } = useCart()
  const { user, logout, isAdmin } = useAuth()
  const [lang, setLang] = useState('EN')
  const [showMobile, setShowMobile] = useState(false)
  const nav = useNavigate()

  return (
    <div className="sticky top-0 z-50">
      {/* Top trust bar */}
      <div className="bg-black text-white text-[11px] tracking-widest py-2 text-center flex justify-center gap-6">
        <span>✓ FREE SHIPPING WORLDWIDE</span>
        <span className="hidden md:inline">✓ 30-DAY MONEY BACK</span>
        <span className="hidden md:inline">✓ 24/7 SUPPORT</span>
        <span className="flex items-center gap-1"><Globe size={12}/> {lang}</span>
      </div>

      <header className="bg-white/90 backdrop-blur border-b border-zinc-100">
        <div className="max-w-[1280px] mx-auto px-4 md:px-6 h-[68px] flex items-center justify-between">
          <div className="flex items-center gap-8">
            <button className="md:hidden" onClick={()=>setShowMobile(!showMobile)}><Menu /></button>
            <Link to="/" className="flex items-center gap-3">
              <img src="/logo.png" alt="GadgetsN.Store" className="h-10 w-auto object-contain" />
              <span className="hidden lg:flex flex-col leading-none">
                <b className="text-[18px] tracking-tight">GadgetsN<span className="text-lime-500">.</span>Store</b>
                <span className="text-[10px] tracking-[0.2em] opacity-60">SMARTER TECH</span>
              </span>
            </Link>
            <nav className="hidden md:flex gap-6 text-[14px] font-medium">
              <Link to="/" className="hover:opacity-60">Home</Link>
              <Link to="/collections/all" className="hover:opacity-60">Shop All</Link>
              <Link to="/collections/bestsellers" className="hover:opacity-60">Best Sellers</Link>
              <Link to="/pages/shipping" className="hover:opacity-60">Shipping</Link>
              <Link to="/pages/contact" className="hover:opacity-60">Contact</Link>
            </nav>
          </div>

          <div className="flex items-center gap-2 md:gap-3">
            <div className="hidden md:flex items-center bg-zinc-100 rounded-full px-4 py-2 gap-2">
              <Search size={16} className="opacity-50" />
              <input placeholder="Search gadgets..." className="bg-transparent outline-none text-sm w-[180px]" onKeyDown={(e)=>{ if(e.key==='Enter') nav(`/search?q=${e.target.value}`)}} />
            </div>
            <Link to="/wishlist" className="relative p-2.5 rounded-full hover:bg-zinc-100"><Heart size={20} />{wishlist.length>0 && <span className="absolute -top-1 -right-1 bg-black text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">{wishlist.length}</span>}</Link>
            <Link to="/cart" className="relative p-2.5 rounded-full bg-black text-white"><ShoppingBag size={18} />{count>0 && <span className="absolute -top-1 -right-1 bg-[#a3ff12] text-black text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">{count}</span>}</Link>

            {user ? (
              <div className="flex items-center gap-2">
                {isAdmin && <Link to="/admin" className="hidden md:flex items-center gap-2 bg-[#a3ff12] text-black px-4 py-2 rounded-full text-sm font-semibold"><LayoutDashboard size={16}/> Dashboard</Link>}
                <div className="relative group">
                  <Link to="/account" className="flex items-center gap-2 pl-1 pr-3 py-1 rounded-full bg-zinc-100 hover:bg-zinc-200">
                    <img src={user.photo} alt="" className="w-7 h-7 rounded-full object-cover" />
                    <span className="hidden md:inline text-sm font-medium max-w-[100px] truncate">{user.name}</span>
                  </Link>
                  <div className="absolute right-0 top-full pt-2 hidden group-hover:block">
                    <div className="bg-white rounded-2xl shadow-xl border p-2 min-w-[200px]">
                      <div className="p-3 text-sm"><b>{user.name}</b><br/><span className="text-zinc-500 text-xs">{user.email}</span>{isAdmin && <span className="block mt-1 text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full w-fit">ADMIN • {user.email}</span>}</div>
                      <Link to="/account" className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-zinc-100 text-sm"><User size={16}/> My Account</Link>
                      <Link to="/account/orders" className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-zinc-100 text-sm"><ShoppingBag size={16}/> Orders</Link>
                      {isAdmin && <Link to="/admin" className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-zinc-100 text-sm"><LayoutDashboard size={16}/> Admin Panel</Link>}
                      <button onClick={logout} className="w-full flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-red-50 text-red-600 text-sm"><LogOut size={16}/> Logout</button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <Link to="/login" className="flex items-center gap-2 bg-zinc-100 hover:bg-zinc-200 px-4 py-2.5 rounded-full text-sm font-semibold"><User size={16}/> Login</Link>
            )}
          </div>
        </div>

        {showMobile && (
          <div className="md:hidden border-t bg-white p-4 space-y-3">
            <Link to="/" className="block py-2" onClick={()=>setShowMobile(false)}>Home</Link>
            <Link to="/collections/all" className="block py-2" onClick={()=>setShowMobile(false)}>Shop All</Link>
            <Link to="/pages/shipping" className="block py-2" onClick={()=>setShowMobile(false)}>Shipping & Returns</Link>
            <Link to="/pages/trust" className="block py-2" onClick={()=>setShowMobile(false)}>Why Trust Us</Link>
          </div>
        )}
      </header>
    </div>
  )
}
