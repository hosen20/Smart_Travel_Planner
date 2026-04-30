"""Pydantic schemas for the travel planner app."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class TravelQuery(BaseModel):
    query: str


class ToolResult(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class AgentResponse(BaseModel):
    response: str
    tools_used: List[str]
    token_usage: Optional[dict] = None


class DestinationClassify(BaseModel):
    destination: str


class RAGSearch(BaseModel):
    query: str


class LiveConditions(BaseModel):
    destination: str
    date: Optional[str] = None