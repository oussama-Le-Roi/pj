import Hero from '../components/Hero'
import TrustBadges from '../components/TrustBadges'
import ProductCard from '../components/ProductCard'
import { products, categories } from '../data/products'
import { useState } from 'react'
import { ArrowRight, CheckCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Home() {
  const [cat, setCat] = useState('All')
  const filtered = cat==='All'? products : products.filter(p=>p.category===cat)

  return (
    <div className="pb-[80px]">
      <Hero />
      <TrustBadges />

      <div className="max-w-[1280px] mx-auto px-4 md:px-6 mt-8 flex gap-2 overflow-x-auto scrollbar-none">
        {categories.map(c=> <button key={c} onClick={()=>setCat(c)} className={`px-5 py-2.5 rounded-full text-sm font-semibold whitespace-nowrap border ${cat===c?'bg-black text-white border-black':'bg-white hover:bg-zinc-100'}`}>{c}</button>)}
      </div>

      <div className="max-w-[1280px] mx-auto px-4 md:px-6 mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {filtered.map(p=> <ProductCard key={p.id} product={p} />)}
      </div>

      {/* Why trust us - credibility */}
      <div className="max-w-[1280px] mx-auto px-4 md:px-6 mt-12 grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-[28px] p-8 border">
          <div className="text-[12px] tracking-widest opacity-50">WHY CHOOSE US?</div>
          <h3 className="text-[28px] font-black leading-none mt-3">More Than a Store.<br/>We Guarantee Your<br/><span className="text-lime-500">Satisfaction.</span></h3>
          <div className="mt-6 space-y-4 text-sm">
            <div className="flex gap-3"><CheckCircle className="text-[#a3ff12]" size={20}/><span><b>Innovative Design:</b> Nostalgic aesthetics with modern tech for unique experience.</span></div>
            <div className="flex gap-3"><CheckCircle className="text-[#a3ff12]" size={20}/><span><b>High-Quality Sound & Build:</b> Premium materials, tested 100 times before shipping.</span></div>
            <div className="flex gap-3"><CheckCircle className="text-[#a3ff12]" size={20}/><span><b>Tracked Shipping:</b> Real-time tracking from China/US warehouse, insured. 5-12 days worldwide.</span></div>
            <div className="flex gap-3"><CheckCircle className="text-[#a3ff12]" size={20}/><span><b>User Satisfaction First:</b> 24/7 support, 4.8★ Trustpilot, 12k+ happy customers.</span></div>
          </div>
          <Link to="/pages/trust" className="mt-6 inline-flex bg-black text-white px-6 py-3 rounded-full text-sm font-bold">Learn more <ArrowRight size={16} className="ml-2"/></Link>
        </div>
        <div className="rounded-[28px] overflow-hidden bg-black text-white p-8 relative min-h-[400px] flex flex-col justify-end">
          <img src="https://gadgetsn.store/cdn/shop/files/homepage3.webp?v=1785934869&width=800" alt="" className="absolute inset-0 w-full h-full object-cover opacity-60" />
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent"/>
          <div className="relative z-10">
            <div className="inline-block bg-[#a3ff12] text-black px-3 py-1 rounded-full text-xs font-bold">REAL CUSTOMER PHOTOS</div>
            <h3 className="text-[28px] font-black leading-none mt-4">See How Our Customers<br/>Use Our Gadgets Daily!</h3>
            <p className="mt-3 text-white/70 text-sm">Verified buyer photos only. No fake reviews. Like AliExpress, but curated.</p>
            <div className="mt-4 flex -space-x-2">
              {[1,2,3,4].map(i=><img key={i} src={`https://i.pravatar.cc/100?img=${i+10}`} alt="" className="w-8 h-8 rounded-full border-2 border-black" />)}
              <div className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center text-[10px] font-bold border-2 border-black">+1.2k</div>
            </div>
          </div>
        </div>
      </div>

      {/* Newsletter + shipping credibility */}
      <div className="max-w-[1280px] mx-auto px-4 md:px-6 mt-8 bg-[#a3ff12] rounded-[28px] p-8 md:p-10 flex flex-col md:flex-row justify-between gap-6">
        <div>
          <h3 className="text-[26px] font-black leading-tight">Don't Miss Our Hot Deals! Get 10% OFF</h3>
          <p className="text-sm opacity-70 mt-2">Join 8,432 gadget lovers. Free shipping coupon inside.</p>
        </div>
        <div className="flex gap-2 max-w-[420px] w-full">
          <input placeholder="Enter your email" className="flex-1 bg-white rounded-full px-5 py-3 text-sm outline-none" />
          <button className="bg-black text-white rounded-full px-6 py-3 text-sm font-bold">Subscribe</button>
        </div>
      </div>
    </div>
  )
}
