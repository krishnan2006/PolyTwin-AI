import asyncio
import math
import random
import time
from turtle import mode

import asyncpg
from app.core.config import settings
from app.core.db import create_pool, close_pool
from app.services.actuator_service import get_actuators
# ==========================
# Configuration
# ==========================

POLYHOUSE_ID = "7eea3fb5-97fa-4f68-9fce-3549a888c092"

UPDATE_INTERVAL = 5  # seconds


# ==========================
# Fake Polyhouse
# ==========================

class FakePolyhouse:

    def __init__(self):

        # Sensors

        self.temperature = 27.50
        self.humidity = 51.10
        self.soil_moisture = 45.0
        self.light = 1500.0          # lux
        self.water_level = 50.0       # %

        # Actuators

        self.fan = False
        self.mist = False
        self.pump = False
        self.grow_light = False


        self.ai_override = False
    # ----------------------------------

    def update_environment(
    self,
    dt=5,
    actuators=None,
    ):

        if actuators is None:
            actuators = {}

        hour = (time.time() % 86400) / 3600

        sunlight = max(
            0,
            math.sin((hour - 6) / 12 * math.pi)
        )

        # ---------------------------------------
        # NORMAL MODE
        # ---------------------------------------

        if not self.ai_override:

            pump = 1 if self.soil_moisture < 35 else 0

            fan = 1 if self.temperature > 32 else 0

            mist = 1 if self.humidity < 60 else 0

            light = 1 if sunlight < 0.2 else 0

        # ---------------------------------------
        # AI OVERRIDE
        # ---------------------------------------

        else:

            pump = actuators.get("pump", 0) / 100

            fan = actuators.get("fan", 0) / 100

            mist = actuators.get("mist", 0) / 100

            light = actuators.get("light", 0) / 100

        self.pump = pump
        self.fan = fan
        self.mist = mist
        self.grow_light = light

        # ---------------------------------------
        # LIGHT
        # ---------------------------------------

        self.light = sunlight * 100000
        self.light += light * 20000

        # ---------------------------------------
        # TEMPERATURE
        # ---------------------------------------

        self.temperature += sunlight * dt / 250

        self.temperature -= fan * 0.40 * dt / 60
        self.temperature -= mist * 0.60 * dt / 60
        self.temperature += light * 0.15 * dt / 60

        self.temperature += random.uniform(-0.05, 0.05)

        # ---------------------------------------
        # HUMIDITY
        # ---------------------------------------

        self.humidity -= 0.10 * dt / 60

        self.humidity += mist * 2.5 * dt / 60

        self.humidity -= fan * 0.20 * dt / 60

        # ---------------------------------------
        # SOIL
        # ---------------------------------------

        self.soil_moisture -= 0.08 * dt / 60

        self.soil_moisture += pump * 1.8 * dt / 60

        self.water_level -= pump * 0.4 * dt / 60

        # ---------------------------------------

        self.temperature = max(15, min(45, self.temperature))
        self.humidity = max(25, min(95, self.humidity))
        self.soil_moisture = max(0, min(100, self.soil_moisture))
        self.light = max(0, min(120000, self.light))
        self.water_level = max(0, min(100, self.water_level))

    def sensor_packet(self):

        return [

            ("temp", self.temperature, "C"),

            ("humidity", self.humidity, "%"),

            ("soil_moisture", self.soil_moisture, "%"),

            ("light", self.light, "lux"),

            ("water_level", self.water_level, "%")

        ]

async def log_actuator_event(
    conn,
    polyhouse_id,
    actuator,
    state,
    source="automation",
):
    """
    Log an actuator state change.
    Only called when the actuator actually changes state.
    """

    await conn.execute(
        """
        INSERT INTO actuator_event
        (time, polyhouse_id, actuator, command, source)
        VALUES
        (NOW(), $1, $2, $3, $4)
        """,
        polyhouse_id,
        actuator,
        "ON" if state else "OFF",
        source,
    )
# =======================================
# Main Loop
# =======================================

async def main():

    await create_pool()
    conn = await asyncpg.connect(settings.database_url)

    greenhouse = FakePolyhouse()

    print("=" * 70)
    print(" SMART POLYHOUSE MOCK ESP32 ")
    print("=" * 70)

    previous_states = {
        "fan": greenhouse.fan,
        "mist": greenhouse.mist,
        "pump": greenhouse.pump,
        "grow_light": greenhouse.grow_light,
    }

    try:

        while True:

            actuators = await get_actuators(POLYHOUSE_ID)

            greenhouse.ai_override = any(
                value > 0
                for value in actuators.values()
            )

            greenhouse.update_environment(
                UPDATE_INTERVAL,
                actuators,
            )

            sensors = greenhouse.sensor_packet()

            for sensor_type, value, unit in sensors:

                await conn.execute(
                    """
                    INSERT INTO sensor_reading
                    (time, polyhouse_id, sensor_type, value, unit)
                    VALUES
                    (NOW(), $1, $2, $3, $4)
                    """,
                    POLYHOUSE_ID,
                    sensor_type,
                    value,
                    unit,
                )

            current_states = {
                "fan": greenhouse.fan >= 0.5,
                "mist": greenhouse.mist >= 0.5,
                "pump": greenhouse.pump >= 0.5,
                "grow_light": greenhouse.grow_light >= 0.5,
            }

            for actuator, current_state in current_states.items():

                if previous_states[actuator] != current_state:

                    await log_actuator_event(
                        conn,
                        POLYHOUSE_ID,
                        actuator,
                        current_state,
                    )

            previous_states = current_states.copy()

            mode = "AI STRATEGY" if greenhouse.ai_override else "AUTO"

            print(f"\nMODE : {mode}")
            print(
                f"T={greenhouse.temperature:.2f}°C | "
                f"H={greenhouse.humidity:.2f}% | "
                f"Soil={greenhouse.soil_moisture:.2f}%"
            )

            print(
                f"Light={greenhouse.light:.0f} lux | "
                f"Tank={greenhouse.water_level:.1f}%"
            )

            print(
                f"Pump={greenhouse.pump*100:.0f}% | "
                f"Fan={greenhouse.fan*100:.0f}% | "
                f"Mist={greenhouse.mist*100:.0f}% | "
                f"Light={greenhouse.grow_light*100:.0f}%"
            )

            await asyncio.sleep(UPDATE_INTERVAL)

    finally:

        await conn.close()
        await close_pool()

if __name__ == "__main__":
    asyncio.run(main())