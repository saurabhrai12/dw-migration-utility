import streamlit as st
import requests
import json
import os
import uuid
import time
from database import init_database, log_interaction, get_session_history, get_statistics

# LLM API Configuration
LLM_API_URL = "http://127.0.0.1:1234/v1/chat/completions"
LLM_MODEL = "claude-3.7-sonnet-reasoning-gemma3-12b"

# File to store saved prompts
SAVED_PROMPTS_FILE = "saved_prompts.json"

# Load saved prompts from file
def load_saved_prompts():
    """Load saved prompts from JSON file"""
    if os.path.exists(SAVED_PROMPTS_FILE):
        try:
            with open(SAVED_PROMPTS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

# Save prompts to file
def save_prompts_to_file(prompts):
    """Save prompts to JSON file"""
    try:
        with open(SAVED_PROMPTS_FILE, 'w') as f:
            json.dump(prompts, f, indent=2)
    except Exception as e:
        st.error(f"Error saving prompts: {str(e)}")

# Function to call LLM API with streaming
def call_llm_stream(messages, placeholder, session_id):
    """Call the local LLM API with streaming for real-time responses"""
    start_time = time.time()
    user_message = messages[-1]["content"] if messages else ""

    try:
        payload = {
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True
        }

        response = requests.post(LLM_API_URL, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]  # Remove 'data: ' prefix
                    if line.strip() == '[DONE]':
                        break
                    try:
                        chunk = json.loads(line)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_response += content
                                placeholder.markdown(full_response + "▌")
                    except json.JSONDecodeError:
                        continue

        placeholder.markdown(full_response)

        # Calculate response time and log interaction
        response_time = time.time() - start_time
        log_interaction(
            session_id=session_id,
            user_message=user_message,
            assistant_response=full_response,
            model_used=LLM_MODEL,
            response_time=response_time,
            tokens_used=None,  # Could be extracted from response if available
            metadata={"status": "success"}
        )

        return full_response

    except requests.exceptions.Timeout:
        error_msg = "⚠️ The request timed out. The LLM is taking longer than expected to respond. Please try again with a shorter prompt or check if the LLM server is running properly."
        placeholder.markdown(error_msg)

        # Log error
        response_time = time.time() - start_time
        log_interaction(
            session_id=session_id,
            user_message=user_message,
            assistant_response=error_msg,
            model_used=LLM_MODEL,
            response_time=response_time,
            metadata={"status": "timeout", "error": "Request timed out"}
        )

        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Cannot connect to the LLM server at http://127.0.0.1:1234. Please make sure the LLM server is running."
        placeholder.markdown(error_msg)

        # Log error
        response_time = time.time() - start_time
        log_interaction(
            session_id=session_id,
            user_message=user_message,
            assistant_response=error_msg,
            model_used=LLM_MODEL,
            response_time=response_time,
            metadata={"status": "connection_error", "error": "Cannot connect to LLM server"}
        )

        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error connecting to LLM: {str(e)}"
        placeholder.markdown(error_msg)

        # Log error
        response_time = time.time() - start_time
        log_interaction(
            session_id=session_id,
            user_message=user_message,
            assistant_response=error_msg,
            model_used=LLM_MODEL,
            response_time=response_time,
            metadata={"status": "request_error", "error": str(e)}
        )

        return error_msg
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        placeholder.markdown(error_msg)

        # Log error
        response_time = time.time() - start_time
        log_interaction(
            session_id=session_id,
            user_message=user_message,
            assistant_response=error_msg,
            model_used=LLM_MODEL,
            response_time=response_time,
            metadata={"status": "unknown_error", "error": str(e)}
        )

        return error_msg

# Configure page
st.set_page_config(
    page_title="Jarvis",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Minimal custom CSS - mostly relying on Streamlit's native styling
st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 2rem;
        max-width: 900px;
        margin-left: 0 !important;
        margin-right: auto !important;
    }

    /* Center header container */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .header-icon {
        font-size: 5rem;
        line-height: 1;
    }

    .header-title {
        font-size: 3.5rem;
        font-weight: 600;
        margin: 0;
    }

    /* Center chat input */
    .stChatInputContainer {
        max-width: 700px;
        margin: 2rem auto;
    }

    /* Increase text input size */
    .stTextInput input {
        font-size: 1.1rem !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        height: 3.5rem !important;
        text-align: left !important;
    }

    /* Increase chat input size */
    .stChatInputContainer textarea {
        font-size: 1.1rem !important;
        padding: 1rem !important;
        min-height: 3.5rem !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        min-width: 250px;
    }

    /* Remove top padding from sidebar content */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }

    /* Remove top padding from sidebar block container */
    [data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
    }

    /* Reduce font size for sidebar buttons */
    [data-testid="stSidebar"] button {
        font-size: 0.85rem !important;
    }

    /* Single line display for sidebar buttons */
    [data-testid="stSidebar"] button div {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* Smaller delete buttons */
    [data-testid="stSidebar"] button[kind="secondary"] {
        font-size: 0.7rem !important;
        padding: 0.25rem 0.5rem !important;
        min-height: 1.5rem !important;
    }

    /* Hide only the main menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize database
init_database()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "saved_prompts" not in st.session_state:
    st.session_state["saved_prompts"] = load_saved_prompts()

# Generate unique session ID
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

with st.sidebar:
    # Logo at the top of the sidebar
    logo_col = st.columns([1, 2, 1])[1]
    logo_col.image("logo.png", width=140)

    # Model information dictionary
    MODEL_INFO = {
        "GPT-4": {
            "description": "Most capable GPT-4 model",
            "context": "8K tokens",
            "strengths": "Complex reasoning, creative tasks"
        },
        "GPT-4 Turbo": {
            "description": "Faster GPT-4 with larger context",
            "context": "128K tokens",
            "strengths": "Speed, long documents"
        },
        "GPT-3.5 Turbo": {
            "description": "Fast and efficient model",
            "context": "16K tokens",
            "strengths": "Quick responses, cost-effective"
        },
        "Claude 3.5 Sonnet": {
            "description": "Balanced performance model",
            "context": "200K tokens",
            "strengths": "Analysis, code generation"
        },
        "Claude 3 Opus": {
            "description": "Most powerful Claude model",
            "context": "200K tokens",
            "strengths": "Complex tasks, reasoning"
        },
        "Gemini Pro": {
            "description": "Google's advanced model",
            "context": "32K tokens",
            "strengths": "Multimodal, versatile"
        }
    }

    selected_model = st.selectbox(
        "Select Model",
        options=list(MODEL_INFO.keys()),
        index=0,
        key="model_selector",
        help="Choose an AI model for your conversations"
    )

    # Display model info
    if selected_model in MODEL_INFO:
        info = MODEL_INFO[selected_model]
        with st.expander(f"ℹ️ {selected_model} Details", expanded=False):
            st.markdown(f"**Description:** {info['description']}")
            st.markdown(f"**Context Window:** {info['context']}")
            st.markdown(f"**Best for:** {info['strengths']}")

    # Saved prompts section
    st.markdown("#### Saved Prompts")

    if len(st.session_state.saved_prompts) > 0:
        for i, prompt in enumerate(st.session_state.saved_prompts):
            col1, col2 = st.columns([4, 1])

            with col1:
                # Display prompt with ellipsis for long text
                if st.button(prompt, key=f"saved_{i}", use_container_width=True, help=prompt):
                    # Add the prompt to messages again
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.rerun()

            with col2:
                # Delete button with smaller size
                if st.button("🗑️", key=f"delete_saved_{i}", type="secondary"):
                    st.session_state.saved_prompts.pop(i)
                    save_prompts_to_file(st.session_state.saved_prompts)
                    st.rerun()
    else:
        st.markdown("*No saved prompts yet*")

    # Recent prompts section
    st.markdown("#### Recent Prompts")

    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        # Get unique user messages (prompts only)
        user_prompts = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]

        # Show last 5 prompts
        recent_prompts = user_prompts[-5:][::-1]  # Reverse to show most recent first

        for i, prompt in enumerate(recent_prompts):
            # Display with ellipsis and tooltip showing full prompt
            if st.button(prompt, key=f"recent_{i}", use_container_width=True, help=prompt):
                # Add the prompt to messages again
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    else:
        st.markdown("*No recent prompts yet*")

    st.markdown("#### Help & Support")
    st.markdown("📧 [Contact us for queries](mailto:support@jarvis.ai)")
    st.markdown("💡 [View Documentation](https://docs.jarvis.ai)")

# Sample queries configuration (shown before chat starts)
SAMPLE_QUERIES = {
    ":blue[📚 What is Streamlit?]": "What is Streamlit?",
    ":green[🔄 How does session state work?]": "How does session state work?",
    ":orange[📊 Show me an example chart]": "Show me an example chart",
    ":violet[🎨 How to customize the theme?]": "How to customize the theme?",
    ":red[🚀 How do I deploy my app?]": "How do I deploy my app?"
}

# Show welcome screen when no messages exist
if len(st.session_state.messages) == 0:
    # Create left-aligned container for input and samples
    st.markdown("<div style='max-width: 700px;'>", unsafe_allow_html=True)

    # Welcome message
    st.markdown("<h1 style='text-align: left; font-size: 3rem; font-weight: 600; margin-bottom: 1.5rem;'>Welcome! How can I help you today?</h1>", unsafe_allow_html=True)

    # Text input that can be positioned above sample queries
    initial_query = st.text_input(
        "question",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        key="initial_input"
    )

    # Add space before sample queries
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Sample queries below the input
    #st.markdown("##### Try asking:")
    selected = st.pills(
        label="Examples",
        options=list(SAMPLE_QUERIES.keys()),
        label_visibility="collapsed",
        selection_mode="single"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Handle text input submission
    if initial_query:
        st.session_state.messages.append({"role": "user", "content": initial_query})
        st.rerun()

    # Handle pill selection
    if selected:
        query = SAMPLE_QUERIES[selected]
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()

# Display chat messages
else:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

            # Add save button for user messages
            if msg["role"] == "user":
                prompt_content = msg["content"]
                # Check if already saved
                if prompt_content not in st.session_state.saved_prompts:
                    if st.button("💾 Save", key=f"save_msg_{idx}"):
                        st.session_state.saved_prompts.append(prompt_content)
                        save_prompts_to_file(st.session_state.saved_prompts)
                        st.rerun()
                else:
                    st.caption("⭐ Saved")

    # Generate response if last message is from user
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            placeholder = st.empty()
            response_content = call_llm_stream(
                st.session_state.messages,
                placeholder,
                st.session_state.session_id
            )

        st.session_state.messages.append({"role": "assistant", "content": response_content})
        st.rerun()

# Chat input at bottom for ongoing conversation
if len(st.session_state.messages) > 0:
    prompt = st.chat_input("Ask a follow-up...")

# Handle user input from bottom chat input
if len(st.session_state.messages) > 0 and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Get response from LLM with streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_content = call_llm_stream(
            st.session_state.messages,
            placeholder,
            st.session_state.session_id
        )

    st.session_state.messages.append({"role": "assistant", "content": response_content})
