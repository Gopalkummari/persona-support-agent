"""
Escalation Engine Module.

Evaluates whether a customer support query should be escalated to a human agent
based on three trigger conditions:
  1. Low retrieval confidence (cosine similarity below threshold)
  2. Sensitive topic detection (billing, refund, legal keywords)
  3. Repeated frustration across consecutive conversation turns
"""

import json
from src.config import CONFIDENCE_THRESHOLD, SENSITIVE_KEYWORDS, FRUSTRATION_TURN_LIMIT


def check_escalation(
    context_chunks: list,
    user_query: str,
    conversation_history: list = None
) -> dict:
    """
    Evaluate whether the current interaction should be escalated to a human agent.

    Args:
        context_chunks:       List of retrieved context dicts with 'score' keys.
        user_query:           The user's current support message.
        conversation_history: List of past turn dicts with optional 'persona' keys.

    Returns:
        A dict with:
          - should_escalate (bool): Whether to escalate.
          - reasons (list[str]):    List of triggered escalation reasons.
    """
    reasons = []

    # ── Trigger 1: Low Retrieval Confidence ──
    if context_chunks:
        best_score = max(chunk["score"] for chunk in context_chunks)
        if best_score < CONFIDENCE_THRESHOLD:
            reasons.append(
                f"Low retrieval confidence: best score {best_score:.4f} "
                f"is below threshold {CONFIDENCE_THRESHOLD}"
            )
    else:
        reasons.append("No relevant documents found in the knowledge base")

    # ── Trigger 2: Sensitive Topic Detection ──
    query_lower = user_query.lower()
    detected_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in query_lower]
    if detected_keywords:
        reasons.append(
            f"Sensitive topic detected: {', '.join(detected_keywords)}"
        )

    # ── Trigger 3: Repeated Frustration ──
    if conversation_history:
        recent_personas = [
            turn.get("persona", "")
            for turn in conversation_history[-FRUSTRATION_TURN_LIMIT:]
        ]
        consecutive_frustrated = sum(
            1 for p in recent_personas if p == "Frustrated User"
        )
        if consecutive_frustrated >= FRUSTRATION_TURN_LIMIT:
            reasons.append(
                f"Repeated frustration detected: {consecutive_frustrated} consecutive "
                f"turns classified as 'Frustrated User'"
            )

    return {
        "should_escalate": len(reasons) > 0,
        "reasons": reasons
    }


def generate_escalation_report(
    user_query: str,
    persona: str,
    context_chunks: list,
    escalation_reasons: list,
    conversation_history: list = None
) -> str:
    """
    Generate a structured JSON escalation report for human agent handoff.

    Args:
        user_query:           The user's support query.
        persona:              The classified customer persona.
        context_chunks:       Retrieved context chunks.
        escalation_reasons:   List of reasons triggering escalation.
        conversation_history: Full conversation history for context.

    Returns:
        A formatted JSON string containing the escalation report.
    """
    # Summarize recent conversation
    recent_messages = []
    if conversation_history:
        for turn in conversation_history[-5:]:  # Last 5 turns
            recent_messages.append({
                "role": turn.get("role", "unknown"),
                "message_preview": turn.get("content", "")[:150],
                "persona": turn.get("persona", "N/A")
            })

    report = {
        "escalation_report": {
            "type": "human_handoff",
            "priority": _determine_priority(escalation_reasons),
            "customer_persona": persona,
            "current_query": user_query[:300],
            "escalation_reasons": escalation_reasons,
            "retrieval_results": {
                "documents_found": len(context_chunks),
                "best_confidence": max(
                    (c["score"] for c in context_chunks), default=0.0
                ),
                "sources": [c["source"] for c in context_chunks]
            },
            "conversation_context": recent_messages,
            "recommended_actions": [
                "Review the customer's full query and conversation history",
                "Check internal systems for relevant information not in the knowledge base",
                "Contact the customer directly if the issue is time-sensitive",
                "Update the knowledge base if this represents a common query gap"
            ]
        }
    }
    return json.dumps(report, indent=2)


def _determine_priority(reasons: list) -> str:
    """
    Determine escalation priority based on the triggered reasons.

    Returns: 'critical', 'high', or 'medium'
    """
    reason_text = " ".join(reasons).lower()

    # Critical: sensitive + frustration combined, or legal/fraud
    if any(word in reason_text for word in ["fraud", "legal", "lawsuit", "attorney"]):
        return "critical"

    # High: sensitive topics or repeated frustration
    if "sensitive topic" in reason_text or "repeated frustration" in reason_text:
        return "high"

    # Medium: low confidence only
    return "medium"
