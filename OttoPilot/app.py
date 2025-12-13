"""
OttoPilot - OVGU Chatbot
Version with DIRECT sources display (no expander)
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from graph import OVGUChatbot
except ImportError as e:
    st.error(f"Error importing chatbot: {e}")
    st.error("Make sure all required files are in the src/ directory")
    st.stop()


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="OttoPilot - OVGU Chatbot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================================
# Custom CSS
# ============================================================================

st.markdown("""
<style>
    /* Try multiple monospace fonts in order of preference */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    
    /* Apply font hierarchy */
    html, body {
        font-family: 'IBM Plex Mono', 'Roboto Mono', 'Space Mono', 'Courier New', 'Courier', monospace !important;
    }
    
    /* Force on all elements */
    * {
        font-family: 'IBM Plex Mono', 'Roboto Mono', 'Space Mono', 'Courier New', monospace !important;
    }
    
    .stApp {
        font-family: 'IBM Plex Mono', 'Roboto Mono', 'Space Mono', monospace !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #7A003E 0%, #4a0025 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Header */
    .otto-header {
        background: #FFFFFF;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .otto-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #7A003E;
        margin: 0;
        letter-spacing: -2px;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .otto-subtitle {
        font-size: 0.9rem;
        color: #7A003E;
        opacity: 0.7;
        margin-top: 0.5rem;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #7A003E 0%, #4a0025 100%);
        color: #FFFFFF;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .welcome-card h3 {
        margin: 0;
        font-size: 1.5rem;
        color: #FFFFFF;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .welcome-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: #FFFFFF;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    /* CHAT MESSAGES */
    .stChatMessage {
        background: none !important;
        padding: 0.5rem 0 !important;
    }
    
    .stChatMessage[data-testid="user-message"],
    div[class*="user"] {
        background: transparent !important;
    }
    
    .stChatMessage[data-testid="user-message"] [data-testid="stMarkdownContainer"],
    div[class*="user"] [data-testid="stMarkdownContainer"] {
        background: #f8f9fa !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border-left: 4px solid #7A003E !important;
        color: #000000 !important;
        margin-bottom: 1rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stChatMessage[data-testid="user-message"] p,
    .stChatMessage[data-testid="user-message"] *,
    div[class*="user"] p,
    div[class*="user"] * {
        color: #000000 !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stChatMessage[data-testid="assistant-message"],
    div[class*="assistant"] {
        background: transparent !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] [data-testid="stMarkdownContainer"],
    div[class*="assistant"] [data-testid="stMarkdownContainer"] {
        background: #7A003E !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border-right: 4px solid #FFFFFF !important;
        color: #FFFFFF !important;
        margin-bottom: 1rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] p,
    .stChatMessage[data-testid="assistant-message"] *,
    div[class*="assistant"] p,
    div[class*="assistant"] * {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stChatMessage p {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    /* Sources box - DIRECT DISPLAY (no expander) */
    .sources-box {
        background: #f8f9fa !important;
        border-left: 4px solid #7A003E !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin-top: 1rem !important;
    }
    
    .sources-title {
        font-weight: 700 !important;
        color: #7A003E !important;
        margin-bottom: 0.5rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .sources-list {
        color: #000000 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.9rem !important;
    }
    
    /* Input */
    .stChatInputContainer {
        background: #FFFFFF;
        border-radius: 15px;
        padding: 0.5rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stChatInput > div {
        border: 2px solid #7A003E !important;
        border-radius: 10px !important;
        background: #7A003E !important;
    }
    
    input, textarea {
        font-family: 'IBM Plex Mono', 'Roboto Mono', 'Space Mono', monospace !important;
        color: #FFFFFF !important;
        background: #7A003E !important;
    }
    
    input::placeholder, textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    input:focus, textarea:focus {
        color: #FFFFFF !important;
        background: #7A003E !important;
        border-color: #FFFFFF !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: #7A003E;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stButton > button:hover {
        background: #4a0025;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(122, 0, 62, 0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #7A003E;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4a0025;
    }
    
    .stSpinner > div {
        border-top-color: #7A003E !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Initialize Session State
# ============================================================================

if "chatbot" not in st.session_state:
    with st.spinner("Initializing OttoPilot..."):
        try:
            st.session_state.chatbot = OVGUChatbot()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources_history" not in st.session_state:
    st.session_state.sources_history = []


# ============================================================================
# Header
# ============================================================================

st.markdown("""
<div class="otto-header">
    <div class="otto-title">OttoPilot</div>
    <div class="otto-subtitle">Powered by Gemini</div>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# Welcome Message
# ============================================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3>Welcome to OttoPilot! 👋</h3>
        <p>Ask me anything about Otto-von-Guericke University Magdeburg</p>
        <p>English & Deutsch supported</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Chat Interface - WITH DIRECT SOURCES DISPLAY
# ============================================================================

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources DIRECTLY (no expander)
        if message["role"] == "assistant" and i < len(st.session_state.sources_history):
            sources = st.session_state.sources_history[i // 2]
            if sources:
                sources_html = f"""
                <div class="sources-box">
                    <div class="sources-title">📚 Sources:</div>
                    <div class="sources-list">
                        {''.join([f'• {source}<br>' for source in sources])}
                    </div>
                </div>
                """
                st.markdown(sources_html, unsafe_allow_html=True)


# Chat input
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = st.session_state.chatbot.ask(prompt)

                # Parse sources
                sources = []
                if "Sources:" in answer or "Quellen:" in answer:
                    parts = answer.split("\n\nSources:" if "Sources:" in answer else "\n\nQuellen:")
                    if len(parts) == 2:
                        main_answer = parts[0]
                        source_text = parts[1]
                        sources = [s.strip("- ").strip() for s in source_text.split("\n") if s.strip()]
                        answer = main_answer
                    else:
                        main_answer = answer
                else:
                    main_answer = answer

                st.markdown(main_answer)

                # Show sources directly
                if sources:
                    sources_html = f"""
                    <div class="sources-box">
                        <div class="sources-title">📚 Sources:</div>
                        <div class="sources-list">
                            {''.join([f'• {source}<br>' for source in sources])}
                        </div>
                    </div>
                    """
                    st.markdown(sources_html, unsafe_allow_html=True)

                st.session_state.messages.append({"role": "assistant", "content": main_answer})
                st.session_state.sources_history.append(sources)

            except Exception as e:
                error_message = f"Sorry, an error occurred: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                st.session_state.sources_history.append([])


# ============================================================================
# Clear Chat Button
# ============================================================================

if st.session_state.messages:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.sources_history = []
            st.session_state.chatbot.reset_conversation()
            st.rerun()