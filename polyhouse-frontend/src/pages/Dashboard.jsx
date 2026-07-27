import { useEffect, useState } from "react";
import api from "../services/api";

import SensorCard from "../components/SensorCard";
import ScenarioForm from "../components/ScenarioForm";
import StrategyList from "../components/StrategyList";

import "./Dashboard.css";

const POLYHOUSE_ID = "7eea3fb5-97fa-4f68-9fce-3549a888c092";

function riskClass(risk) {
  const r = String(risk || "").toLowerCase();
  if (r.includes("low")) return "risk-low";
  if (r.includes("high")) return "risk-high";
  if (r.includes("med")) return "risk-medium";
  return "";
}

export default function Dashboard() {
  const [state, setState] = useState({});
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  async function loadState() {
    try {
      const res = await api.get(`/twin/${POLYHOUSE_ID}/state`);
      setState(res.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error(err);
    }
  }

  async function simulate(data) {
    setLoading(true);

    try {
      const res = await api.post("/simulate", data);
      setSimulation(res.data);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  }
  async function applyStrategy(strategy){

    try{

        const res = await api.post(

            "/scenario/apply",

            {

                polyhouse_id:POLYHOUSE_ID,

                strategy:strategy.name

            }

        )

        console.log(res.data)

        alert("Strategy Applied")

    }

    catch(err){

        console.error(err)

    }

}

  useEffect(() => {
    loadState();
    const timer = setInterval(loadState, 5000);
    return () => clearInterval(timer);
  }, []);

  const rec = simulation?.recommended_strategy;

  return (
    <div className="dash">
      <header className="dash__header">
        <div className="dash__titleBlock">
          <span className="dash__eyebrow">Digital Twin</span>
          <h1 className="dash__title">🌱 Smart Polyhouse</h1>
        </div>

        <div className="dash__status">
          <span className="dash__pulse" aria-hidden="true" />
          <span>
            Live
            {lastUpdated
              ? ` · updated ${lastUpdated.toLocaleTimeString()}`
              : " · connecting…"}
          </span>
        </div>
      </header>

      <section className="dash__section" aria-label="Live sensor readings">
        <h2 className="dash__sectionLabel">Live Sensor Data</h2>

        <div className="dash__sensorGrid">
          <SensorCard
            title="🌡 Temperature"
            value={
              state.temp !== undefined ? Number(state.temp).toFixed(1) : "--"
            }
            unit="°C"
          />

          <SensorCard
            title="💧 Humidity"
            value={
              state.humidity !== undefined
                ? Number(state.humidity).toFixed(1)
                : "--"
            }
            unit="%"
          />

          <SensorCard
            title="🌱 Soil Moisture"
            value={
              state.soil_moisture !== undefined
                ? Number(state.soil_moisture).toFixed(1)
                : "--"
            }
            unit="%"
          />

          <SensorCard
            title="☀ Light"
            value={state.light !== undefined ? Math.round(state.light) : "--"}
            unit="Lux"
          />

          <SensorCard
            title="🚰 Water Tank"
            value={
              state.water_level !== undefined
                ? Number(state.water_level).toFixed(1)
                : "--"
            }
            unit="%"
          />
        </div>
      </section>

      <div className="dash__vein" aria-hidden="true">
        <svg viewBox="0 0 1200 24" preserveAspectRatio="none">
          <path d="M0 12 H1200" />
          <path d="M100 12 L120 4 M300 12 L320 20 M500 12 L520 4 M700 12 L720 20 M900 12 L920 4 M1100 12 L1120 20" />
        </svg>
      </div>

      <section className="dash__section">
        <h2 className="dash__sectionLabel">Run a Scenario</h2>
        <div className="dash__card">
          <ScenarioForm onSimulate={simulate} />
        </div>
      </section>

      {loading && (
        <div className="dash__loading" role="status">
          <span className="dash__spinner" aria-hidden="true" />
          Running simulation…
        </div>
      )}

      {simulation && rec && (
        <section className="dash__section dash__results">
          <div className="dash__strategyHero">
            <div className="dash__strategyHeroHead">
              <span className="dash__eyebrow">🏆 Recommended Strategy</span>
              <h2 className="dash__strategyName">{rec.name}</h2>
              <p className="dash__strategyDesc">{rec.description}</p>
            </div>

            <div className="dash__statGrid">
              <div className="dash__stat">
                <span className="dash__statLabel">🌱 Growth</span>
                <span className="dash__statValue">
                  {rec.expected.growth.toFixed(1)}%
                </span>
              </div>

              <div className="dash__stat">
                <span className="dash__statLabel">💧 Water Remaining</span>
                <span className="dash__statValue">
                  {rec.expected.water_remaining.toFixed(1)}%
                </span>
              </div>

              <div className="dash__stat">
                <span className="dash__statLabel">⚡ Energy</span>
                <span className="dash__statValue">
                  {rec.expected.energy.toFixed(1)}
                </span>
              </div>

              <div className="dash__stat">
                <span className="dash__statLabel">⚠ Risk</span>
                <span className={`dash__badge ${riskClass(rec.expected.risk)}`}>
                  {rec.expected.risk}
                </span>
              </div>

              <div className="dash__stat">
                <span className="dash__statLabel">⭐ Score</span>
                <span className="dash__statValue dash__statValue--accent">
                  {rec.score.toFixed(2)}
                </span>
              </div>
            </div>

            <button
              onClick={() => applyStrategy(rec)}
              className="dash__applyBtn"
            >
              Apply Strategy
            </button>
          </div>

          <div className="dash__strategyList">
            <h3 className="dash__sectionLabel dash__sectionLabel--sub">
              Other Strategies
            </h3>
            <StrategyList strategies={simulation.strategies} onApply={applyStrategy} />
          </div>

          <div className="dash__timeline">
            <h3 className="dash__sectionLabel dash__sectionLabel--sub">
              📅 Simulation Timeline
            </h3>

            <div className="dash__tableWrap">
              <table className="dash__table">
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Water</th>
                    <th>Soil</th>
                    <th>Temp</th>
                    <th>Humidity</th>
                    <th>Growth</th>
                    <th>Risk</th>
                  </tr>
                </thead>

                <tbody>
                  {rec.timeline.map((day) => (
                    <tr key={day.day}>
                      <td className="dash__mono">{day.day}</td>
                      <td className="dash__mono">
                        {day.water_level.toFixed(1)}
                      </td>
                      <td className="dash__mono">
                        {day.soil_moisture.toFixed(1)}
                      </td>
                      <td className="dash__mono">
                        {day.temperature.toFixed(1)}
                      </td>
                      <td className="dash__mono">{day.humidity.toFixed(1)}</td>
                      <td className="dash__mono">{day.growth.toFixed(1)}</td>
                      <td>
                        <span className={`dash__badge ${riskClass(day.risk)}`}>
                          {day.risk}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
