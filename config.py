import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# UI Constants
UI_CONFIG = {
    "SIDEBAR_BG_COLOR": "#19253F",
    "TEXT_COLOR": "#FFFFFF",
    "HEADER_COLOR": "#19253F",
    "APP_TITLE": "Presidential Executive Order Analyzer",
    "APP_VERSION": "1.0.0",
    "DEVELOPER_NAME": "Toni Williams",
    "DEVELOPER_GITHUB": "https://github.com/tonijhanel/executiveorderchatbot",
}

# API Configuration
API_CONFIG = {
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
    "PINECONE_INDEX": os.getenv("PINECONE_INDEX", "executiveorderscleantxt"),
    "MAX_SOURCES": int(os.getenv("MAX_SOURCES", "2")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0")),
}

# Chat Configuration
CHAT_CONFIG = {
    "MAX_HISTORY_LENGTH": int(os.getenv("MAX_HISTORY_LENGTH", "10")),
    "PROMPT_PLACEHOLDER": "Enter your prompt here...",
    "TEXT_AREA_HEIGHT": int(os.getenv("TEXT_AREA_HEIGHT", "100")),
}

# Instructions text
INSTRUCTIONS_TEXT = """
This bot helps you understand and analyze Presidential Executive Orders. 
It uses executive orders from the White House, dating back to 2021 to present. 
Here's how to use it:

1. **Type your question** related to Executive Orders in the prompt box. If you want sentiment analysis and a summary, make sure to ask for it explicitly.
2. Click Submit or "Cntrl + Enter" to get an AI-generated response

**Examples of questions you can ask:**
* General questions
    * Based on the information provided, what is president Bidens stance on immigration?
* Specific Executive Orders 
    * (Summarize executive order 14257, and provide a summary and sentiment analysis)
* Policy implications
    * What are the potential policy implications of Executive Order 13988 regarding nondiscrimination?
* Historical context
    * What were the significant historical developments or prior policies concerning Reciprocal Tariffs that preceded the Executive Order 14257?
* Legal interpretations
    * What are the constitutional implications of Executive Order 14160?
"""

# Developer Information
DEV_INFO = f"""
**Document Helper Bot**  
Version: {UI_CONFIG['APP_VERSION']}

**Developer Contact**  
Name: [{UI_CONFIG['DEVELOPER_NAME']}]  
GitHub: [{UI_CONFIG['DEVELOPER_GITHUB']}]

Built with Streamlit, LangChain, Pinecone and OpenAI API.
"""

def get_config() -> Dict[str, Any]:
    """Returns the complete configuration dictionary."""
    return {
        "ui": UI_CONFIG,
        "api": API_CONFIG,
        "chat": CHAT_CONFIG,
        "instructions": INSTRUCTIONS_TEXT,
        "dev_info": DEV_INFO
    } 