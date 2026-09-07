import { apiRequest } from "./client";

export const loginUser = (credentials) => apiRequest("/api/auth/login", { method: "POST", body: credentials, skipAuth: true });
export const registerUser = (payload) => apiRequest("/api/auth/register", { method: "POST", body: payload, skipAuth: true });
export const getCurrentUser = () => apiRequest("/api/auth/me");
