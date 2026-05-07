export type UserRecord = {
  id: string
  name: string
  role: string
  email: string
  status: 'Active' | 'Pending' | 'Suspended'
}

export type OrderRecord = {
  id: string
  customer: string
  amount: number
  status: 'Paid' | 'Processing' | 'Refunded'
  createdAt: string
}

export const dashboardStats = {
  activeUsers: 18542,
  ordersToday: 469,
  conversionRate: 4.73,
  revenue: 126500,
}

export const users: UserRecord[] = [
  { id: 'USR-1001', name: 'Luna Wong', role: 'Admin', email: 'luna@demo.com', status: 'Active' },
  { id: 'USR-1002', name: 'Milo Tan', role: 'Editor', email: 'milo@demo.com', status: 'Pending' },
  { id: 'USR-1003', name: 'Ava Lee', role: 'Operator', email: 'ava@demo.com', status: 'Suspended' },
  { id: 'USR-1004', name: 'Ryan Yang', role: 'Admin', email: 'ryan@demo.com', status: 'Active' },
]

export const orders: OrderRecord[] = [
  { id: 'ORD-20260508-01', customer: 'Luna Wong', amount: 1880, status: 'Paid', createdAt: '2026-05-08 09:00' },
  { id: 'ORD-20260508-02', customer: 'Milo Tan', amount: 320, status: 'Processing', createdAt: '2026-05-08 10:12' },
  { id: 'ORD-20260508-03', customer: 'Ava Lee', amount: 760, status: 'Refunded', createdAt: '2026-05-08 10:57' },
]

export const mediaAssets = [
  { id: 'MED-001', name: 'hero-banner.jpg', type: 'Image', size: '2.3MB', updatedAt: '2026-05-08' },
  { id: 'MED-002', name: 'product-video.mp4', type: 'Video', size: '42.1MB', updatedAt: '2026-05-07' },
  { id: 'MED-003', name: 'brand-guide.pdf', type: 'Document', size: '5.5MB', updatedAt: '2026-05-01' },
]
