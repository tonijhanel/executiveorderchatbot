import streamlit as st
from typing import List, Dict, Any, Tuple

from backend.core import run_llm
from config import get_config

# Get configuration
config = get_config()

# Constants
SIDEBAR_BG_COLOR = "#19253F"
TEXT_COLOR = "#FFFFFF"
HEADER_COLOR = "#19253F"

# Helper Functions
def format_source_documents(source_documents: List[Dict]) -> str:
    """Formats the source documents into a readable string, ensuring only unique sources are included."""
    if not source_documents:
        return ""

    sources_string = "Sources:\n\n"
    unique_urls = set()
    count = 0
    for doc in source_documents:
        if count >= config["api"]["MAX_SOURCES"]:
            break
        url = doc.metadata.get('html_url', None)
        if url and url not in unique_urls:
            unique_urls.add(url)
            sources_string += f"--- Source ---\n"
            sources_string += f"URL: {url}\n"
            # Convert executive order number to string and remove decimal places
            eo_number = doc.metadata.get('executive_order_number', 'N/A')
            if isinstance(eo_number, float):
                eo_number = str(int(eo_number))
            sources_string += f"Executive Order Number: {eo_number}\n\n"
            count += 1

    return sources_string if unique_urls else "No unique sources found."

def create_sources_string(sources_urls: set[str]) -> str:
    """Creates a formatted string of source URLs."""
    if not sources_urls:
        return ""
    sources_list = list(sources_urls)
    return "sources:\n" + "\n".join(f"{i+1}. {source}" for i, source in enumerate(sources_list))

def initialize_session_state() -> None:
    """Initialize session state variables if they don't exist."""
    if "chat_answers_history" not in st.session_state:
        st.session_state["user_prompt_history"] = []
        st.session_state["chat_answers_history"] = []
        st.session_state["chat_history"] = []

def clear_chat_history() -> None:
    """Clear all chat history from session state."""
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []
    st.rerun()

def display_chat_history() -> None:
    """Display the chat history in the UI."""
    if st.session_state["chat_answers_history"]:
        for generate_response, user_query in zip(st.session_state["chat_answers_history"], st.session_state["user_prompt_history"]):
            st.chat_message("user").write(user_query)
            st.chat_message("assistant").write(generate_response)

def handle_chat_submission(prompt: str) -> None:
    """Handle the chat submission and update session state."""
    try:
        with st.spinner("Generating response..."):
            generate_response = run_llm(query=prompt, chat_history=st.session_state["chat_history"])
            sources = set(doc.metadata["html_url"] for doc in generate_response["source_documents"])
            formatted_sources = format_source_documents(generate_response["source_documents"])
            formatted_response_with_sources = f"{generate_response['result']} \n\n {formatted_sources}"

            st.session_state["user_prompt_history"].append(prompt)
            st.session_state["chat_answers_history"].append(formatted_response_with_sources)
            st.session_state["chat_history"].append(("human", prompt))
            st.session_state["chat_history"].append(("ai", generate_response["result"]))
            
            st.rerun()
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        st.stop()

# CSS Styles
SIDEBAR_CSS = f"""
    <style>
    section[data-testid="stSidebar"] {{
        background-color: {config['ui']['SIDEBAR_BG_COLOR']} !important;
        color: {config['ui']['TEXT_COLOR']} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {config['ui']['TEXT_COLOR']} !important;
    }}
    </style>
"""

MAIN_CSS = """
    <style>
    .main {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #19253F !important;
        font-family: 'Georgia', 'Times New Roman', Times, serif !important;
        font-weight: 600 !important;
        letter-spacing: -1px;
    }
    /* Subtext and meta info */
    .subtext, .meta-info {
        color: #6B7280 !important;
        font-size: 1rem !important;
        font-family: 'Georgia', 'Times New Roman', Times, serif !important;
    }
    /* Executive order list styling */
    .eo-title {
        font-size: 2.2rem;
        font-family: "Arial", sans-serif;
        font-weight: 500;
        margin-bottom: 0.2rem;
        margin-top: 2.2rem;
        color: #19253F;
    }
    .eo-meta {
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    /* Optional: Add a subtle divider */
    .eo-divider {
        border-bottom: 1px solid #E5E7EB;
        margin: 1.5rem 0;
    }
    .stApp {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        margin-bottom: 0px; /* Space for input form */
        margin-top: 0.5rem !important; /* Reduce space above chat */
    }
    .input-form {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 0;
        border-top: 1px solid #e0e0e0;
        z-index: 100;
    }
    .stTextInput > div > div > textarea {
        min-height: 100px !important;
        resize: vertical !important;
    }
    .button-col {
        display: flex;
        align-items: flex-end;  /* Bottom align */
        height: 100%;
        justify-content: center;
    }
    .button-align-bottom {
        height: 100%;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }
    /* Reduce space below the header */
    h1, .stMarkdown h1 {
        margin-bottom: 0.5rem !important;
    }
    /* Reduce default block spacing */
    section.main > div.block-container {
        padding-top: 1rem !important;
    }
    /* Reduce space for stElementContainer */
    .stElementContainer {
        min-height: 0 !important;
       
        margin: 0 !important;
        padding: 0 !important;
    }
    .main-flex {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem; /* Adjust this for spacing between header and chat */
        margin-top: 1.5rem; /* Adjust or remove as needed */
    }
    .input-row {
        display: flex;
        flex-direction: row;
        align-items: flex-end;
        gap: 1rem;
        width: 100%;
    }
    .input-row textarea {
        flex: 4;
        min-height: 100px;
        resize: vertical;
    }
    .input-row .submit-btn {
        flex: 1;
        height: 40px;
        align-self: flex-end;
    }
    </style>
"""

# Add sidebar content
with st.sidebar:
    # Instructions section
    st.header("Instructions")
    st.markdown(config["instructions"])
    
    
    
    # Developer information section
    st.markdown("---")  # Add a separator
    st.header("Developer Information")
    st.markdown(config["dev_info"])

# Apply CSS
st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# Main UI
st.header(config["ui"]["APP_TITLE"])

# Initialize session state
initialize_session_state()

# Create the main chat interface
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
display_chat_history()
st.markdown('</div>', unsafe_allow_html=True)

# Create the input form
st.markdown('<div class="input-form main-flex">', unsafe_allow_html=True)
with st.form("prompt_form", clear_on_submit=True):
    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    prompt = st.text_area(
        "Prompt",
        placeholder=config["chat"]["PROMPT_PLACEHOLDER"],
        key="prompt_input",
        height=config["chat"]["TEXT_AREA_HEIGHT"]
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        submit_button = st.form_submit_button("Submit", type="primary")
    with col2:
        clear_button = st.form_submit_button("Clear Chat", type="secondary")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle form submissions
if prompt and submit_button:
    handle_chat_submission(prompt)

if clear_button:
    clear_chat_history()