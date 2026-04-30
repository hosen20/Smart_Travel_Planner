"""Dependency providers.

Engineering standard: handlers declare what they need with `Depends(...)`.
This is the FastAPI-native way to inject testable, lifecycle-managed
objects. In tests, override with `app.dependency_overrides[...] = ...`.
"""

from __future__ import annotations

from typing import Annotated, AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import TravelAgent
from app.lifespan import AppState
from app.services.database import DatabaseService
from app.services.llm import LLMService
from app.services.ml import MLService
from app.services.rag import RAGService
from app.settings import Settings


def get_app_state(request: Request) -> AppState:
    """Pull the lifespan-built :class:`AppState` off the FastAPI app.

    Every other ``get_*`` dependency below chains off this one so they
    share the same singletons inside a request.
    """
    return request.app.state.app_state


def get_settings_dep(state: Annotated[AppState, Depends(get_app_state)]) -> Settings:
    """Return the application :class:`Settings` instance."""
    return state.settings


def get_db_service(state: Annotated[AppState, Depends(get_app_state)]) -> DatabaseService:
    """Return the singleton :class:`DatabaseService`."""
    return state.db_service


def get_llm(state: Annotated[AppState, Depends(get_app_state)]) -> LLMService:
    """Return the singleton :class:`LLMService`."""
    return state.llm_service


def get_ml_service(state: Annotated[AppState, Depends(get_app_state)]) -> MLService:
    """Return the singleton :class:`MLService`."""
    return state.ml_service


def get_rag_service(state: Annotated[AppState, Depends(get_app_state)]) -> RAGService:
    """Return the singleton :class:`RAGService`."""
    return state.rag_service


def get_agent(state: Annotated[AppState, Depends(get_app_state)]) -> TravelAgent:
    """Return the singleton :class:`TravelAgent`."""
    return state.agent


async def get_db_session(
    db_service: Annotated[DatabaseService, Depends(get_db_service)]
) -> AsyncIterator[AsyncSession]:
    """Provide an async database session for the request."""
    async with db_service.async_session() as session:
        yield session