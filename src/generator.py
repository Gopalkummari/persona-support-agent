"""
Adaptive Response Generator Module.

Combines the classified persona, retrieved context chunks, and the user's query
to generate a persona-adaptive response using Google Gemini. Handles escalation
logic when confidence is too low or sensitive topics are detected.
"""

import os
import json
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL, CONFIDENCE_THRESHOLD


# ──────────────────────────────────────────────
# Persona-specific system prompt templates
# ──────────────────────────────────────────────

PERSONA_TEMPLATES = {
    "Technical Expert": (
        "You are a Senior Systems Engineer speaking to a technically proficient customer. "
        "Provide clear root-cause analysis, configuration specifications, and precise API "
        "pathways or code blocks. Use structured formatting with numbered steps, code snippets, "
        "and technical terminology. Keep descriptions exact, systematic, and thorough. "
        "Include relevant log analysis pointers and architectural diagnostics where applicable."
    ),
    "Frustrated User": (
        "You are a deeply empathetic, reassuring Customer Care Specialist. "
        "Begin EVERY response with a warm, genuine validation of their difficulty "
        "(e.g., 'I completely understand how frustrating this must be...'). "
        "Use straightforward, reassuring language with simple action-oriented bullet steps. "
        "Avoid confusing jargon or overly technical explanations. Focus on making the customer "
        "feel heard and guiding them step-by-step to a resolution."
    ),
    "Business Executive": (
        "You are a concise Client Relations Director speaking to a business executive. "
        "Focus on direct business outcomes, impact summaries, and timelines for resolution. "
        "Keep responses extremely brief, professional, and executive-friendly. "
        "Skip unnecessary configuration details. Use bullet points for key actions "
        "and always include estimated resolution timeframes."
    ),
}


def generate_adaptive_response(
    user_query: str,
    persona: str,
    context_chunks: list
) -> dict:
    """
    Generate a personalized response matching the classified user archetype.
    If context confidence is too low, the issue is flagged for escalation.

    Args:
        user_query:     The user's support query.
        persona:        The classified persona (Technical Expert / Frustrated User / Business Executive).
        context_chunks: List of dicts from RAG retrieval, each with 'text', 'source', and 'score'.

    Returns:
        A dict with keys:
          - escalated (bool): Whether the query was escalated.
          - response (str):   The generated response text or an escalation message.
          - handoff_summary (str|None): JSON handoff data if escalated.
    """
    # 1. Escalation check — low retrieval confidence
    best_score = max([chunk["score"] for chunk in context_chunks]) if context_chunks else 0.0

    if best_score < CONFIDENCE_THRESHOLD or len(context_chunks) == 0:
        return {
            "escalated": True,
            "response": (
                "I apologize, but I am unable to locate the precise solution to your request "
                "in our knowledge base. I am connecting you with a live human support specialist "
                "who can assist you further."
            ),
            "handoff_summary": generate_handoff_summary(user_query, persona, context_chunks)
        }

    # 2. Select persona-specific system prompt
    persona_instructions = PERSONA_TEMPLATES.get(persona, PERSONA_TEMPLATES["Frustrated User"])

    # 3. Assemble the context-grounded system prompt
    context_text = "\n\n".join(
        [f"Source [{c['source']}]: {c['text']}" for c in context_chunks]
    )

    full_system_prompt = (
        f"{persona_instructions}\n\n"
        "CRITICAL RULES:\n"
        "- Base your response ONLY on the provided context documents below.\n"
        "- Do NOT hallucinate or assume facts not found in the documents.\n"
        "- If the context does not contain enough information, say so honestly.\n"
        "- Always be helpful, accurate, and professional.\n\n"
        f"FACTUAL CONTEXT DOCUMENTS:\n{context_text}"
    )

    # 4. Call Gemini
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_query,
        config=types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            temperature=0.2
        )
    )

    return {
        "escalated": False,
        "response": response.text,
        "handoff_summary": None
    }


def generate_handoff_summary(
    user_query: str,
    persona: str,
    context_chunks: list
) -> str:
    """
    Compile a structured JSON handoff report for escalation to a human agent.

    Args:
        user_query:     The user's original support query.
        persona:        The classified customer persona.
        context_chunks: Retrieved context chunks (may be empty or low-confidence).

    Returns:
        A formatted JSON string containing the handoff data.
    """
    handoff_data = {
        "escalation_type": "automated_handoff",
        "persona": persona,
        "detected_issue": user_query[:200] + ("..." if len(user_query) > 200 else ""),
        "retrieved_sources": [c["source"] for c in context_chunks],
        "best_confidence_score": max([c["score"] for c in context_chunks]) if context_chunks else 0.0,
        "context_snippets": [c["text"][:150] for c in context_chunks[:2]],
        "recommended_action": (
            "Review the customer's query manually. The automated system could not find "
            "a high-confidence match in the knowledge base. Check system error codes, "
            "review API logs, and contact the user directly."
        ),
    }
    return json.dumps(handoff_data, indent=2)
