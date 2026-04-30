from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import health
from app.models import User
from app.routes.agent import router as agent_router, get_agent as get_agent_dep, get_db_session
from app.routes.auth import router as auth_router
from app.deps import get_settings_dep
from app.settings import get_settings


class FakeAgent:
    async def run(self, query: str):
        return {
            "response": f"fake plan for {query}",
            "tools_used": ["fake_tool"],
        }


def create_test_app(db_session, current_user=None):
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(agent_router)
    app.get("/health")(health)

    async def _override_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_db_session
    app.dependency_overrides[get_settings_dep] = lambda: get_settings()
    app.dependency_overrides[get_agent_dep] = lambda: FakeAgent()
    if current_user is not None:
        from app.routes.auth import get_current_user as get_current_user_dep

        app.dependency_overrides[get_current_user_dep] = lambda: current_user
    return app


class FakeResult:
    def __init__(self, item):
        self._item = item

    def scalars(self):
        return self

    def first(self):
        return self._item


class FakeDBSession:
    def __init__(self):
        self.users: dict[str, User] = {}
        self.next_id = 1
        self.added = []

    def add(self, obj):
        if isinstance(obj, User):
            if getattr(obj, "id", None) is None:
                obj.id = self.next_id
                self.next_id += 1
            if getattr(obj, "is_active", None) is None:
                obj.is_active = True
            if getattr(obj, "is_superuser", None) is None:
                obj.is_superuser = False
            self.users[obj.email] = obj
        self.added.append(obj)

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self.next_id
            self.next_id += 1

    async def execute(self, stmt):
        if hasattr(stmt, "whereclause") and stmt.whereclause is not None:
            clause = stmt.whereclause
            left_name = getattr(clause.left, "name", None)
            left_text = str(clause.left).lower()
            if left_name == "email" or "users.email" in left_text:
                email = getattr(clause.right, "value", None)
                return FakeResult(self.users.get(email))
        return FakeResult(None)


def test_health_route():
    fake_db = FakeDBSession()
    app = create_test_app(fake_db)
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_auth_register_login_verify_routes():
    import app.routes.auth as auth_module

    auth_module.get_password_hash = lambda password: password
    auth_module.verify_password = lambda plain_password, hashed_password: plain_password == hashed_password

    fake_db = FakeDBSession()
    app = create_test_app(fake_db)

    with TestClient(app) as client:
        register_resp = client.post(
            "/auth/register",
            json={"email": "route-test@example.com", "password": "securepass"},
        )
        assert register_resp.status_code == 200
        body = register_resp.json()
        assert body["email"] == "route-test@example.com"
        assert body["is_active"] is True
        assert body["is_superuser"] is False

        token_resp = client.post(
            "/auth/token",
            data={"username": "route-test@example.com", "password": "securepass"},
        )
        assert token_resp.status_code == 200
        token_body = token_resp.json()
        assert "access_token" in token_body
        assert token_body["token_type"] == "bearer"

        verify_resp = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {token_body['access_token']}"},
        )
        assert verify_resp.status_code == 200
        verify_body = verify_resp.json()
        assert verify_body["email"] == "route-test@example.com"
        assert verify_body["is_active"] is True
        assert verify_body["is_superuser"] is False


def test_agent_plan_route_works_with_fake_agent():
    fake_db = FakeDBSession()
    current_user = User(
        id=1,
        email="plan-route@example.com",
        hashed_password="irrelevant",
        is_active=True,
        is_superuser=False,
    )
    app = create_test_app(fake_db, current_user=current_user)

    with TestClient(app) as client:
        response = client.post("/agent/plan", json={"query": "Weekend hiking"})

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "fake plan for Weekend hiking"
    assert data["tools_used"] == ["fake_tool"]
