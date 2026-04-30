"""Agent router for travel planning."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import TravelAgent
from app.deps import get_db_session
from app.logging_config import get_logger
from app.models import AgentRun, ToolCall, User
from app.routes.auth import get_current_user
from app.schemas import AgentResponse, TravelQuery

log = get_logger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


async def get_agent(request: Request) -> TravelAgent:
    """Dependency to get the agent from app state."""
    return request.app.state.app_state.agent


@router.post("/plan", response_model=AgentResponse)
async def plan_trip(
    query: TravelQuery,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    agent: Annotated[TravelAgent, Depends(get_agent)]
) -> AgentResponse:
    try:
        # Run agent
        result = await agent.run(query.query)

        # Save to database
        agent_run = AgentRun(
            user_id=current_user.id,
            query=query.query,
            response=result["response"],
            tools_used=result["tools_used"]
        )
        db.add(agent_run)
        await db.commit()
        await db.refresh(agent_run)

        # Save tool calls
        for tool in result["tools_used"]:
            tool_call = ToolCall(
                agent_run_id=agent_run.id,
                tool_name=tool,
                input_data={},  # Would parse from agent
                output_data={}
            )
            db.add(tool_call)
        await db.commit()

        log.info("Trip planned", user_id=current_user.id, tools_used=result["tools_used"])
        return AgentResponse(
            response=result["response"],
            tools_used=result["tools_used"]
        )

    except Exception as e:
        log.error("Agent run failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to plan trip")