export const reviewsMock = [
  { id: 1, productId: "mini-retro-white-noise-bluetooth-speaker", user: "Sarah L.", avatar: "SL", rating: 5, verified: true, date: "2024-12-10", comment: "This gadget is so handy and works flawlessly. It's well-designed, reliable, and perfect for everyday use. Highly recommend!", image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", helpful: 24, purchaseDate: "2024-11-28" },
  { id: 2, productId: "mini-retro-white-noise-bluetooth-speaker", user: "Daniel M.", avatar: "DM", rating: 5, verified: true, date: "2024-11-22", comment: "I'm amazed by the quality and performance. Easy to use, stylish, delivers exactly what I needed. Great addition to my tech collection.", image: "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400", helpful: 18, purchaseDate: "2024-11-05" },
  { id: 3, productId: "mini-retro-white-noise-bluetooth-speaker", user: "Emily R.", avatar: "ER", rating: 5, verified: true, date: "2024-11-15", comment: "Worth every penny. Features are impressive, built to last. I use it every day!", helpful: 32, purchaseDate: "2024-10-29" },
  { id: 4, productId: "smart-led-strip-lights", user: "Alex K.", avatar: "AK", rating: 4, verified: true, date: "2024-12-01", comment: "Color quality amazing, app could be better but overall love it.", image: "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=400", helpful: 11, purchaseDate: "2024-11-20" }
]

export const generateCanReview = (userId, productId, orders) => {
  // user can review only if purchased and delivered
  return orders.some(o => o.status === 'delivered' && o.items.some(i => i.id === productId) && o.userId === userId)
}
