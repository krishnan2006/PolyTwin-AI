from app.core.db import get_pool


async def get_actuators(polyhouse_id: str):
    """
    Returns the latest actuator percentages for the polyhouse.
    """

    pool = get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch(
            """
            SELECT actuator, value
            FROM actuator_state
            WHERE polyhouse_id = $1
            """,
            polyhouse_id,
        )

    actuators = {
        "pump": 0,
        "fan": 0,
        "mist": 0,
        "light": 0,
    }

    for row in rows:
        actuators[row["actuator"]] = row["value"]

    return actuators


async def set_actuators(polyhouse_id: str, commands: dict):
    """
    Updates actuator percentages.
    """

    pool = get_pool()

    async with pool.acquire() as conn:

        for actuator, value in commands.items():

            await conn.execute(
                """
                INSERT INTO actuator_state
                (polyhouse_id, actuator, value)

                VALUES ($1, $2, $3)

                ON CONFLICT (polyhouse_id, actuator)

                DO UPDATE
                SET value = EXCLUDED.value
                """,
                polyhouse_id,
                actuator,
                value,
            )