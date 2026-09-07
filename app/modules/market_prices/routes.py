"""Authenticated frontend endpoint for normalized CEDA mandi prices."""

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.enums import Role
from app.models.user import User
from app.modules.auth.dependencies import require_role
from app.modules.market_prices.service import (
    MarketPriceLookupError,
    MarketPriceUpstreamError,
    cached_market_prices,
    fetch_market_prices,
)


router = APIRouter(prefix="/api/market-prices", tags=["market-prices"])


class MarketObservation(BaseModel):
    market: str
    market_id: int
    date: date
    min_price: float
    max_price: float
    modal_price: float


class MarketPriceResponse(BaseModel):
    source: str
    attribution: str
    price_unit: str
    commodity: str
    state: str
    district: str
    latest_observation: date | None
    age_days: int | None
    stale_cache: bool
    markets: list[MarketObservation]


@router.get("", response_model=MarketPriceResponse)
def get_market_prices(
    commodity: Annotated[str, Query(min_length=1, max_length=100)],
    state_name: Annotated[str, Query(alias="state", min_length=1, max_length=100)],
    district: Annotated[str, Query(min_length=1, max_length=100)],
    current_user: Annotated[User, Depends(require_role(Role.FARMER, Role.CONSUMER, Role.BULK_BUYER, Role.ADMIN))],
    market: Annotated[str | None, Query(min_length=1, max_length=150)] = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    """Resolve names to documented CEDA IDs and return price observations."""
    settings = get_settings()
    if not settings.ceda_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market prices unavailable: CEDA_API_KEY is not configured",
        )

    end = to_date or date.today()
    start = from_date or end - timedelta(days=30)
    if start > end:
        raise HTTPException(status_code=422, detail="from_date must be on or before to_date")

    filters = {
        "commodity": commodity,
        "state": state_name,
        "district": district,
        "market": market,
        "from_date": start,
        "to_date": end,
    }
    try:
        return fetch_market_prices(
            api_key=settings.ceda_api_key,
            base_url=settings.ceda_api_base_url,
            **filters,
        )
    except MarketPriceLookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MarketPriceUpstreamError as exc:
        cached = cached_market_prices(**filters)
        if cached:
            return cached
        raise HTTPException(status_code=502, detail="Market prices unavailable from CEDA") from exc
