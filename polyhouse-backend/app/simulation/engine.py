from app.simulation.templates import (
    WATER_SAVING,
    BALANCED,
    GROWTH_PRIORITY,
)

# -----------------------------
# Simulation Constants
# -----------------------------

BASE_DAILY_WATER_USE = 3
SOIL_DRYING_PER_DAY = 1

LIGHT_HEAT_GAIN = 0.3
FAN_COOLING = 0.4

MIST_HUMIDITY_GAIN = 2
FAN_HUMIDITY_LOSS = 1

IDEAL_TEMPERATURE = 28


def simulate(current_state: dict, scenario: dict):

    strategies = generate_strategies(current_state, scenario)

    evaluated = []

    for strategy in strategies:
        evaluated.append(
            evaluate_strategy(
                strategy.copy(),
                current_state.copy(),
                scenario,
            )
        )

    ranked = rank_strategies(evaluated, scenario)

    return ranked


def generate_strategies(current_state: dict, scenario: dict):

    crisis = scenario.get("crisis")

    if crisis == "water_shortage":
        return [
            WATER_SAVING.copy(),
            BALANCED.copy(),
            GROWTH_PRIORITY.copy(),
        ]

    return []


def evaluate_strategy(strategy, current_state, scenario):

    state = current_state.copy()

    days = scenario.get("duration", 1)

    timeline = []

    pump = strategy["pump_factor"]
    fan = strategy["fan_factor"]
    mist = strategy["mist_factor"]
    light = strategy["light_factor"]

    for day in range(1, days + 1):

        # -------------------------
        # Water
        # -------------------------

        state["water_level"] -= BASE_DAILY_WATER_USE * pump
        state["water_level"] = max(0, min(100, state["water_level"]))

        # -------------------------
        # Soil
        # -------------------------

        state["soil_moisture"] += pump * 2
        state["soil_moisture"] -= SOIL_DRYING_PER_DAY
        state["soil_moisture"] = max(0, min(100, state["soil_moisture"]))

        # -------------------------
        # Temperature
        # -------------------------

        state["temp"] += light * LIGHT_HEAT_GAIN
        state["temp"] -= fan * FAN_COOLING

        # -------------------------
        # Humidity
        # -------------------------

        state["humidity"] += mist * MIST_HUMIDITY_GAIN
        state["humidity"] -= fan * FAN_HUMIDITY_LOSS
        state["humidity"] = max(0, min(100, state["humidity"]))

        # -------------------------
        # Temperature Score
        # -------------------------

        temp_score = max(
            0,
            100 - abs(state["temp"] - IDEAL_TEMPERATURE) * 5,
        )

        # -------------------------
        # Growth
        # -------------------------

        growth = (
            state["soil_moisture"] * 0.4
            + state["water_level"] * 0.3
            + temp_score * 0.3
        )

        growth = max(0, min(100, growth))

        # -------------------------
        # Risk
        # -------------------------
        '''
        risk = 0

        if state["water_level"] < 20:
            risk += 30

        if state["soil_moisture"] < 30:
            risk += 30

        if state["temp"] > 35:
            risk += 20

        if growth < 70:
            risk += 20

        risk = min(100, risk)
        '''
        risk = 0

        # Water (0–35)

        risk += max(0, (50 - state["water_level"])) * 0.7

        # Soil (0–30)

        risk += max(0, (45 - state["soil_moisture"])) * 0.6

        # Temperature (0–20)

        risk += max(0, state["temp"] - 30) * 4

        # Growth (0–15)

        risk += max(0, 80 - growth) * 0.3

        risk = round(min(100, risk))
        # -------------------------
        # Timeline
        # -------------------------

        timeline.append(
            {
                "day": day,
                "water_level": round(state["water_level"], 2),
                "soil_moisture": round(state["soil_moisture"], 2),
                "temperature": round(state["temp"], 2),
                "humidity": round(state["humidity"], 2),
                "growth": round(growth, 2),
                "risk": risk,
            }
        )

    # -------------------------
    # Energy
    # -------------------------

    energy = (
        pump * 30
        + fan * 25
        + mist * 15
        + light * 30
    )

    strategy["expected"] = {
        "growth": round(growth, 2),
        "water_remaining": round(state["water_level"], 2),
        "soil_moisture": round(state["soil_moisture"], 2),
        "energy": round(energy, 2),
        "risk": risk,
    }

    strategy["timeline"] = timeline

    return strategy


def rank_strategies(strategies, scenario):

    goal = scenario.get("goal", "maximize_growth")

    for strategy in strategies:

        expected = strategy["expected"]

        if goal == "maximize_growth":

            score = (
                expected["growth"]
                - (100 - expected["water_remaining"]) * 0.4
                - expected["energy"] * 0.2
                - expected["risk"] * 0.5
            )

        elif goal == "save_water":

            score = (
                expected["water_remaining"]
                - expected["risk"] * 0.4
                + expected["growth"] * 0.2
            )

        else:

            score = (
                expected["growth"]
                - expected["risk"]
            )

        strategy["score"] = round(score, 2)

    strategies.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return strategies