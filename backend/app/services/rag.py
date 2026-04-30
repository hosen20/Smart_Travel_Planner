"""RAG service for destination knowledge retrieval."""

from __future__ import annotations

from typing import List, Tuple
from sqlalchemy import text

from app.logging_config import get_logger
from app.services.database import DatabaseService
from app.services.llm import LLMService
from app.settings import Settings

log = get_logger(__name__)


class RAGService:
    """Service for RAG operations using pgvector."""

    def __init__(self, settings: Settings, llm_service: LLMService, db_service: DatabaseService):
        self.settings = settings
        self.llm_service = llm_service
        self.db_service = db_service

    async def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Search for relevant destination knowledge."""
        try:
            query_emb = await self.llm_service.embed([query])
            query_emb = query_emb[0]

            async with self.db_service.async_session() as session:
                result = await session.execute(
                    text("""
                    SELECT content, metadata, 1 - (embedding <=> :query_emb) as similarity
                    FROM destination_knowledge
                    ORDER BY embedding <=> :query_emb
                    LIMIT :top_k
                    """),
                    {"query_emb": query_emb, "top_k": top_k}
                )
                rows = result.fetchall()

            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "metadata": row[1],
                    "similarity": float(row[2])
                })

            log.info("RAG search completed", query=query, results_count=len(results))
            return results

        except Exception as e:
            log.error("RAG search failed", error=str(e))
            return []

    async def ingest_documents(self, documents: List[Tuple[str, dict]]) -> None:
        """Ingest documents into the vector store."""
        try:
            async with self.db_service.async_session() as session:
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS destination_knowledge (
                        id SERIAL PRIMARY KEY,
                        content TEXT,
                        metadata JSONB,
                        embedding VECTOR(384)
                    )
                """))

                contents = [doc[0] for doc in documents]
                embeddings = await self.llm_service.embed(contents)

                for (content, metadata), emb in zip(documents, embeddings):
                    await session.execute(
                        text("""
                        INSERT INTO destination_knowledge (content, metadata, embedding)
                        VALUES (:content, :metadata, :embedding)
                        """),
                        {"content": content, "metadata": metadata, "embedding": emb}
                    )

                await session.commit()
                log.info("Documents ingested", count=len(documents))

        except Exception as e:
            log.error("Document ingestion failed", error=str(e))
