"""Agent tools for the travel planner."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.logging_config import get_logger
from app.schemas import ToolResult
from app.services.ml import MLService
from app.services.rag import RAGService
from app.settings import Settings

log = get_logger(__name__)


class Tool(ABC):
    """Base class for agent tools."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, **kwargs) -> ToolResult:
        """Run the tool with given arguments."""
        pass

    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """Return the tool schema for LLM."""
        pass


class DestinationClassifierTool(Tool):
    """Tool to classify destination travel style."""

    def __init__(self, ml_service: MLService):
        super().__init__("classify_destination")
        self.ml_service = ml_service

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Classify the travel style for a destination (e.g., adventure, relaxation, cultural).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "The destination to classify."}
                    },
                    "required": ["destination"]
                }
            }
        }

    async def run(self, destination: str) -> ToolResult:
        try:
            style = self.ml_service.classify_destination(destination)
            return ToolResult(success=True, data={"style": style})
        except Exception as e:
            log.error("Classification failed", error=str(e))
            return ToolResult(success=False, error=str(e))


class RAGSearchTool(Tool):
    """Tool to search destination knowledge."""

    def __init__(self, rag_service: RAGService):
        super().__init__("rag_search")
        self.rag_service = rag_service

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Search for information about destinations using RAG.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query."}
                    },
                    "required": ["query"]
                }
            }
        }

    async def run(self, query: str) -> ToolResult:
        try:
            results = await self.rag_service.search(query)
            return ToolResult(success=True, data={"results": results})
        except Exception as e:
            log.error("RAG search failed", error=str(e))
            return ToolResult(success=False, error=str(e))


class LiveConditionsTool(Tool):
    """Tool to fetch live weather, flights, FX."""

    def __init__(self, settings: Settings):
        super().__init__("live_conditions")
        self.settings = settings

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Fetch live conditions like weather, exchange rates, and flight info for a destination.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "The destination."},
                        "date": {"type": "string", "description": "Optional date for conditions."}
                    },
                    "required": ["destination"]
                }
            }
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def run(self, destination: str, date: str | None = None) -> ToolResult:
        try:
            # Mock implementation - in real app, integrate with APIs
            async with httpx.AsyncClient(timeout=10) as client:
                # Weather
                weather_resp = await client.get(
                    self.settings.weather_api_url,
                    params={"latitude": 40.0, "longitude": -74.0, "current_weather": True}  # Mock coords
                )
                weather = weather_resp.json() if weather_resp.status_code == 200 else {}

                # FX
                fx_resp = await client.get(self.settings.exchange_api_url)
                fx = fx_resp.json() if fx_resp.status_code == 200 else {}

                # Flights - placeholder
                flights = {"message": "Flight data not implemented"}

            return ToolResult(success=True, data={
                "weather": weather,
                "exchange_rates": fx,
                "flights": flights
            })
        except Exception as e:
            log.error("Live conditions fetch failed", error=str(e))
            return ToolResult(success=False, error=str(e))