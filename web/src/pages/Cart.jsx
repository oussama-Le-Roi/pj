import { useCart } from '../contexts/CartContext'
import { useAuth } from '../contexts/AuthContext'
import { Link, useNavigate } from 'react-router-dom'

export default function Cart() {
  const { items, updateQty, removeFromCart, total, clearCart } = useCart()
  const { user } = useAuth()
  const nav = useNavigate()

  const checkout = () => {
    if(!user) { nav('/login'); return }
    if(items.length===0) return
    const order = { id: Date.now().toString().slice(-6), userId: user.id, items, total, date: new Date().toISOString().split('T')[0], status: 'processing', shipping: 'Free' }
    const prev = JSON.parse(localStorage.getItem('gadgetsn_orders')||'[]')
    localStorage.setItem('gadgetsn_orders', JSON.stringify([order, ...prev]))
    clearCart()
    // simulate email trigger for review after 3 days
    alert(`Order #${order.id} placed! You will receive tracking email soon. After delivery, we'll email you to invite for photo review (like AliExpress).`)
    nav('/account/orders')
  }

  if(items.length===0) return <div className="min-h-[60vh] flex flex-col items-center justify-center"><div className="text-[48px]">🛒</div><h2 className="text-2xl font-black mt-2">Your cart is empty</h2><Link to="/" className="mt-4 bg-black text-white px-6 py-3 rounded-full">Continue shopping</Link></div>

  return (
    <div className="max-w-[1100px] mx-auto px-4 md:px-6 py-8 grid md:grid-cols-[1.2fr_0.5fr] gap-6">
      <div className="bg-white rounded-[24px] border p-6">
        <h1 className="text-[24px] font-black">Shopping Cart ({items.length})</h1>
        <div className="mt-6 space-y-4">
          {items.map(it=><div key={it.id+it.variantIndex} className="flex gap-4 border-b pb-4">
            <img src={it.image} alt="" className="w-20 h-20 rounded-xl object-cover bg-zinc-50" />
            <div className="flex-1"><b className="text-sm">{it.title}</b><div className="text-xs opacity-60">{it.variantTitle}</div><div className="mt-2 flex items-center gap-2"><button onClick={()=>updateQty(it.id,it.variantIndex,it.qty-1)} className="w-6 h-6 border rounded-full">-</button><span className="w-6 text-center text-sm">{it.qty}</span><button onClick={()=>updateQty(it.id,it.variantIndex,it.qty+1)} className="w-6 h-6 border rounded-full">+</button><button onClick={()=>removeFromCart(it.id,it.variantIndex)} className="ml-4 text-xs underline opacity-60">Remove</button></div></div>
            <div className="font-bold">${(it.price*it.qty).toFixed(2)}</div>
          </div>)}
        </div>
      </div>
      <div className="bg-white rounded-[24px] border p-6 h-fit">
        <h3 className="font-bold">Order summary</h3>
        <div className="mt-4 space-y-2 text-sm"><div className="flex justify-between"><span>Subtotal</span><span>${total.toFixed(2)}</span></div><div className="flex justify-between"><span>Shipping</span><span className="text-green-600 font-bold">Free</span></div><div className="flex justify-between"><span>Tax</span><span>Calculated at checkout</span></div><div className="border-t pt-2 flex justify-between font-black text-[16px]"><span>Total</span><span>${total.toFixed(2)}</span></div></div>
        <button onClick={checkout} className="mt-6 w-full bg-black text-white py-3 rounded-full font-bold">Checkout • Secure</button>
        <div className="mt-3 text-[11px] text-center opacity-60">✓ SSL Secure • PayPal • Apple Pay • 30-day returns • 2-year warranty</div>
      </div>
    </div>
  )
}
