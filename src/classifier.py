"""
Persona Classification Module.

Analyzes the user's support message and classifies it into one of three
customer personas using Google Gemini with structured JSON output:
  - Technical Expert
  - Frustrated User
  - Business Executive
"""

import os
import json
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL


def classify_customer_persona(user_message: str) -> dict:
    """
    Analyzes the user's message and classifies it into one of the three target personas.

    Args:
        user_message: The incoming customer support message.

    Returns:
        A dict with keys: persona (str), confidence (float), reasoning (str).
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    system_instruction = (
        "You are an advanced classification engine. Your task is to analyze the "
        "sentiment, vocabulary, and tone of an incoming support message and classify "
        "it into exactly one of three customer personas:\n"
        "1. 'Technical Expert': Uses jargon, asks about APIs/code/configs, references "
        "logs, error codes, or system architecture. Tone is analytical and precise.\n"
        "2. 'Frustrated User': Uses emotional language, exclamation marks, mentions "
        "urgency, expresses dissatisfaction, or describes inconvenience. Tone is upset or impatient.\n"
        "3. 'Business Executive': Focuses on business impact, ROI, timelines, team "
        "productivity, and brevity. Tone is formal and outcome-oriented.\n\n"
        "Provide your evaluation strictly in the requested JSON structure."
    )

    # Define structured schema for JSON output
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "persona": {
                "type": "STRING",
                "enum": ["Technical Expert", "Frustrated User", "Business Executive"]
            },
            "confidence": {"type": "NUMBER"},
            "reasoning": {"type": "STRING"}
        },
        "required": ["persona", "confidence", "reasoning"]
    }

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.1
        )
    )

    return json.loads(response.text)


# ──────────────────────────────────────────────
# Standalone test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    test_messages = [
        "Our production API key stopped working with a 401 Unauthorized block. Check our logs immediately.",
        "Where is the guide to clear cookies? It's been an hour and nothing is loading on your interface!",
        "Our operational uptime is decreasing. We need a timeline of when billing disputes are resolved.",
    ]

    for msg in test_messages:
        result = classify_customer_persona(msg)
        print(f"\nMessage: {msg}")
        print(json.dumps(result, indent=2))
