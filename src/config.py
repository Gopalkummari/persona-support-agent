"""
Application configuration and thresholds for the Persona-Adaptive Customer Support Agent.
Loads environment variables and defines global constants used across all modules.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ──────────────────────────────────────────────
# API Configuration
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-2"

# ──────────────────────────────────────────────
# RAG Pipeline Settings
# ──────────────────────────────────────────────
CHUNK_SIZE = 400          # Character length per chunk
CHUNK_OVERLAP = 50        # Overlap between adjacent chunks
TOP_K = 3                 # Number of top results to retrieve
CHROMA_DB_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "support_kb"

# ──────────────────────────────────────────────
# Escalation Thresholds
# ──────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.40   # Minimum cosine similarity score before escalation
FRUSTRATION_TURN_LIMIT = 3    # Consecutive frustrated turns before escalation

# ──────────────────────────────────────────────
# Sensitive Topic Keywords (triggers human handoff)
# ──────────────────────────────────────────────
SENSITIVE_KEYWORDS = [
    "refund", "billing dispute", "legal", "lawsuit", "attorney",
    "cancel subscription", "unauthorized charge", "fraud",
    "account deletion", "data breach", "privacy violation",
    "discrimination", "harassment", "compliance"
]

# ──────────────────────────────────────────────
# Data Directory
# ──────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ──────────────────────────────────────────────
# Persona Definitions
# ──────────────────────────────────────────────
PERSONAS = ["Technical Expert", "Frustrated User", "Business Executive"]
