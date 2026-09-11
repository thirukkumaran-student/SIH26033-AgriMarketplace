import { apiRequest } from "./client";

const PROFILE_PREFIX = {
  FARMER: "/api/farmer",
  CONSUMER: "/api/consumer",
  BULK_BUYER: "/api/buyer",
  FINANCIER: "/api/financier",
};

export function getProfile(role) {
  return apiRequest(`${PROFILE_PREFIX[role]}/profile`);
}

export function createProfile(role, payload) {
  return apiRequest(`${PROFILE_PREFIX[role]}/profile`, { method: "POST", body: payload });
}

export function updateProfile(role, payload) {
  return apiRequest(`${PROFILE_PREFIX[role]}/profile`, { method: "PUT", body: payload });
}

export const getVerification = () => apiRequest("/api/verification/status");
export const submitVerification = (payload) => apiRequest("/api/verification/documents", { method: "POST", body: payload });
