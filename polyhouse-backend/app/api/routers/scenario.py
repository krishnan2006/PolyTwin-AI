from fastapi import APIRouter

from app.schemas.scenario import ApplyStrategyRequest

from app.services.scenario_service import apply_strategy

router = APIRouter(
    prefix="/scenario",
    tags=["Scenario"],
)
@router.post("/apply")
async def apply(req: ApplyStrategyRequest):

    return await apply_strategy(req)
print("Scenario module loaded")
print(router)