import { apiRequest } from "./client";

export const listRelationships = () => apiRequest("/api/finance/relationships/me");
export const listFinanceRequests = () => apiRequest("/api/finance/requests");
export const createFinanceRequest = (financierId) => apiRequest("/api/finance/requests", { method: "POST", body: { financier_id: financierId } });
export const approveFinanceRequest = (id, decision) => apiRequest(`/api/finance/requests/${id}/approve`, { method: "POST", body: decision });
export const rejectFinanceRequest = (id) => apiRequest(`/api/finance/requests/${id}/reject`, { method: "POST" });
export const selectFinanceOffer = (id) => apiRequest(`/api/finance/requests/${id}/select`, { method: "POST" });
export const listFinanciers = () => apiRequest("/api/financier/");
export const listTransactions = (relationshipId) => apiRequest(`/api/finance/transactions?relationship_id=${relationshipId}`);
export const repayTransaction = (id) => apiRequest(`/api/finance/transactions/${id}/repayment`, { method: "POST" });
