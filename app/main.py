"""FastAPI application entry point.

Run with:  uvicorn app.main:app --reload
Docs:      http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (import registers all models on Base.metadata)
from app.core.database import Base, engine
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup.

    ``Base.metadata.create_all`` simply creates any tables that do not exist
    yet (the ``users`` table for now). It is idempotent and NEVER drops or
    resets existing tables, so it is safe for the initial prototype.
    Alembic migrations can replace this later without any code changes here.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SIH26033 Backend",
    description=(
        "Shared Authentication + RBAC foundation. One users table for all "
        "roles (FARMER, CONSUMER, BULK_BUYER, FINANCIER, LOGISTICS, ADMIN). "
        "Feature modules (Farmer, Consumer, Marketplace, ...) will be added "
        "on top of this foundation."
    ),
    version="0.1.0",
    lifespan=lifespan,
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

@app.get("/", tags=["meta"], summary="Health check")
def root() -> dict:
    return {"message": "SIH26033 backend is running", "docs": "/docs"}
