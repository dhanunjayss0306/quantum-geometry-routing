"""FastAPI application: the quantum engine behind a clean HTTP API.

Quantum logic lives in quantum/ and algorithms/ -- this file only wires
routes together. Run with:

    uvicorn backend.main:app --reload          # from the repo root
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import experiments, health, topologies

app = FastAPI(
    title="Quantum Geometry Routing API",
    description="Bell-state routing experiments across quantum chip topologies.",
    version="0.1.0",
)

# Local dashboard development; tighten origins if deployed publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(topologies.router)
app.include_router(experiments.router)
