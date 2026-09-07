"""FastAPI application entry point.

Run with:  uvicorn app.main:app --reload
Docs:      http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (import registers all models on Base.metadata)
from app.core.config import get_settings
from app.modules.auth.routes import router as auth_router
from app.modules.farmer.routes import profile_router as farmer_profile_router
from app.modules.farmer.routes import verification_router as verification_router
from app.modules.farmer.shipments_routes import router as farmer_shipments_router
from app.modules.admin.routes import router as admin_router
from app.modules.admin.dispute_routes import router as admin_dispute_router
from app.modules.admin.monitoring_routes import router as admin_monitoring_router
from app.modules.produce.routes import router as produce_router
from app.modules.orders.routes import router as orders_router
from app.modules.consumer.routes import router as consumer_router
from app.modules.consumer.marketplace_routes import router as marketplace_router
from app.modules.consumer.tracking_routes import router as tracking_router
from app.modules.consumer.dispute_routes import router as consumer_dispute_router
from app.modules.buyer.routes import router as buyer_router
from app.modules.financier.routes import router as financier_router
from app.modules.finance.router import router as finance_router
from app.modules.logistics.routes import router as logistics_router
from app.modules.forecast.routes import router as forecast_router
from app.modules.suggestion.routes import router as suggestion_router
from app.modules.market_prices.routes import router as market_prices_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    yield


app = FastAPI(
    title="SIH26033 Backend",
    description=(
        "Integrated agricultural marketplace API with shared authentication, "
        "role-based access, produce, orders, finance, logistics, forecasting, "
        "administration, and CEDA Agmarknet market-price references."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(farmer_profile_router)
app.include_router(verification_router)
app.include_router(farmer_shipments_router)
app.include_router(admin_router)
app.include_router(produce_router)
app.include_router(orders_router)
app.include_router(consumer_router)
app.include_router(marketplace_router)
app.include_router(tracking_router)
app.include_router(consumer_dispute_router)
app.include_router(admin_dispute_router)
app.include_router(admin_monitoring_router)
app.include_router(buyer_router)
app.include_router(financier_router)
app.include_router(finance_router)
app.include_router(logistics_router)
app.include_router(forecast_router)
app.include_router(suggestion_router)
app.include_router(market_prices_router)


@app.get("/", tags=["meta"], summary="Health check")
def root() -> dict:
    return {"message": "SIH26033 backend is running", "docs": "/docs"}
