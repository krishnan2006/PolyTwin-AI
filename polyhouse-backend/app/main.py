from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import telemetry, simulation
from app.core.db import create_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database connection pool...")
    await create_pool()

    yield

    print("Closing database connection pool...")
    await close_pool()


app = FastAPI(
    title="PolyHouse Backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    telemetry.router,
    prefix="/api/v1",
    tags=["Telemetry"],
)

app.include_router(simulation.router)
from app.api.routers import scenario

app.include_router(
    scenario.router,
    prefix="/api/v1",
    tags=["Scenario"],
)