from app.core.db import get_pool


async def get_current_state(polyhouse_id: str):
    """
    Returns the latest value for each sensor.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DISTINCT ON (sensor_type)
                sensor_type,
                value
            FROM sensor_reading
            WHERE polyhouse_id = $1
            ORDER BY sensor_type, time DESC
            """,
            polyhouse_id,
        )

    return {
        row["sensor_type"]: row["value"]
        for row in rows
    }
from datetime import datetime


async def update_state(polyhouse_id: str, state: dict):

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.transaction():

            for sensor, value in state.items():

                unit = {
                    "temp": "°C",
                    "humidity": "%",
                    "soil_moisture": "%",
                    "water_level": "%",
                    "light": "Lux",
                }.get(sensor, "")

                await conn.execute(
                    """
                    INSERT INTO sensor_reading
                    (
                        time,
                        polyhouse_id,
                        sensor_type,
                        value,
                        unit
                    )
                    VALUES
                    ($1,$2,$3,$4,$5)
                    """,
                    datetime.utcnow(),
                    polyhouse_id,
                    sensor,
                    value,
                    unit,
                )