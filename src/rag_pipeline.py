"""
RAG Pipeline Module.

Handles document ingestion, chunking, vector embedding generation,
ChromaDB indexing, and semantic similarity search for the knowledge base.
"""

import os
import time
import random
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from google import genai
import chromadb

from src.config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    CHROMA_DB_DIR,
    CHROMA_COLLECTION_NAME,
    DATA_DIR,
)


def _call_with_backoff(func, *args, max_retries=6, **kwargs):
    """Call a function with exponential backoff for transient API errors."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            # Only retry on transient server errors (5xx)
            if "503" in error_str or "429" in error_str or "500" in error_str or "UNAVAILABLE" in error_str:
                if attempt == max_retries - 1:
                    raise
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"    [RETRY] Attempt {attempt + 1}/{max_retries} failed ({error_str[:80]}...), retrying in {sleep_time:.1f}s")
                time.sleep(sleep_time)
            else:
                raise  # Non-transient errors should not be retried


class LocalRAGPipeline:
    """
    Retrieval-Augmented Generation pipeline that:
    1. Loads and parses documents from the data/ directory (.txt, .md, .pdf)
    2. Chunks them using RecursiveCharacterTextSplitter
    3. Generates vector embeddings via Gemini embedding model
    4. Stores embeddings in a persistent ChromaDB collection
    5. Retrieves the top-K most relevant chunks for a given query
    """

    def __init__(self, db_dir: str = CHROMA_DB_DIR):
        """Initialize the Gemini client and ChromaDB persistent storage."""
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    # ──────────────────────────────────────────
    # Embedding helper
    # ──────────────────────────────────────────

    def get_embedding(self, text: str) -> list:
        """
        Generate a dense vector embedding for the given text using
        the configured Gemini embedding model, with automatic retry
        on transient server errors (503, 429, 500).

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        response = _call_with_backoff(
            self.client.models.embed_content,
            model=EMBEDDING_MODEL,
            contents=text
        )
        return response.embeddings[0].values

    # ──────────────────────────────────────────
    # Document parsing
    # ──────────────────────────────────────────

    @staticmethod
    def _read_text_file(filepath: str) -> str:
        """Read a plain text or markdown file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _read_pdf_file(filepath: str) -> str:
        """Extract text from a PDF file page-by-page using pypdf."""
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    # ──────────────────────────────────────────
    # Document ingestion
    # ──────────────────────────────────────────

    def ingest_document(self, doc_name: str, content: str):
        """
        Split a document into chunks and add them to the vector database.

        Args:
            doc_name: A unique identifier for the document (e.g., filename).
            content:  The full text content of the document.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_text(content)

        for idx, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk)
            chunk_id = f"{doc_name}_chunk_{idx}"

            # Use upsert to avoid duplicate ID errors on re-indexing
            self.collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[{"source": doc_name, "chunk_index": idx}],
                documents=[chunk]
            )

    def ingest_all_documents(self, data_dir: str = DATA_DIR):
        """
        Walk the data directory and ingest all supported files
        (.txt, .md, .pdf) into the vector database.

        Args:
            data_dir: Path to the directory containing knowledge base documents.
        """
        supported_extensions = {".txt", ".md", ".pdf"}

        for filename in sorted(os.listdir(data_dir)):
            filepath = os.path.join(data_dir, filename)
            ext = os.path.splitext(filename)[1].lower()

            if ext not in supported_extensions or not os.path.isfile(filepath):
                continue

            print(f"  [*] Ingesting: {filename}")

            if ext in (".txt", ".md"):
                content = self._read_text_file(filepath)
            elif ext == ".pdf":
                content = self._read_pdf_file(filepath)
            else:
                continue

            if content.strip():
                self.ingest_document(filename, content)

        print(f"  [OK] Total chunks indexed: {self.collection.count()}")

    # ──────────────────────────────────────────
    # Retrieval
    # ──────────────────────────────────────────

    def retrieve_context(self, query: str, top_k: int = TOP_K) -> list:
        """
        Perform semantic similarity search against the vector database.

        Args:
            query: The user's search query.
            top_k: Number of top results to return.

        Returns:
            A list of dicts, each containing:
              - text:   The retrieved chunk text
              - source: The source document name
              - score:  A confidence score (1 - cosine_distance)
        """
        query_vector = self.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        retrieved_items = []
        if results and results["documents"]:
            for i in range(len(results["documents"][0])):
                distance = results["distances"][0][i] if results["distances"] else 0.0
                retrieved_items.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "score": round(1.0 - distance, 4)
                })
        return retrieved_items

    # ──────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────

    def is_indexed(self) -> bool:
        """Check whether the collection already has documents indexed."""
        return self.collection.count() > 0

    def get_document_count(self) -> int:
        """Return the total number of chunks in the collection."""
        return self.collection.count()


# ──────────────────────────────────────────────
# Standalone test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    pipeline = LocalRAGPipeline()

    if not pipeline.is_indexed():
        print("Indexing documents...")
        pipeline.ingest_all_documents()
    else:
        print(f"Already indexed: {pipeline.get_document_count()} chunks")

    # Test retrieval
    test_query = "How do I reset my password?"
    results = pipeline.retrieve_context(test_query)
    print(f"\nQuery: {test_query}")
    for r in results:
        print(f"  [{r['score']:.4f}] {r['source']}: {r['text'][:100]}...")
