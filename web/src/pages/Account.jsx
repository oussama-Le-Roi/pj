import { useAuth } from '../contexts/AuthContext'
import { Link } from 'react-router-dom'

export default function Account() {
  const { user, logout, isAdmin } = useAuth()
  const orders = JSON.parse(localStorage.getItem('gadgetsn_orders')||'[]').filter(o=>o.userId===user?.id)
  const points = localStorage.getItem('gadgetsn_points')||0

  if(!user) return <div className="p-20 text-center">Please <Link to="/login" className="underline">login</Link> first.</div>

  return (
    <div className="max-w-[1000px] mx-auto px-4 md:px-6 py-8">
      <div className="flex items-center gap-4">
        <img src={user.photo} alt="" className="w-16 h-16 rounded-full" />
        <div><h1 className="text-[24px] font-black">{user.name}</h1><div className="text-sm opacity-60">{user.email} {isAdmin && "• ADMIN"}</div><div className="mt-1 text-xs bg-[#a3ff12] inline-block px-2 py-1 rounded-full font-bold">{points} points earned from reviews</div></div>
        <button onClick={logout} className="ml-auto border rounded-full px-5 py-2 text-sm">Logout</button>
      </div>

      <div className="mt-8 grid md:grid-cols-3 gap-6">
        <div className="bg-white rounded-[20px] border p-6"><h3 className="font-bold">Orders</h3><div className="text-3xl font-black mt-2">{orders.length}</div><Link to="/account/orders" className="text-sm underline">View all</Link></div>
        <div className="bg-white rounded-[20px] border p-6"><h3 className="font-bold">Wishlist</h3><div className="text-3xl font-black mt-2">{JSON.parse(localStorage.getItem('gadgetsn_wishlist')||'[]').length}</div><Link to="/wishlist" className="text-sm underline">View wishlist</Link></div>
        <div className="bg-white rounded-[20px] border p-6"><h3 className="font-bold">Profile Settings</h3><div className="text-sm opacity-60 mt-2">Update address, password, notifications</div><button className="mt-3 bg-black text-white px-4 py-2 rounded-full text-sm">Edit profile</button></div>
      </div>

      <div className="mt-8 bg-white rounded-[24px] border p-6">
        <h3 className="font-bold text-[18px]">Recent Orders</h3>
        {orders.length===0 ? <div className="mt-4 text-sm opacity-50">No orders yet. <Link to="/" className="underline">Start shopping</Link></div> :
          <div className="mt-4 space-y-3">{orders.slice(0,5).map(o=><div key={o.id} className="flex items-center justify-between border rounded-xl p-3"><div><b>#{o.id}</b> • {o.items.length} items • ${o.total.toFixed(2)}<br/><span className="text-xs opacity-60">{o.date} • {o.status}</span></div><span className={`text-xs px-2 py-1 rounded-full font-bold ${o.status==='delivered'?'bg-green-100 text-green-700':'bg-yellow-100'}`}>{o.status}</span></div>)}</div>
        }
      </div>
    </div>
  )
}
