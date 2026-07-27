function riskClass(risk) {
    const r = String(risk ?? "").toLowerCase();
    if (r.includes("low")) return "risk-low";
    if (r.includes("high")) return "risk-high";
    if (r.includes("med")) return "risk-medium";
    return "";
}

export default function StrategyList({

    strategies,

    onApply

}){
    if (!strategies || strategies.length === 0) return null;

    return (
        <div className="strategyGrid">
            {strategies.map((s, index) => (
                <div key={index} className="strategyCard">
                    <h4 className="strategyCard__name">{s.name}</h4>

                    <div className="strategyCard__stats">
                        <div className="strategyCard__stat">
                            <span>🌱 Growth</span>
                            <span className="dash__mono">{s.expected.growth.toFixed(1)}</span>
                        </div>
                        <div className="strategyCard__stat">
                            <span>💧 Water</span>
                            <span className="dash__mono">{s.expected.water_remaining.toFixed(1)}</span>
                        </div>
                        <div className="strategyCard__stat">
                            <span>⚠ Risk</span>
                            <span className={`dash__badge ${riskClass(s.risk_score)}`}>
                                {s.expected.risk}
                            </span>
                        </div>
                    </div>

                    <button onClick={()=>onApply(s)} type="button" className="strategyCard__apply">
                        Apply Strategy
                    </button>
                </div>
            ))}
        </div>
    );
}
