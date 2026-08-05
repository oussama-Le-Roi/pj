import { useParams } from 'react-router-dom'
import { products } from '../data/products'
import { reviewsMock } from '../data/reviews'
import { useState } from 'react'
import { useCart } from '../contexts/CartContext'
import { useAuth } from '../contexts/AuthContext'
import ReviewSection from '../components/ReviewSection'
import { Truck, Shield, RotateCcw, Star, Heart, Share, Minus, Plus, Check } from 'lucide-react'

export default function Product() {
  const { handle } = useParams()
  const product = products.find(p=>p.handle===handle) || products[0]
  const [idx, setIdx] = useState(0)
  const [variant, setVariant] = useState(0)
  const [qty, setQty] = useState(1)
  const { addToCart, toggleWishlist, wishlist } = useCart()
  const { user } = useAuth()
  const [reviews, setReviews] = useState(reviewsMock)

  // mock orders to check if user can review
  const mockOrders = JSON.parse(localStorage.getItem('gadgetsn_orders')||'[]')
  const canReview = user && mockOrders.some(o=> o.userId===user.id && o.status==='delivered' && o.items.some(i=>i.id===product.id))

  const handleReview = (newR)=>{
    const review = { id: Date.now(), productId: product.id, user: user.name, avatar: user.name.slice(0,2).toUpperCase(), rating: newR.rating, verified: true, date: new Date().toISOString().split('T')[0], comment: newR.comment, image: newR.image, helpful:0, purchaseDate: new Date().toISOString().split('T')[0] }
    setReviews([...reviews, review])
    // reward points
    const points = parseInt(localStorage.getItem('gadgetsn_points')||'0') + (newR.image?50:20)
    localStorage.setItem('gadgetsn_points', points)
    alert(`Review submitted! +${newR.image?50:20} points earned. ${newR.image?'10% discount code: REVIEW10':''}`)
  }

  return (
    <div className="max-w-[1280px] mx-auto px-4 md:px-6 py-6">
      <div className="text-[12px] opacity-50">Home / {product.category} / {product.title}</div>

      <div className="grid md:grid-cols-2 gap-8 mt-4">
        {/* Images */}
        <div className="space-y-3">
          <div className="aspect-[4/3] bg-white rounded-[28px] overflow-hidden border">
            <img src={product.images[idx]} alt={product.title} className="w-full h-full object-cover" />
          </div>
          <div className="flex gap-2 overflow-x-auto">
            {product.images.map((im,i)=><button key={i} onClick={()=>setIdx(i)} className={`w-[84px] h-[84px] rounded-2xl overflow-hidden border-2 shrink-0 ${idx===i?'border-black':'border-transparent'}`}><img src={im} alt="" className="w-full h-full object-cover" /></button>)}
          </div>
        </div>

        {/* Info */}
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-[#a3ff12] text-black text-[11px] font-bold px-2.5 py-1 rounded-full">IN STOCK • {product.stock} left</span>
            <span className="flex items-center gap-1 bg-zinc-100 px-2.5 py-1 rounded-full text-[11px]"><Star size={12} fill="black"/> {product.rating} ({product.reviewsCount})</span>
          </div>
          <h1 className="text-[32px] font-black leading-[1.05] mt-4">{product.title}</h1>
          <div className="mt-3 flex items-center gap-3">
            <span className="text-[28px] font-black">${(product.variants[variant]?.price||product.price).toFixed(2)}</span>
            {product.compareAt && <span className="line-through opacity-40">${product.compareAt}</span>}
            {product.compareAt && <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-bold">SAVE ${(product.compareAt - (product.variants[variant]?.price||product.price)).toFixed(2)}</span>}
          </div>
          <p className="mt-4 text-[14px] leading-relaxed opacity-70">{product.description}</p>

          <div className="mt-6">
            <div className="text-xs font-bold tracking-widest opacity-60">VARIANT</div>
            <div className="flex gap-2 mt-2">{product.variants.map((v,i)=><button key={i} onClick={()=>setVariant(i)} className={`px-4 py-2 rounded-full border text-sm ${variant===i?'bg-black text-white border-black':'bg-white'}`}>{v.title} • ${v.price}</button>)}</div>
          </div>

          <div className="mt-6 flex gap-3">
            <div className="flex items-center gap-2 bg-white border rounded-full px-2">
              <button onClick={()=>setQty(Math.max(1,qty-1))} className="w-8 h-8 rounded-full hover:bg-zinc-100 flex items-center justify-center"><Minus size={14}/></button>
              <span className="w-8 text-center font-bold text-sm">{qty}</span>
              <button onClick={()=>setQty(qty+1)} className="w-8 h-8 rounded-full hover:bg-zinc-100 flex items-center justify-center"><Plus size={14}/></button>
            </div>
            <button onClick={()=>{ addToCart(product, variant, qty); alert("Added to cart!") }} className="flex-1 bg-black text-white rounded-full py-3 font-bold text-sm hover:bg-zinc-800">Add to Cart - ${( (product.variants[variant]?.price||product.price)*qty).toFixed(2)}</button>
            <button onClick={()=>toggleWishlist(product)} className={`w-[52px] h-[52px] rounded-full border flex items-center justify-center ${wishlist.includes(product.id)?'bg-black text-white':'bg-white'}`}><Heart size={18} fill={wishlist.includes(product.id)?'currentColor':''} /></button>
            <button className="w-[52px] h-[52px] rounded-full border bg-white flex items-center justify-center"><Share size={18}/></button>
          </div>

          <div className="mt-6 grid grid-cols-3 gap-2 text-[11px]">
            <div className="bg-white border rounded-2xl p-3 text-center"><Truck className="mx-auto" size={20}/><div className="font-bold mt-1">Free Shipping</div><div className="opacity-60">5-12 days, tracked</div></div>
            <div className="bg-white border rounded-2xl p-3 text-center"><RotateCcw className="mx-auto" size={20}/><div className="font-bold mt-1">30-Day Return</div><div className="opacity-60">No questions</div></div>
            <div className="bg-white border rounded-2xl p-3 text-center"><Shield className="mx-auto" size={20}/><div className="font-bold mt-1">2Y Warranty</div><div className="opacity-60">Official</div></div>
          </div>

          <div className="mt-6 bg-zinc-50 rounded-2xl p-4 text-[12px]">
            <div className="font-bold">✓ In stock, ready to ship • Ships from US/EU warehouse</div>
            <div className="opacity-70 mt-1">Order within 2h 15m for same-day dispatch. Estimated delivery: {new Date(Date.now()+7*24*3600*1000).toLocaleDateString()} - {new Date(Date.now()+12*24*3600*1000).toLocaleDateString()}</div>
            <div className="mt-3 flex items-center gap-2"><Check size={12} className="text-green-600"/> PayPal • Apple Pay • Visa • MasterCard • Bitcoin • Afterpay</div>
          </div>

          <div className="mt-8 border-t pt-6">
            <h4 className="font-bold">Specifications</h4>
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">{Object.entries(product.specs).map(([k,v])=><div key={k} className="flex justify-between bg-white border rounded-xl p-3"><span className="opacity-60">{k}</span><b>{v}</b></div>)}</div>
          </div>
        </div>
      </div>

      <div className="mt-12"><ReviewSection productId={product.id} reviews={reviews} canReview={!!canReview} onSubmitReview={handleReview} /></div>
    </div>
  )
}
