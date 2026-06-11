from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Nyx Integration"])

# --- Pydantic Models for Type Safety ---
class NyxMetrics(BaseModel):
    estimated_co2_impact_g: float
    energy_usage_kwh: float
    emissions_saved_g: float

class NyxInsights(BaseModel):
    status_level: str
    quick_tip: str

class NyxData(BaseModel):
    sustainability_score: int
    metrics: NyxMetrics
    insights: NyxInsights

class NyxResponse(BaseModel):
    status: str
    data: NyxData

# --- The Live Endpoint ---
@router.get("/api/v1/nyx/metrics", response_model=NyxResponse)
async def get_nyx_metrics():
    # V1: Returning static baseline metrics for dashboard UI mapping.
    return NyxResponse(
        status="success",
        data=NyxData(
            sustainability_score=88,
            metrics=NyxMetrics(
                estimated_co2_impact_g=14.2,
                energy_usage_kwh=0.005,
                emissions_saved_g=6.8
            ),
            insights=NyxInsights(
                status_level="Excellent",
                quick_tip="Blocking background trackers reduces data transfer, saving additional server energy."
            )
        )
    )
