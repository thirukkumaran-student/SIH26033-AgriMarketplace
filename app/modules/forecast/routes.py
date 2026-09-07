from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.forecast import Forecast
from app.models.user import User
from app.core.enums import Role
from app.modules.auth.dependencies import require_role
from .service import forecast_service


router = APIRouter(
    prefix="/api/forecast",
    tags=["Forecast"],
)


class ForecastRequest(BaseModel):
    crop: str
    district_name: str
    date: str
    lag_1: float = Field(ge=0)
    lag_2: float = Field(ge=0)
    days_since_previous: int = Field(gt=0)


class ForecastResponse(BaseModel):
    crop: str
    district_name: str
    date: str
    predicted_demand: float


class TrainResponse(BaseModel):
    model_name: str
    validation_mae: float
    validation_rmse: float
    test_mae: float
    test_rmse: float
    training_period: str
    test_period: str


@router.post("/train", response_model=TrainResponse)
def train_forecast(current_user: Annotated[User, Depends(require_role(Role.ADMIN))]):
    try:
        result = forecast_service.train()
        return TrainResponse(**result)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/predict", response_model=ForecastResponse)
def predict_forecast(
    request: ForecastRequest,
    current_user: Annotated[User, Depends(require_role(Role.FARMER, Role.BULK_BUYER, Role.ADMIN))],
    db: Session = Depends(get_db),
):
    try:
        prediction = forecast_service.predict(
            crop=request.crop,
            district_name=request.district_name,
            date=request.date,
            lag_1=request.lag_1,
            lag_2=request.lag_2,
            days_since_previous=request.days_since_previous,
        )

        forecast = Forecast(
            crop=request.crop,
            region=request.district_name,
            period=request.date,
            predicted_demand=prediction,
            model_version=forecast_service.model_package["model_name"],
        )

        db.add(forecast)
        db.commit()
        db.refresh(forecast)

        return ForecastResponse(
            crop=request.crop,
            district_name=request.district_name,
            date=request.date,
            predicted_demand=prediction,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/", response_model=list[ForecastResponse])
def get_forecasts(
    current_user: Annotated[User, Depends(require_role(Role.FARMER, Role.BULK_BUYER, Role.ADMIN))],
    db: Session = Depends(get_db),
):
    forecasts = (
        db.query(Forecast)
        .order_by(Forecast.created_at.desc())
        .all()
    )

    return [
        ForecastResponse(
            crop=forecast.crop,
            district_name=forecast.region,
            date=forecast.period,
            predicted_demand=forecast.predicted_demand,
        )
        for forecast in forecasts
    ]
