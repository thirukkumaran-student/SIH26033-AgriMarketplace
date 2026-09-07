import { apiRequest, toQuery } from "./client";

export const listMarketplace = (filters) => apiRequest(`/api/marketplace/produce${toQuery(filters)}`);
export const getMarketplaceProduce = (id) => apiRequest(`/api/marketplace/produce/${id}`);
