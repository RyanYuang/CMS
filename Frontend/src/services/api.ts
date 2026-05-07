import { dashboardStats, mediaAssets, orders, users } from '../mocks/data'

const latency = 200

function simulateRequest<T>(data: T): Promise<T> {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(data), latency)
  })
}

export function fetchDashboardStats() {
  return simulateRequest(dashboardStats)
}

export function fetchUsers() {
  return simulateRequest(users)
}

export function fetchOrders() {
  return simulateRequest(orders)
}

export function fetchMediaAssets() {
  return simulateRequest(mediaAssets)
}
