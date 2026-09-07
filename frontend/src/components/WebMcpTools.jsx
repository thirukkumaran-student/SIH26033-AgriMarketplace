import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createOrder, reviewOrder } from "../api/orders";

export default function WebMcpTools({ role }) {
  const navigate = useNavigate();

  useEffect(() => {
    const context = document.modelContext;
    if (!context?.registerTool || !["CONSUMER", "BULK_BUYER"].includes(role)) return undefined;

    const lifecycle = new AbortController();
    const prefix = role === "BULK_BUYER" ? "/app/buyer" : "/app/consumer";
    const tool = {
      name: "place_marketplace_order",
      title: "Place marketplace order",
      description: "Review current backend pricing and place an order for an eligible produce listing for the authenticated buyer.",
      inputSchema: {
        type: "object",
        properties: {
          produceId: { type: "integer", minimum: 1 },
          quantity: { type: "integer", minimum: 1 },
          relationshipId: { type: "integer", minimum: 1, description: "Optional active financing relationship for a bulk buyer." },
        },
        required: ["produceId", "quantity"],
        additionalProperties: false,
      },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      async execute(input) {
        const produceId = Number(input?.produceId);
        const quantity = Number(input?.quantity);
        const relationshipId = input?.relationshipId ? Number(input.relationshipId) : null;
        if (!Number.isInteger(produceId) || produceId < 1 || !Number.isInteger(quantity) || quantity < 1) {
          throw new Error("produceId and quantity must be positive integers");
        }
        const review = await reviewOrder({ produce_id: produceId, quantity });
        const payload = { produce_id: produceId, quantity };
        if (relationshipId) payload.relationship_id = relationshipId;
        const order = await createOrder(payload);
        navigate(`${prefix}/orders`);
        return { orderId: order.id, status: order.status, totalAmount: review.total_amount };
      },
    };

    Promise.resolve(context.registerTool(tool, { signal: lifecycle.signal })).catch(() => {});
    return () => lifecycle.abort();
  }, [navigate, role]);

  return null;
}
