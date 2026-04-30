"""Tests for the travel planner."""

import pytest
from pydantic import ValidationError

from app.schemas import TravelQuery, ToolResult


def test_travel_query_valid():
    """Test valid travel query."""
    query = TravelQuery(query="Two weeks in July, warm destination")
    assert query.query == "Two weeks in July, warm destination"


def test_tool_result_success():
    """Test successful tool result."""
    result = ToolResult(success=True, data={"key": "value"})
    assert result.success is True
    assert result.data == {"key": "value"}


def test_tool_result_failure():
    """Test failed tool result."""
    result = ToolResult(success=False, error="API error")
    assert result.success is False
    assert result.error == "API error"