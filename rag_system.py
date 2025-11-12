#!/usr/bin/env python3
"""
RAG System - Retrieval Augmented Generation
ChromaDB + Vector Search + Long-term Memory

Copyright © 2025 AlphaEdge AINV
"""
import os
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
import hashlib

import chromadb
from chromadb.config import Settings


class RAGSystem:
    """
    RAG System with ChromaDB
    - Document storage and retrieval
    - Semantic search
    - Long-term memory
    - Conversation history
    """

    def __init__(
        self,
        db_path: str = "./chroma_db",
        collection_name: str = "jareth2_memory"
    ):
        """
        Initialize RAG system

        Args:
            db_path: Path to ChromaDB database
            collection_name: Collection name
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Long-term memory and knowledge base"}
        )

        print(f"✓ RAG System initialized: {collection_name}")
        print(f"  Documents: {self.collection.count()}")

    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add document to knowledge base

        Args:
            text: Document text
            metadata: Optional metadata
            doc_id: Optional document ID (auto-generated if None)

        Returns:
            Document ID
        """
        if not doc_id:
            # Generate ID from content hash
            doc_id = hashlib.sha256(text.encode()).hexdigest()[:16]

        # Add timestamp
        if metadata is None:
            metadata = {}

        metadata['timestamp'] = datetime.now().isoformat()
        metadata['doc_length'] = len(text)

        # Add to collection
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

        return doc_id

    def add_documents_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple documents

        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of IDs

        Returns:
            List of document IDs
        """
        if ids is None:
            ids = [
                hashlib.sha256(text.encode()).hexdigest()[:16]
                for text in texts
            ]

        if metadatas is None:
            metadatas = [
                {'timestamp': datetime.now().isoformat()}
                for _ in texts
            ]
        else:
            for meta in metadatas:
                if 'timestamp' not in meta:
                    meta['timestamp'] = datetime.now().isoformat()

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        return ids

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Semantic search

        Args:
            query: Search query
            n_results: Number of results
            where: Optional metadata filter

        Returns:
            Search results
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        return {
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0],
            'ids': results['ids'][0]
        }

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID

        Args:
            doc_id: Document ID

        Returns:
            Document dict or None
        """
        try:
            result = self.collection.get(ids=[doc_id])

            if result['documents']:
                return {
                    'id': doc_id,
                    'text': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
        except:
            pass

        return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete document"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except:
            return False

    def update_document(
        self,
        doc_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update document

        Args:
            doc_id: Document ID
            text: New text (optional)
            metadata: New metadata (optional)

        Returns:
            Success boolean
        """
        try:
            update_args = {'ids': [doc_id]}

            if text:
                update_args['documents'] = [text]

            if metadata:
                metadata['updated_at'] = datetime.now().isoformat()
                update_args['metadatas'] = [metadata]

            self.collection.update(**update_args)
            return True

        except:
            return False

    def clear(self):
        """Clear all documents"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(self.collection.name)

    def count(self) -> int:
        """Get document count"""
        return self.collection.count()

    async def search_async(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Async version of search"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.search, query, n_results, where)


class ConversationMemory:
    """
    Conversation history with RAG
    """

    def __init__(self, db_path: str = "./chroma_db"):
        """Initialize conversation memory"""
        self.rag = RAGSystem(
            db_path=db_path,
            collection_name="conversation_history"
        )

    def add_turn(
        self,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add conversation turn

        Args:
            user_message: User's message
            assistant_message: Assistant's response
            metadata: Optional metadata

        Returns:
            Turn ID
        """
        if metadata is None:
            metadata = {}

        metadata['type'] = 'conversation_turn'
        metadata['timestamp'] = datetime.now().isoformat()

        # Combine messages for embedding
        combined = f"User: {user_message}\nAssistant: {assistant_message}"

        return self.rag.add_document(combined, metadata)

    async def search_history(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search conversation history

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            List of relevant conversation turns
        """
        results = await self.rag.search_async(
            query,
            n_results=n_results,
            where={'type': 'conversation_turn'}
        )

        turns = []
        for doc, meta, distance in zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        ):
            turns.append({
                'text': doc,
                'metadata': meta,
                'relevance': 1.0 - distance
            })

        return turns

    def get_recent_turns(self, n: int = 10) -> List[str]:
        """Get N most recent conversation turns"""
        # This is a simplified version
        # In production, you'd query by timestamp
        all_docs = self.rag.collection.get()

        if not all_docs['documents']:
            return []

        # Sort by timestamp
        docs_with_time = [
            (doc, meta)
            for doc, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]

        docs_with_time.sort(
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )

        return [doc for doc, _ in docs_with_time[:n]]


class KnowledgeBase:
    """
    Knowledge base with RAG
    """

    def __init__(self, db_path: str = "./chroma_db"):
        """Initialize knowledge base"""
        self.rag = RAGSystem(
            db_path=db_path,
            collection_name="knowledge_base"
        )

    def add_knowledge(
        self,
        text: str,
        category: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Add knowledge entry

        Args:
            text: Knowledge text
            category: Category (e.g., "technical", "business", "personal")
            tags: Optional tags
            source: Optional source

        Returns:
            Entry ID
        """
        metadata = {
            'type': 'knowledge',
            'category': category,
            'tags': tags or [],
            'source': source,
            'timestamp': datetime.now().isoformat()
        }

        return self.rag.add_document(text, metadata)

    async def query_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge base

        Args:
            query: Search query
            category: Optional category filter
            n_results: Number of results

        Returns:
            List of relevant knowledge entries
        """
        where = {'type': 'knowledge'}
        if category:
            where['category'] = category

        results = await self.rag.search_async(query, n_results, where)

        entries = []
        for doc, meta, distance in zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        ):
            entries.append({
                'text': doc,
                'category': meta.get('category'),
                'tags': meta.get('tags', []),
                'source': meta.get('source'),
                'relevance': 1.0 - distance
            })

        return entries

    def ingest_file(self, file_path: str, category: str) -> int:
        """
        Ingest file into knowledge base

        Args:
            file_path: Path to file
            category: Category for the file

        Returns:
            Number of entries added
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file
        text = path.read_text(encoding='utf-8')

        # Split into chunks (simple split by paragraphs)
        chunks = [
            chunk.strip()
            for chunk in text.split('\n\n')
            if chunk.strip()
        ]

        # Add chunks
        ids = []
        for chunk in chunks:
            doc_id = self.add_knowledge(
                text=chunk,
                category=category,
                source=str(file_path)
            )
            ids.append(doc_id)

        return len(ids)


# ===== Global Instances =====

_rag_system: Optional[RAGSystem] = None
_conversation_memory: Optional[ConversationMemory] = None
_knowledge_base: Optional[KnowledgeBase] = None


def get_rag_system() -> RAGSystem:
    """Get global RAG system"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system


def get_conversation_memory() -> ConversationMemory:
    """Get global conversation memory"""
    global _conversation_memory
    if _conversation_memory is None:
        _conversation_memory = ConversationMemory()
    return _conversation_memory


def get_knowledge_base() -> KnowledgeBase:
    """Get global knowledge base"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base


# ===== CLI =====

if __name__ == "__main__":
    import sys

    async def test_rag():
        print("=== Testing RAG System ===\n")

        # Test knowledge base
        kb = get_knowledge_base()

        # Add some knowledge
        kb.add_knowledge(
            "Python is a high-level programming language known for its simplicity.",
            category="technical",
            tags=["python", "programming"]
        )

        kb.add_knowledge(
            "Machine learning is a subset of AI that learns from data.",
            category="technical",
            tags=["ml", "ai"]
        )

        # Query
        results = await kb.query_knowledge("What is Python?")

        print("Query: What is Python?\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['text']}")
            print(f"   Relevance: {result['relevance']:.2%}\n")

    asyncio.run(test_rag())
