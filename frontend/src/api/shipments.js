import { apiRequest } from "./client";

export const listFarmerShipments = () => apiRequest("/api/farmer/shipments");
export const listConsumerShipments = () => apiRequest("/api/consumer/shipments");
export const getFarmerShipment = (id) => apiRequest(`/api/farmer/shipments/${id}`);
export const getConsumerShipment = (id) => apiRequest(`/api/consumer/shipments/${id}`);
