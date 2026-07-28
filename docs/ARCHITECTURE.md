# PolyTwin AI Architecture

## Overview

PolyTwin AI is an AI-powered Digital Twin platform for protected agriculture.

The system consists of six major layers.

```
                   User
                     │
                     ▼
            React Frontend
                     │
                     ▼
             FastAPI Backend
                     │
 ┌────────────┬────────────┬─────────────┐
 │Telemetry   │Simulation  │Disaster     │
 │Engine      │Engine      │Engine       │
 └────────────┴────────────┴─────────────┘
                     │
             Recommendation Engine
                     │
                     ▼
               TimescaleDB
                     │
                     ▼
          ESP32 / Mock Publisher
                     │
                     ▼
             Weather Forecast API
```

---

## Modules

### Frontend

Responsibilities

- Dashboard
- Scenario Builder
- Recommendation View
- Historical Charts

---

### Backend

Responsibilities

- REST APIs
- Authentication
- Validation
- Business Logic

---

### Telemetry Engine

Responsibilities

- Receive sensor values
- Store data
- Validate readings

---

### Simulation Engine

Responsibilities

- Simulate future greenhouse state
- Evaluate actuator changes
- Compare scenarios

---

### Disaster Engine

Responsibilities

- Weather analysis
- Risk calculation
- Early warning

---

### Recommendation Engine

Responsibilities

- Generate mitigation strategies
- Rank recommendations
- Explain reasoning

---

## Data Flow

ESP32

↓

Backend

↓

Database

↓

Simulation

↓

Disaster Engine

↓

Recommendation Engine

↓

Dashboard

↓

Farmer Decision

↓

Actuator