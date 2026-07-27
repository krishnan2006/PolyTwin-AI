const MAX_BY_UNIT = {
    "°C": 50,
    "%": 100,
    Lux: 2000,
};

export default function SensorCard({ title, value, unit }) {
    const numeric = Number(value);
    const hasValue = value !== "--" && !Number.isNaN(numeric);
    const max = MAX_BY_UNIT[unit] ?? 100;
    const pct = hasValue ? Math.min(100, Math.max(0, (numeric / max) * 100)) : 0;

    return (
        <div className="sensorCard">
            <h3 className="sensorCard__title">{title}</h3>

            <div className="sensorCard__valueRow">
                <span className="sensorCard__value">{value}</span>
                <span className="sensorCard__unit">{unit}</span>
            </div>

            <div
                className="sensorCard__gauge"
                role="progressbar"
                aria-label={`${title} level`}
                aria-valuenow={hasValue ? Math.round(numeric) : undefined}
                aria-valuemin={0}
                aria-valuemax={max}
            >
                <div
                    className="sensorCard__gaugeFill"
                    style={{ width: `${hasValue ? pct : 0}%` }}
                />
            </div>
        </div>
    );
}
