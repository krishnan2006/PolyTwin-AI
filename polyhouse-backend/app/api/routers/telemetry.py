from datetime import datetime, timedelta

from fastapi import APIRouter

from app.core.db import get_pool
from app.services.state_service import get_current_state

router = APIRouter()


@router.get("/twin/{polyhouse_id}/state")
async def current_state(polyhouse_id: str):
    """
    Returns the latest value for each sensor in the polyhouse.
    """

    return await get_current_state(polyhouse_id)


@router.get("/telemetry/{polyhouse_id}")
async def telemetry(
    polyhouse_id: str,
    hours: int = 1,
):
    """
    Returns historical telemetry for the specified time range.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                time,
                sensor_type,
                value,
                unit
            FROM sensor_reading
            WHERE
                polyhouse_id = $1
                AND time > $2
            ORDER BY time ASC
            """,
            polyhouse_id,
            datetime.utcnow() - timedelta(hours=hours),
        )

    return [
        {
            "time": row["time"],
            "sensor": row["sensor_type"],
            "value": row["value"],
            "unit": row["unit"],
        }
        for row in rows
    ]