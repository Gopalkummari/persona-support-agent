"""
Persona-Adaptive Customer Support Agent — Streamlit Chat UI

Main application entry point. Provides an interactive chat interface with:
- Real-time persona classification display
- RAG-powered context retrieval
- Persona-adaptive response generation
- Automatic escalation detection with human handoff
- Conversation history with session state

Usage:
    streamlit run app.py
"""

import time
import random
import streamlit as st

from src.config import DATA_DIR, GEMINI_API_KEY
from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.generator import generate_adaptive_response
from src.escalator import check_escalation, generate_escalation_report


# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Persona Support Agent",
    page_icon="app_shortcut",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# Custom CSS for premium styling
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main .block-container {
        padding-top: 3rem;
        max-width: 900px;
    }

    /* Chat bubble tweaks */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1rem 1.5rem;
    }

    /* Title styling */
    .app-title {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 16px;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Retry wrapper with exponential backoff
# ──────────────────────────────────────────────
def call_with_backoff(func, *args, max_retries=5, **kwargs):
    """
    Call a function with exponential backoff retry logic
    to handle API rate limits and transient errors.
    """
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)


# ──────────────────────────────────────────────
# Initialize session state
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "current_persona" not in st.session_state:
    st.session_state.current_persona = None

if "current_confidence" not in st.session_state:
    st.session_state.current_confidence = 0.0

if "current_reasoning" not in st.session_state:
    st.session_state.current_reasoning = ""

if "current_sources" not in st.session_state:
    st.session_state.current_sources = []

if "last_escalation" not in st.session_state:
    st.session_state.last_escalation = None

if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None


# ──────────────────────────────────────────────
# Initialize RAG Pipeline
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_rag_pipeline():
    """Initialize the RAG pipeline and ingest documents if needed."""
    pipeline = LocalRAGPipeline()
    if not pipeline.is_indexed():
        pipeline.ingest_all_documents(DATA_DIR)
    return pipeline


# ──────────────────────────────────────────────
# Main Chat Interface
# ──────────────────────────────────────────────
def main():
    """Main application entry point."""

    # Header
    st.markdown('<p class="app-title">Persona-Adaptive Support Agent</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-subtitle">Intelligent customer support that adapts to your communication style</p>',
        unsafe_allow_html=True
    )

    # Initialize RAG pipeline
    with st.spinner("Initializing knowledge base..."):
        pipeline = init_rag_pipeline()
        st.session_state.rag_pipeline = pipeline

    # Minimal Sidebar
    with st.sidebar:
        if st.button("Clear Chat", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.current_persona = None
            st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_input := st.chat_input("Type your support question here..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process the message
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your message..."):
                try:
                    # Step 1: Classify persona
                    classification = call_with_backoff(
                        classify_customer_persona, user_input
                    )
                    persona = classification.get("persona", "Frustrated User")
                    confidence = classification.get("confidence", 0.0)
                    reasoning = classification.get("reasoning", "")

                    # Update session state
                    st.session_state.current_persona = persona
                    st.session_state.current_confidence = confidence
                    st.session_state.current_reasoning = reasoning

                    # Step 2: Retrieve context from RAG
                    context_chunks = call_with_backoff(
                        pipeline.retrieve_context, user_input
                    )
                    st.session_state.current_sources = context_chunks

                    # Step 3: Check escalation triggers
                    escalation_check = check_escalation(
                        context_chunks,
                        user_input,
                        st.session_state.conversation_history
                    )
                    st.session_state.last_escalation = escalation_check

                    # Step 4: Generate response
                    if escalation_check["should_escalate"]:
                        # Generate escalation report
                        report = generate_escalation_report(
                            user_input,
                            persona,
                            context_chunks,
                            escalation_check["reasons"],
                            st.session_state.conversation_history
                        )

                        response_text = (
                            "I understand your concern, and I want to make sure you get the best "
                            "possible assistance. Based on the nature of your request, I'm connecting "
                            "you with a specialized human support agent who can help you directly.\n\n"
                            "**Your case has been escalated** with all relevant context. "
                            "A support specialist will review your case shortly.\n\n"
                            f"**Escalation Reason(s):**\n"
                        )
                        for reason in escalation_check["reasons"]:
                            response_text += f"- {reason}\n"

                        st.markdown(response_text)

                        # Save to messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text
                        })
                    else:
                        # Generate adaptive response
                        result = call_with_backoff(
                            generate_adaptive_response,
                            user_input,
                            persona,
                            context_chunks
                        )

                        if result["escalated"]:
                            # Generator-level escalation (low confidence)
                            st.markdown(result["response"])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["response"]
                            })
                        else:
                            st.markdown(result["response"])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["response"]
                            })

                    # Update conversation history for frustration tracking
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": user_input,
                        "persona": persona
                    })

                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

        # Rerun to update sidebar
        st.rerun()


if __name__ == "__main__":
    main()
