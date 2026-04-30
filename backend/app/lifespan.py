"""FastAPI lifespan: build singletons on startup, dispose on shutdown.

Engineering standard: things that should exist exactly once per process
(LLM client, embedding client, vector store, tool registry, agent runner,
trace store) live on `app.state` and are exposed to handlers via the
DI providers in `deps.py`. This is the only place we instantiate them.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from app.agents import TravelAgent
from app.logging_config import configure_logging, get_logger
from app.services.database import DatabaseService
from app.services.llm import LLMService
from app.services.ml import MLService
from app.services.rag import RAGService
from app.settings import Settings, get_settings


@dataclass
class AppState:
    """Container for every singleton built at startup.

    Held on ``app.state.app_state`` and surfaced to handlers via the
    dependency providers in :mod:`app.deps`.
    """

    settings: Settings
    db_service: DatabaseService
    llm_service: LLMService
    ml_service: MLService
    rag_service: RAGService
    agent: TravelAgent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI startup/shutdown context.

    Builds singletons in dependency order on entry, runs the best-effort
    RAG warmup, then yields control to the server. On exit, closes the
    LLM and embedding HTTP clients so we don't leak sockets.
    """
    settings = get_settings()
    # Configure logging FIRST so every subsequent line is structured.
    configure_logging(level=settings.log_level, json_output=settings.log_json)
    log = get_logger(__name__)
    log.info(
        "startup",
        provider=settings.llm_provider,
        model=settings.model_name(),
    )

    # Build singletons in dependency order. Each subsequent line may rely
    # on the objects above it, so the ordering is intentional.
    db_service = DatabaseService(settings)
    await db_service.create_tables()

    llm_service = LLMService(settings)
    ml_service = MLService(settings)
    ml_service.load_model()

    rag_service = RAGService(settings, llm_service, db_service)

    # Initialize tools
    from app.tools import DestinationClassifierTool, LiveConditionsTool, RAGSearchTool
    tools = {
        "classify_destination": DestinationClassifierTool(ml_service),
        "live_conditions": LiveConditionsTool(settings),
        "rag_search": RAGSearchTool(rag_service)
    }

    agent_instance = TravelAgent(llm_service, tools, settings.max_agent_steps)

    app.state.app_state = AppState(
        settings=settings,
        db_service=db_service,
        llm_service=llm_service,
        ml_service=ml_service,
        rag_service=rag_service,
        agent=agent_instance,
    )

    log.info("Application startup complete")
    try:
        yield
    finally:
        # Always close clients on shutdown, even if startup raised partway.
        log.info("shutdown")
        await llm_service.aclose()