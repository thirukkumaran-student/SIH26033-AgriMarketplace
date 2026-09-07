import { apiRequest, toQuery } from "./client";

export const getMarketPrices = (filters) => apiRequest(`/api/market-prices${toQuery(filters)}`);
