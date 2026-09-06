from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .service import logistics_service

router = APIRouter(prefix="/api/logistics", tags=["Logistics"])


class RouteOptimizeRequest(BaseModel):
    distance_matrix: list[list[int]]
    start_index: int = 0


class RouteOptimizeResponse(BaseModel):
    route: list[int]
    total_distance: int


@router.post("/routes/optimize", response_model=RouteOptimizeResponse)
def optimize_route(request: RouteOptimizeRequest):
    try:
        return logistics_service.optimize_route(
            distance_matrix=request.distance_matrix,
            start_index=request.start_index,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))