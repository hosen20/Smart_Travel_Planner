"""Agent implementation using LangGraph."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict

import json

from app.logging_config import get_logger
from app.services.llm import LLMService
from app.tools import Tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.prompts import TRAVEL_AGENT_SYSTEM_PROMPT, TRAVEL_AGENT_FINAL_PROMPT

log = get_logger(__name__)


class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    tools_used: List[str]
    current_step: int


class TravelAgent:
    """LangGraph-based agent for travel planning."""

    def __init__(self, llm_service: LLMService, tools: Dict[str, Tool], max_steps: int = 10):
        self.llm_service = llm_service
        self.tools = tools
        self.max_steps = max_steps
        self.tool_schemas = [tool.schema for tool in tools.values()]
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Nodes
        workflow.add_node("reason", self._reason_step)
        workflow.add_node("act", self._act_step)

        # Edges
        workflow.set_entry_point("reason")
        workflow.add_conditional_edges(
            "reason",
            self._should_continue,
            {"act": "act", END: END}
        )
        workflow.add_edge("act", "reason")

        return workflow.compile()

    async def _reason_step(self, state: AgentState) -> AgentState:
        """Reasoning step - decide what to do."""
        messages = [
            {"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT},
            *state["messages"]
        ]

        tools = self.tool_schemas if state["current_step"] < self.max_steps else None

        response = await self.llm_service.generate(messages, tools=tools)
        state["messages"].append(response)
        state["current_step"] += 1
        return state

    async def _act_step(self, state: AgentState) -> AgentState:
        """Action step - call tools."""
        last_message = state["messages"][-1]

        if "tool_calls" not in last_message or not last_message["tool_calls"]:
            return state

        for tool_call in last_message["tool_calls"]:
            tool_name = tool_call.function.name
            args_str = tool_call.function.arguments
            try:
                args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError:
                args = {}
            if tool_name in self.tools:
                result = await self.tools[tool_name].run(**args)
                state["tools_used"].append(tool_name)
                state["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result.data)
                })

        return state

    def _should_continue(self, state: AgentState) -> str:
        """Decide whether to continue or end."""
        if state["current_step"] >= self.max_steps:
            return END
        last_message = state["messages"][-1]
        if "tool_calls" in last_message and last_message["tool_calls"]:
            return "act"
        return END

    async def run(self, query: str) -> Dict[str, Any]:
        """Run the agent on a travel query."""
        initial_state = {
            "messages": [{"role": "user", "content": query}],
            "tools_used": [],
            "current_step": 0
        }

        final_state = await self.graph.ainvoke(initial_state)
        return {
            "response": final_state["messages"][-1]["content"],
            "tools_used": final_state["tools_used"]
        }