#!/usr/bin/env python3
"""Script to ingest destination knowledge into the RAG system."""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import app modules
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))

from app.services.database import DatabaseService
from app.services.llm import LLMService
from app.services.rag import RAGService
from app.settings import Settings


async def main():
    try:
        settings = Settings()
        db_service = DatabaseService(settings)
        await db_service.create_tables()

        llm_service = LLMService(settings)

        # Sample destination data
        destinations = [
            {
                "content": "Paris is the capital and most populous city of France. Known for its art, fashion, gastronomy and culture, it is a major railway, highway, and air-transport hub. Paris is especially known for its museums and architectural landmarks: the Louvre, the Arc de Triomphe, the Eiffel Tower, the Notre-Dame Cathedral, Sacré-Cœur, etc.",
                "metadata": {"destination": "Paris", "country": "France", "type": "city"}
            },
            {
                "content": "Bali is a province of Indonesia and the westernmost of the Lesser Sunda Islands. It is one of the country's 34 provinces with the provincial capital at Denpasar. Bali is known for its volcanic mountains, iconic rice terraces, beaches and coral reefs, lush tropical forests, and beautiful Hindu temples.",
                "metadata": {"destination": "Bali", "country": "Indonesia", "type": "island"}
            },
            {
                "content": "The Swiss Alps are a mountain range in Switzerland. They are part of the Alps, a chain of mountains that extends across Europe. The Swiss Alps are known for their stunning landscapes, ski resorts, hiking trails, and picturesque villages. Popular activities include skiing, snowboarding, hiking, and mountaineering.",
                "metadata": {"destination": "Swiss Alps", "country": "Switzerland", "type": "mountains"}
            }
        ]

        rag_service = RAGService(settings, llm_service, db_service)
        await rag_service.ingest_documents(destinations)

        print("Data ingestion complete!")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database is running. Run 'docker compose up -d db' first.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)