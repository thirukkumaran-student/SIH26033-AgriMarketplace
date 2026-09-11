import { apiRequest } from "./client";

export const reviewOrder = (payload) => apiRequest("/api/orders/review", { method: "POST", body: payload });
export const createOrder = (payload) => apiRequest("/api/orders", { method: "POST", body: payload });
export const listOrders = () => apiRequest("/api/orders");
export const getOrder = (id) => apiRequest(`/api/orders/${id}`);
export const updateOrderStatus = (id, status) => apiRequest(`/api/orders/${id}/status`, { method: "PATCH", body: { status } });
