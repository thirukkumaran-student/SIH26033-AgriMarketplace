import { apiRequest, toQuery } from "./client";

export const listProduce = (filters) => apiRequest(`/api/produce${toQuery(filters)}`);
export const getProduce = (id) => apiRequest(`/api/produce/${id}`);
export const createProduce = (payload) => apiRequest("/api/produce", { method: "POST", body: payload });
export const updateProduce = (id, payload) => apiRequest(`/api/produce/${id}`, { method: "PATCH", body: payload });
export const deleteProduce = (id) => apiRequest(`/api/produce/${id}`, { method: "DELETE" });
