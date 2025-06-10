import streamlit as st
from config import get_config
from backend.projcore import run_llm
from typing import List, Dict, Any

# Get configuration
config = get_config()

# Project 2025 specific instructions
INSTRUCTIONS_TEXT = """
This bot helps you understand and analyze Project 2025, a comprehensive plan for the next conservative administration. 
Here's how to use it:

1. **Type your question** about Project 2025 in the prompt box. You can ask about specific policies, plans, or get a general analysis.
2. Click Submit or "Cntrl + Enter" to get an AI-generated response

**Examples of questions you can ask:**
* General questions
    * What are the main goals of Project 2025?
    * How does Project 2025 plan to handle immigration?
* Specific policy areas
    * What are Project 2025's plans for education reform?
    * How does Project 2025 propose to restructure the federal government?
* Historical context
    * How does Project 2025 compare to previous conservative policy initiatives?
* Implementation details
    * What is the timeline for implementing Project 2025's proposals?
    * Which federal agencies would be most affected by Project 2025?
"""

# Set page config
st.set_page_config(
    page_title="Project 2025",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            sources_string += f"URL: {url}\n\n"
            count += 1

    return sources_string if unique_urls else "No unique sources found."

def initialize_session_state() -> None:
    """Initialize session state variables if they don't exist."""
    if "proj2025_chat_answers_history" not in st.session_state:
        st.session_state["proj2025_user_prompt_history"] = []
        st.session_state["proj2025_chat_answers_history"] = []
        st.session_state["proj2025_chat_history"] = []

def clear_chat_history() -> None:
    """Clear all chat history from session state."""
    st.session_state["proj2025_user_prompt_history"] = []
    st.session_state["proj2025_chat_answers_history"] = []
    st.session_state["proj2025_chat_history"] = []
    st.rerun()

def display_chat_history() -> None:
    """Display the chat history in the UI."""
    if st.session_state["proj2025_chat_answers_history"]:
        for generate_response, user_query in zip(st.session_state["proj2025_chat_answers_history"], st.session_state["proj2025_user_prompt_history"]):
            st.chat_message("user").write(user_query)
            st.chat_message("assistant").write(generate_response)

def handle_chat_submission(prompt: str) -> None:
    """Handle the chat submission and update session state."""
    try:
        with st.spinner("Generating response..."):
            generate_response = run_llm(query=prompt, chat_history=st.session_state["proj2025_chat_history"])
            # formatted_sources = format_source_documents(generate_response["source_documents"])
            formatted_response_with_sources = f"{generate_response['result']}"

            st.session_state["proj2025_user_prompt_history"].append(prompt)
            st.session_state["proj2025_chat_answers_history"].append(formatted_response_with_sources)
            st.session_state["proj2025_chat_history"].append(("human", prompt))
            st.session_state["proj2025_chat_history"].append(("ai", generate_response["result"]))
            
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
    .stApp {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        margin-bottom: 0px;
        margin-top: 0.5rem !important;
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
    .main-flex {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
        margin-top: 1.5rem;
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

# Apply CSS
st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# Add sidebar content
with st.sidebar:
    # Custom Navigation

    st.page_link("main.py", label="Executive Orders", icon="📋")
    st.page_link("pages/proj2025.py", label="Project 2025", icon="📚")
    
    st.markdown("---")  # Add a separator
    
    # Instructions section
    st.header("Instructions")
    st.markdown(INSTRUCTIONS_TEXT)
    
    # Developer information section
    st.markdown("---")  # Add a separator
    st.header("Developer Information")
    st.markdown(config["dev_info"])

# Main content
st.title("Project 2025 Analyzer")

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
        placeholder="Enter your question about Project 2025...",
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