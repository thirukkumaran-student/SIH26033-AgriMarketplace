import { apiRequest } from "./client";

export const listForecasts = () => apiRequest("/api/forecast/");
export const predictForecast = (payload) => apiRequest("/api/forecast/predict", { method: "POST", body: payload });
export const getSuggestion = (payload) => apiRequest("/api/suggestions/", { method: "POST", body: payload });
