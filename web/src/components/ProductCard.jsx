import { Link } from 'react-router-dom'
import { Heart, Star, ShoppingBag } from 'lucide-react'
import { useCart } from '../contexts/CartContext'

export default function ProductCard({ product }) {
  const { addToCart, wishlist, toggleWishlist } = useCart()
  const isWish = wishlist.includes(product.id)
  return (
    <div className="group bg-white rounded-[22px] overflow-hidden border border-zinc-100 hover:shadow-xl transition">
      <Link to={`/products/${product.handle}`} className="block relative aspect-[4/3] overflow-hidden bg-zinc-50">
        <img src={product.images[0]} alt={product.title} className="w-full h-full object-cover group-hover:scale-105 transition duration-500" />
        <div className="absolute top-3 left-3 flex gap-2">
          {product.compareAt > product.price && <span className="bg-[#a3ff12] text-black text-[11px] font-bold px-2.5 py-1 rounded-full">-{Math.round((1-product.price/product.compareAt)*100)}%</span>}
          {product.tags.includes('bestseller') && <span className="bg-black text-white text-[11px] font-bold px-2.5 py-1 rounded-full">BESTSELLER</span>}
        </div>
        <button onClick={(e)=>{ e.preventDefault(); toggleWishlist(product)}} className={`absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center backdrop-blur ${isWish? 'bg-black text-white':'bg-white/80'}`}><Heart size={16} fill={isWish?'currentColor':''} /></button>
        <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center opacity-0 group-hover:opacity-100 transition">
          <span className="bg-white/90 backdrop-blur rounded-full px-3 py-1 text-[11px] flex items-center gap-1"><Star size={12} fill="black"/> {product.rating} ({product.reviewsCount})</span>
          <span className={`w-2 h-2 rounded-full ${product.stock>20?'bg-green-500':'bg-orange-500'}`} title={`${product.stock} in stock`} />
        </div>
      </Link>
      <div className="p-4">
        <Link to={`/products/${product.handle}`} className="block">
          <div className="text-[11px] tracking-widest opacity-50">{product.category}</div>
          <h3 className="font-semibold leading-tight mt-1 line-clamp-2 h-[40px] text-[14px]">{product.title}</h3>
        </Link>
        <div className="flex items-center justify-between mt-3">
          <div><span className="font-black text-[16px]">${product.price}</span> {product.compareAt>product.price && <span className="ml-2 text-[12px] line-through opacity-40">${product.compareAt}</span>}</div>
          <button onClick={()=>addToCart(product)} className="w-9 h-9 rounded-full bg-black text-white flex items-center justify-center hover:bg-zinc-800"><ShoppingBag size={16}/></button>
        </div>
      </div>
    </div>
  )
}
