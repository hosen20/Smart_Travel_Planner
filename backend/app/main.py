"""Main FastAPI application for the Smart Travel Planner."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.lifespan import lifespan
from app.logging_config import get_logger
from app.routes import agent, auth

log = get_logger(__name__)


app = FastAPI(
    title="Smart Travel Planner",
    version="1.0.0",
    description="AI-powered travel planning agent",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(agent.router)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}