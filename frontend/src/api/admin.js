import { apiRequest } from "./client";

export const listVerifications = () => apiRequest("/api/admin/verifications");
export const getVerificationDetail = (userId) => apiRequest(`/api/admin/verifications/${userId}`);
export const approveVerification = (userId) => apiRequest(`/api/admin/verifications/${userId}/approve`, { method: "POST" });
export const rejectVerification = (userId, remarks) => apiRequest(`/api/admin/verifications/${userId}/reject`, { method: "POST", body: { remarks } });
export const listDisputes = () => apiRequest("/api/admin/disputes");
export const getDispute = (id) => apiRequest(`/api/admin/disputes/${id}`);
export const resolveDispute = (id, resolution, adminRemarks) => apiRequest(`/api/admin/disputes/${id}/resolve`, { method: "POST", body: { resolution, admin_remarks: adminRemarks } });
export const getMonitoring = () => apiRequest("/api/admin/monitoring");
export const createDispute = (payload) => apiRequest("/api/consumer/disputes", { method: "POST", body: payload });
