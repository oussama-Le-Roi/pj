import { useEffect, useState } from 'react'
import { products } from '../data/products'
import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles, Truck, Shield } from 'lucide-react'

export default function Hero() {
  const [randomProduct, setRandomProduct] = useState(products[0])

  useEffect(()=>{
    const rnd = products[Math.floor(Math.random()*products.length)]
    setRandomProduct(rnd)
  }, [])

  return (
    <div className="max-w-[1280px] mx-auto px-4 md:px-6 mt-6">
      {/* Promo ticker */}
      <div className="bg-[#a3ff12] rounded-full text-center py-2 text-[12px] font-bold tracking-widest mb-4">WELCOME! SITEWIDE SALE • FREE SHIPPING! • 30-DAY RETURN • WELCOME!</div>

      <div className="grid md:grid-cols-[1.4fr_0.8fr] gap-4">
        {/* Main hero linking to random product */}
        <Link to={`/products/${randomProduct.handle}`} className="relative rounded-[28px] overflow-hidden bg-black text-white min-h-[480px] group block">
          <img src={randomProduct.images[0]} alt={randomProduct.title} className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:scale-[1.02] transition duration-700" />
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
          <div className="relative z-10 p-8 md:p-12 h-full flex flex-col justify-end">
            <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur px-3 py-1 rounded-full text-xs mb-4 w-fit"><Sparkles size={12}/> Featured • {randomProduct.category} • ★ {randomProduct.rating}</div>
            <h1 className="text-[32px] md:text-[54px] leading-[0.95] font-black tracking-tighter max-w-[500px]">{randomProduct.title.split(' - ')[0]}<br/><span className="text-[#a3ff12]">On Sale Now</span></h1>
            <p className="mt-4 text-white/70 max-w-[440px] text-[15px]">{randomProduct.description.slice(0,120)}...</p>
            <div className="mt-6 flex items-center gap-4">
              <span className="bg-white text-black px-7 py-3 rounded-full font-bold flex items-center gap-2">Shop Now <ArrowRight size={16}/></span>
              <span className="text-2xl font-black">${randomProduct.price} <span className="text-sm line-through opacity-50 font-normal">${randomProduct.compareAt}</span></span>
            </div>
            <div className="mt-6 flex gap-6 text-[11px] tracking-widest opacity-80">
              <span className="flex items-center gap-1"><Truck size={14}/> FREE SHIPPING</span>
              <span className="flex items-center gap-1"><Shield size={14}/> 2-YEAR WARRANTY</span>
            </div>
          </div>
        </Link>

        {/* Side stacked */}
        <div className="grid grid-rows-2 gap-4">
          <Link to={`/products/${products[1].handle}`} className="rounded-[28px] overflow-hidden bg-zinc-900 text-white relative min-h-[230px] group block">
            <img src={products[1].images[0]} alt="" className="absolute inset-0 w-full h-full object-cover opacity-70 group-hover:scale-105 transition duration-700" />
            <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent" />
            <div className="relative z-10 p-7 h-full flex flex-col justify-end">
              <div className="text-[11px] tracking-widest opacity-70">SMART HOME</div>
              <h3 className="text-[22px] font-bold leading-tight mt-1">{products[1].title}</h3>
              <span className="mt-3 inline-flex bg-[#a3ff12] text-black px-4 py-1.5 rounded-full text-xs font-bold">From ${products[1].price}</span>
            </div>
          </Link>
          <Link to={`/products/${products[2].handle}`} className="rounded-[28px] overflow-hidden bg-white border relative min-h-[230px] group block">
            <img src={products[2].images[0]} alt="" className="absolute inset-0 w-full h-full object-cover opacity-90 group-hover:scale-105 transition duration-700" />
            <div className="absolute inset-0 bg-gradient-to-t from-white via-white/40 to-transparent" />
            <div className="relative z-10 p-7 h-full flex flex-col justify-end">
              <div className="text-[11px] tracking-widest opacity-60">CHARGING • FAST</div>
              <h3 className="text-[22px] font-bold leading-tight mt-1 text-black">{products[2].title}</h3>
              <span className="mt-3 inline-flex bg-black text-white px-4 py-1.5 rounded-full text-xs font-bold">Shop Now →</span>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
