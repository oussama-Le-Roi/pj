import { createContext, useContext, useState, useEffect } from 'react'

const CartContext = createContext(null)
export const useCart = () => useContext(CartContext)

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    try { return JSON.parse(localStorage.getItem('gadgetsn_cart')||'[]') } catch { return [] }
  })
  const [wishlist, setWishlist] = useState(() => {
    try { return JSON.parse(localStorage.getItem('gadgetsn_wishlist')||'[]') } catch { return [] }
  })

  useEffect(()=>{ localStorage.setItem('gadgetsn_cart', JSON.stringify(items)) }, [items])
  useEffect(()=>{ localStorage.setItem('gadgetsn_wishlist', JSON.stringify(wishlist)) }, [wishlist])

  const addToCart = (product, variantIndex=0, qty=1) => {
    setItems(prev=>{
      const idx = prev.findIndex(p=>p.id===product.id && p.variantIndex===variantIndex)
      if(idx>=0){ const copy=[...prev]; copy[idx].qty+=qty; return copy }
      return [...prev, { id: product.id, title: product.title, price: product.variants?.[variantIndex]?.price || product.price, image: product.images[0], variantIndex, variantTitle: product.variants?.[variantIndex]?.title||'Default', qty }]
    })
  }
  const removeFromCart = (id, vIdx) => setItems(prev=>prev.filter(p=>!(p.id===id && p.variantIndex===vIdx)))
  const updateQty = (id, vIdx, qty) => {
    if(qty<=0) return removeFromCart(id, vIdx)
    setItems(prev=>prev.map(p=>p.id===id&&p.variantIndex===vIdx?{...p, qty}:p))
  }
  const clearCart = () => setItems([])
  const total = items.reduce((s,p)=>s+p.price*p.qty,0)
  const count = items.reduce((s,p)=>s+p.qty,0)

  const toggleWishlist = (product) => {
    setWishlist(prev=> prev.includes(product.id) ? prev.filter(id=>id!==product.id) : [...prev, product.id])
  }

  return <CartContext.Provider value={{ items, addToCart, removeFromCart, updateQty, clearCart, total, count, wishlist, toggleWishlist }}>{children}</CartContext.Provider>
}
