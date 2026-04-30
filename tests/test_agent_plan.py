from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deps import get_db_session
from app.routes.agent import get_agent as get_agent_dep, router as agent_router
from app.routes.auth import get_current_user as get_current_user_dep


class DummyUser:
    id = 1
    email = "test@example.com"
    is_active = True
    is_superuser = False


class DummyAgent:
    async def run(self, query: str):
        return {
            "response": f"Planned trip for {query}",
            "tools_used": ["fake_tool"],
        }


class DummyDBSession:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        return None

    async def refresh(self, obj):
        setattr(obj, "id", 1)


async def dummy_db_session():
    yield DummyDBSession()


def test_plan_trip_returns_expected_response():
    app = FastAPI()
    app.include_router(agent_router)

    app.dependency_overrides[get_agent_dep] = lambda: DummyAgent()
    app.dependency_overrides[get_current_user_dep] = lambda: DummyUser()
    app.dependency_overrides[get_db_session] = dummy_db_session

    client = TestClient(app)
    response = client.post("/agent/plan", json={"query": "Beach vacation"})

    assert response.status_code == 200
    assert response.json()["response"] == "Planned trip for Beach vacation"
    assert response.json()["tools_used"] == ["fake_tool"]


def test_plan_trip_with_groq_provider():
    from app.agents.agent import TravelAgent
    from app.settings import get_settings
    from app.services.llm import LLMService

    settings = get_settings()
    assert settings.llm_provider == "groq"

    llm_service = LLMService(settings)
    agent = TravelAgent(llm_service, tools={})

    app = FastAPI()
    app.include_router(agent_router)

    app.dependency_overrides[get_agent_dep] = lambda: agent
    app.dependency_overrides[get_current_user_dep] = lambda: DummyUser()
    app.dependency_overrides[get_db_session] = dummy_db_session

    with TestClient(app) as client:
        response = client.post("/agent/plan", json={"query": "Find a quick weekend getaway"})

    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert isinstance(body["response"], str)
    assert body["response"].strip() != ""
    assert "tools_used" in body
    assert isinstance(body["tools_used"], list)
