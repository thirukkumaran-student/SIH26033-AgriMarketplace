from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.modules.forecast.service import forecast_service
from app.models.user import User
from app.core.enums import Role
from app.modules.auth.dependencies import require_role
from .service import suggestion_service


router = APIRouter(
    prefix="/api/suggestions",
    tags=["Suggestions"],
)


class SuggestionRequest(BaseModel):
    crop: str
    district_name: str
    date: str
    lag_1: float = Field(ge=0)
    lag_2: float = Field(ge=0)
    days_since_previous: int = Field(gt=0)
    available_quantity: float = Field(ge=0)


class SuggestionResponse(BaseModel):
    crop: str
    district_name: str
    predicted_demand: float
    available_quantity: float
    suggestion: str
    reason: str


@router.post("/", response_model=SuggestionResponse)
def generate_suggestion(
    request: SuggestionRequest,
    current_user: Annotated[User, Depends(require_role(Role.FARMER, Role.BULK_BUYER, Role.ADMIN))],
):

    predicted_demand = forecast_service.predict(
        crop=request.crop,
        district_name=request.district_name,
        date=request.date,
        lag_1=request.lag_1,
        lag_2=request.lag_2,
        days_since_previous=request.days_since_previous,
    )

    return suggestion_service.generate(
        crop=request.crop,
        district_name=request.district_name,
        predicted_demand=predicted_demand,
        available_quantity=request.available_quantity,
    )
