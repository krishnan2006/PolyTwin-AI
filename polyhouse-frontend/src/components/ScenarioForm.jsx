import { useState } from "react";

export default function ScenarioForm({ onSimulate }) {
    const [scenario, setScenario] = useState("water_shortage");
    const [days, setDays] = useState(10);
    const [goal, setGoal] = useState("balanced");

    async function handleSubmit(e) {
        e.preventDefault();

        onSimulate({
            polyhouse_id: "7eea3fb5-97fa-4f68-9fce-3549a888c092",
            crisis: scenario,
            duration: Number(days),
            goal: goal,
        });
    }

    return (
        <form className="scenarioForm" onSubmit={handleSubmit}>
            <div className="scenarioForm__grid">
                <div className="scenarioForm__field">
                    <label htmlFor="scenario">Scenario</label>
                    <select
                        id="scenario"
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                    >
                        <option value="water_shortage">Water Shortage</option>
                        <option value="heat_wave">Heat Wave</option>
                        <option value="heavy_rain">Heavy Rain</option>
                        <option value="power_failure">Power Failure</option>
                    </select>
                </div>

                <div className="scenarioForm__field">
                    <label htmlFor="days">Duration (days)</label>
                    <input
                        id="days"
                        type="number"
                        value={days}
                        min={1}
                        max={30}
                        onChange={(e) => setDays(e.target.value)}
                    />
                </div>

                <div className="scenarioForm__field">
                    <label htmlFor="goal">Goal</label>
                    <select
                        id="goal"
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                    >
                        <option value="balanced">Balanced</option>
                        <option value="save_water">Save Water</option>
                        <option value="maximize_growth">Maximize Growth</option>
                        <option value="lowest_risk">Lowest Risk</option>
                    </select>
                </div>
            </div>

            <button type="submit" className="scenarioForm__submit">
                🚀 Run Simulation
            </button>
        </form>
    );
}
