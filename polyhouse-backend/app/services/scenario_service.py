from app.core.db import get_pool

from app.simulation.templates import (
    WATER_SAVING,
    BALANCED,
    GROWTH_PRIORITY,
)

from app.services.state_service import (
    get_current_state,
    update_state,
)

from app.services.actuator_service import set_actuators


async def apply_strategy(req):

    templates = {
        WATER_SAVING["name"]: WATER_SAVING,
        BALANCED["name"]: BALANCED,
        GROWTH_PRIORITY["name"]: GROWTH_PRIORITY,
    }

    strategy = templates.get(req.strategy)

    if strategy is None:
        return {
            "success": False,
            "message": "Strategy not found."
        }

    # ------------------------------------
    # Get current digital twin state
    # ------------------------------------

    state = await get_current_state(str(req.polyhouse_id))

    # ------------------------------------
    # Simulate strategy effect
    # ------------------------------------

    state["water_level"] -= 3 * strategy["pump_factor"]
    state["water_level"] = max(0, min(100, state["water_level"]))

    state["soil_moisture"] += strategy["pump_factor"] * 2
    state["soil_moisture"] -= 1
    state["soil_moisture"] = max(0, min(100, state["soil_moisture"]))

    state["temp"] += strategy["light_factor"] * 0.3
    state["temp"] -= strategy["fan_factor"] * 0.4
    state["temp"] = max(15, min(45, state["temp"]))

    state["humidity"] += strategy["mist_factor"] * 2
    state["humidity"] -= strategy["fan_factor"]
    state["humidity"] = max(0, min(100, state["humidity"]))

    # ------------------------------------
    # Save updated twin state
    # ------------------------------------

    await update_state(
        str(req.polyhouse_id),
        state,
    )

    # ------------------------------------
    # Convert strategy into actuator %
    # ------------------------------------

    commands = {
        "pump": int(strategy["pump_factor"] * 100),
        "mist": int(strategy["mist_factor"] * 100),
        "fan": int(strategy["fan_factor"] * 100),
        "light": int(strategy["light_factor"] * 100),
    }

    # ------------------------------------
    # Save actuator values
    # ------------------------------------

    await set_actuators(
        str(req.polyhouse_id),
        commands,
    )

    # ------------------------------------
    # Switch controller to AI mode
    # ------------------------------------
    '''
    pool = get_pool()

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE actuator_mode
            SET mode = 'AI'
            WHERE polyhouse_id = $1
            """,
            req.polyhouse_id,
        )'''

    # ------------------------------------
    # Response
    # ------------------------------------

    return {
        "success": True,
        "strategy": req.strategy,
        "commands": commands,
        "updated_state": state,
        "mode": "AI",
    }