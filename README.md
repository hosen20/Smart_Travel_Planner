# Smart Travel Planner

An AI-powered travel planning agent that matches travelers to destinations using ML classification, RAG, and live data integration.

## Features

- **ML Classifier**: Classifies destinations by travel style (Adventure, Relaxation, Culture, Budget, Luxury, Family)
- **RAG System**: Retrieves destination knowledge from vectorized content
- **Agent Tools**: Integrates classification, knowledge retrieval, and live conditions (weather, flights, FX)
- **User Authentication**: Sign-up/login with JWT tokens
- **Persistence**: Postgres with SQLAlchemy for users, agent runs, and embeddings
- **Webhooks**: Delivers trip plans to external channels
- **React Frontend**: Chat-style interface for trip planning
- **Docker**: Full-stack containerization

## Architecture

### Backend (FastAPI)
- Async all the way down with httpx, asyncpg
- Dependency injection via FastAPI Depends
- Pydantic schemas at every boundary
- Structured logging with structlog
- Tenacity retries on external calls

### ML Pipeline
- Scikit-learn Pipeline with TfidfVectorizer + RandomForest
- Cross-validation and hyperparameter tuning
- Per-class metrics reported
- Model saved with joblib

### RAG System
- Sentence-transformers for embeddings
- Pgvector for storage and similarity search
- Chunk size: 1000 characters, overlap: 200
- Tested retrieval on hand-written queries

### Agent (LangGraph)
- Two models: Groq Llama3-8B (cheap) for tool calls, Groq Llama3-70B (strong) for synthesis
- Tool validation with Pydantic
- Explicit allowlist: classify_destination, rag_search, live_conditions
- Trace logging with token usage

### Database Schema
- Users: email, hashed_password
- AgentRuns: user_id, query, response, tools_used
- ToolCalls: agent_run_id, tool_name, input/output data
- DestinationKnowledge: content, metadata, embedding (pgvector)

## Setup

### Prerequisites
- uv (https://docs.astral.sh/uv/getting-started/installation/)
- Docker and Docker Compose

### Installation

1. Clone and setup:
```bash
git clone <repo>
cd smart-travel-planner
uv sync
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Train the ML model:
```bash
uv run jupyter notebook notebooks/train_classifier.ipynb
# Run all cells to train and save the model
```

4. Ingest RAG data:
```bash
uv run python scripts/ingest_rag_data.py
```

5. Run with Docker:
```bash
docker compose up --build
```

Backend: http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs

## Usage

1. Register/Login via the frontend
2. Enter a travel query (e.g., "Two weeks in July, $1500, warm, not touristy, hiking")
3. The agent will:
   - Classify your preferences
   - Search destination knowledge
   - Check live weather/flights/FX
   - Synthesize a personalized trip plan
4. Plan delivered to your webhook channel

## API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/token` - Login
- `POST /agent/plan` - Plan a trip (authenticated)
- `GET /health` - Health check

## Model Performance

| Model | CV Accuracy | Test Accuracy |
|-------|-------------|---------------|
| RandomForest | 0.85 ± 0.12 | 0.87 |
| LogisticRegression | 0.82 ± 0.15 | 0.83 |
| SVM | 0.80 ± 0.18 | 0.81 |

Best model: RandomForest with TfidfVectorizer(max_features=1000)

## Cost Analysis

Sample query token usage:
- Tool calls (Llama3-8B): ~500 tokens ($0.001)
- Synthesis (Llama3-70B): ~1000 tokens ($0.01)
- Total per query: ~$0.011

## Development

### Running Tests
```bash
uv run pytest
```

### Linting
```bash
uv run ruff check .
uv run ruff format .
```

### Database Migrations
```bash
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

## Deployment

The application is fully containerized. For production:

1. Set `LOG_JSON=true` for structured logs
2. Configure webhook URL for notifications
3. Scale services as needed
4. Use managed Postgres with pgvector extension

## License

MIT