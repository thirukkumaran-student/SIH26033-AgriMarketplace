import { apiRequest } from "./client";

export const listLogisticsShipments = () => apiRequest("/api/logistics/shipments");
export const getLogisticsShipment = (id) => apiRequest(`/api/logistics/shipments/${id}`);
export const createShipment = (payload) => apiRequest("/api/logistics/shipments", { method: "POST", body: payload });
export const transitionShipment = (id, action) => apiRequest(`/api/logistics/shipments/${id}/${action}`, { method: "POST" });
export const optimizeRoute = (payload) => apiRequest("/api/logistics/routes/optimize", { method: "POST", body: payload });
export const listHandoffs = (shipmentId) => apiRequest(`/api/logistics/handoff/${shipmentId}`);
export const createHandoff = (shipmentId, payload) => apiRequest(`/api/logistics/handoff/${shipmentId}`, { method: "POST", body: payload });
