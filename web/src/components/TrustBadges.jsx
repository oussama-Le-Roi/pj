import { ShieldCheck, Truck, RotateCcw, Headphones, Award, Lock } from 'lucide-react'

export default function TrustBadges() {
  const badges = [
    { icon: Truck, title: "Free Shipping", desc: "Worldwide, tracked & insured. 5-12 days delivery." },
    { icon: ShieldCheck, title: "Secure Payment", desc: "SSL encrypted. PayPal, Apple Pay, Cards, Bitcoin." },
    { icon: RotateCcw, title: "30-Day Returns", desc: "No questions asked. Free return label included." },
    { icon: Award, title: "2-Year Warranty", desc: "Official warranty on all gadgets. Replace instantly." },
  ]
  return (
    <div className="max-w-[1280px] mx-auto px-4 md:px-6 mt-10">
      <div className="grid md:grid-cols-4 gap-3">
        {badges.map(b=>(
          <div key={b.title} className="bg-white rounded-[20px] border p-5 flex gap-4">
            <div className="w-12 h-12 rounded-full bg-[#a3ff12] flex items-center justify-center shrink-0"><b.icon size={20} /></div>
            <div><div className="font-bold text-[14px]">{b.title}</div><div className="text-[12px] text-zinc-500 mt-1 leading-snug">{b.desc}</div></div>
          </div>
        ))}
      </div>
      <div className="mt-4 bg-black text-white rounded-[20px] p-4 flex flex-wrap items-center justify-center gap-6 text-[11px] tracking-wide">
        <span className="flex items-center gap-2"><Lock size={14}/> 256-bit SSL SECURE</span>
        <span>•</span><span>PAYPAL VERIFIED SELLER</span><span>•</span><span>4.8/5 TRUSTPILOT (1,248 reviews)</span><span>•</span><span>SHOPIFY SECURE BADGE</span>
      </div>
    </div>
  )
}
