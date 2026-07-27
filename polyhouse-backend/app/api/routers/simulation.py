from fastapi import APIRouter

from app.simulation.engine import simulate
from app.services.state_service import get_current_state

router = APIRouter(
    prefix="/api/v1",
    tags=["Simulation"]
)


@router.post("/simulate")
async def run_simulation(payload: dict):
    """
    Runs a simulation based on the current polyhouse state
    and the user-provided scenario.
    """

    current_state = await get_current_state(
        payload["polyhouse_id"]
    )

    strategies = simulate(
        current_state=current_state,
        scenario=payload
    )

    return {
        "success": True,
        "current_state": current_state,
        "scenario": payload,
        "recommended_strategy": strategies[0] if strategies else None,
        "strategies": strategies
    }