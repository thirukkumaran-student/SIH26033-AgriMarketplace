class SuggestionService:

    def generate(
        self,
        crop: str,
        district_name: str,
        predicted_demand: float,
        available_quantity: float,
    ) -> dict:

        if predicted_demand <= 0:
            suggestion = "No procurement needed"
            reason = "Predicted demand is zero or negative."

        elif available_quantity < predicted_demand * 0.5:
            suggestion = "Increase procurement"
            reason = "Available quantity is significantly below predicted demand."

        elif available_quantity < predicted_demand:
            suggestion = "Consider additional procurement"
            reason = "Available quantity is below predicted demand."

        elif available_quantity > predicted_demand * 1.5:
            suggestion = "Reduce procurement"
            reason = "Available quantity significantly exceeds predicted demand."

        else:
            suggestion = "Maintain current procurement"
            reason = "Available quantity is reasonably aligned with predicted demand."

        return {
            "crop": crop,
            "district_name": district_name,
            "predicted_demand": predicted_demand,
            "available_quantity": available_quantity,
            "suggestion": suggestion,
            "reason": reason,
        }


suggestion_service = SuggestionService()