import { Star, BadgeCheck, Image as ImageIcon, ThumbsUp } from 'lucide-react'
import { useState } from 'react'

export default function ReviewSection({ productId, reviews, canReview, onSubmitReview }) {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ rating:5, comment:"", image:null, imagePreview:null })
  const productReviews = reviews.filter(r=>r.productId===productId)
  const avg = productReviews.length ? (productReviews.reduce((s,r)=>s+r.rating,0)/productReviews.length).toFixed(1) : 0

  const handleImage = (e)=>{
    const file = e.target.files[0]
    if(file){
      const reader = new FileReader()
      reader.onload = (ev)=> setForm({...form, image: file, imagePreview: ev.target.result})
      reader.readAsDataURL(file)
    }
  }

  const submit = ()=>{
    if(!form.comment.trim()) { alert("Please write a review"); return }
    onSubmitReview({ productId, rating: form.rating, comment: form.comment, image: form.imagePreview })
    setShowForm(false)
    setForm({ rating:5, comment:"", image:null, imagePreview:null })
  }

  return (
    <div className="bg-white rounded-[24px] border p-6 md:p-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-[22px] font-bold">Customer Reviews</h3>
          <div className="flex items-center gap-3 mt-2">
            <div className="flex items-center gap-1 bg-black text-white px-3 py-1 rounded-full text-sm font-bold"><Star size={14} fill="white"/> {avg}</div>
            <span className="text-sm opacity-60">{productReviews.length} verified reviews • {productReviews.filter(r=>r.image).length} with photos</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 rounded-full bg-zinc-100 text-sm">With Photos ({productReviews.filter(r=>r.image).length})</button>
          <button className="px-4 py-2 rounded-full bg-zinc-100 text-sm">Verified Only</button>
        </div>
      </div>

      <div className="mt-6 grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-4">
          {productReviews.map(r=>(
            <div key={r.id} className="border-b pb-5">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-black text-white flex items-center justify-center text-xs font-bold">{r.avatar}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2"><b className="text-sm">{r.user}</b> {r.verified && <span className="flex items-center gap-1 bg-green-50 text-green-700 text-[10px] px-2 py-0.5 rounded-full"><BadgeCheck size={10}/> VERIFIED PURCHASE</span>}</div>
                  <div className="flex items-center gap-1 mt-1">{[...Array(5)].map((_,i)=><Star key={i} size={12} fill={i<r.rating?'black':''} stroke={i<r.rating?'black':'#ddd'} />)} <span className="text-[11px] opacity-50 ml-2">{r.date} • Bought on {r.purchaseDate}</span></div>
                </div>
              </div>
              <p className="mt-3 text-[14px] leading-relaxed">{r.comment}</p>
              {r.image && <img src={r.image} alt="review" className="mt-3 w-[120px] h-[120px] object-cover rounded-xl border" />}
              <div className="mt-2 flex items-center gap-2 text-[12px] opacity-60"><ThumbsUp size={12}/> Helpful ({r.helpful})</div>
            </div>
          ))}
          {productReviews.length===0 && <div className="text-center py-10 opacity-50">No reviews yet. Be first to review!</div>}
        </div>

        <div className="bg-zinc-50 rounded-[20px] p-5 h-fit">
          <h4 className="font-bold">Review this product</h4>
          <p className="text-xs opacity-60 mt-1">Share your experience with other customers. Only verified buyers can review.</p>
          {!canReview ? (
            <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-xl text-[12px] text-orange-800">You can only review products you have purchased and received. Buy this item and you'll be invited via email to share a photo review — like AliExpress!</div>
          ) : (
            <>
              {!showForm ? <button onClick={()=>setShowForm(true)} className="mt-4 w-full bg-black text-white py-3 rounded-full font-semibold text-sm">Write a review + Get 10% OFF next order</button> :
                <div className="mt-4 space-y-3">
                  <div className="flex gap-1">{[1,2,3,4,5].map(n=><button key={n} onClick={()=>setForm({...form, rating:n})}><Star size={24} fill={n<=form.rating?'black':'none'} /></button>)}</div>
                  <textarea value={form.comment} onChange={e=>setForm({...form, comment:e.target.value})} placeholder="How was the product? Quality? Shipping? Add photo of your received item..." className="w-full border rounded-xl p-3 text-sm min-h-[90px]" />
                  <label className="flex items-center gap-2 text-sm border border-dashed rounded-xl p-3 justify-center cursor-pointer hover:bg-white"><ImageIcon size={16}/> {form.imagePreview ? "Change photo" : "Add photo of delivered product (optional)"}<input type="file" accept="image/*" className="hidden" onChange={handleImage} /></label>
                  {form.imagePreview && <img src={form.imagePreview} alt="preview" className="w-full h-[150px] object-cover rounded-xl" />}
                  <div className="text-[11px] opacity-60">Your photo helps others trust our store. Not mandatory, but you get bonus points!</div>
                  <div className="flex gap-2"><button onClick={submit} className="flex-1 bg-black text-white py-2.5 rounded-full text-sm font-semibold">Submit review</button><button onClick={()=>setShowForm(false)} className="px-4 py-2.5 rounded-full bg-zinc-200 text-sm">Cancel</button></div>
                </div>
              }
            </>
          )}
          <div className="mt-6 text-[11px] opacity-60">🎁 Incentive: Get 50 bonus points + 10% discount coupon when you add a photo review after delivery. We will email you 3 days after delivery!</div>
        </div>
      </div>
    </div>
  )
}
