"""
OttoPilot - OVGU Chatbot
"""

import streamlit as st
import sys
from pathlib import Path
import base64
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from graph import OVGUChatbot
except ImportError as e:
    st.error(f"Error importing chatbot: {e}")
    st.error("Make sure all required files are in the src/ directory")
    st.stop()


# ============================================================================
# Helper Functions
# ============================================================================

def get_portrait_base64():
    """Get portrait image as base64 string"""
    portrait_paths = [
        "./assets/otto_potrait.jpg",
        "assets/otto_portrait.jpg",
        "otto_portrait.jpg",
        Path(__file__).parent / "assets" / "otto_portrait.jpg",
        Path(__file__).parent / "otto_portrait.jpg"
    ]

    for path in portrait_paths:
        try:
            from PIL import Image
            img = Image.open(path)
            # Resize to ensure consistent size
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except:
            continue

    # Fallback: return None if no image found
    return None


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
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
    
    /* Apply font */
    html, body, * {
        font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
    }
    
    /* Hide Streamlit elements */
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
    
    /* Header - Updated for integrated portrait */
    .otto-header {
        background: #FFFFFF;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    
    .header-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .portrait-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid #7A003E;
        object-fit: cover;
        box-shadow: 0 4px 15px rgba(122, 0, 62, 0.3);
        flex-shrink: 0;
    }
    
    .portrait-placeholder {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: #7A003E;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 3px solid #7A003E;
        box-shadow: 0 4px 15px rgba(122, 0, 62, 0.3);
        font-size: 3rem;
        flex-shrink: 0;
    }
    
    .title-section {
        flex: 1;
    }
    
    .otto-title {
        font-size: 3rem;
        font-weight: 700;
        color: #7A003E;
        margin: 0;
        letter-spacing: -2px;
        line-height: 1.2;
    }
    
    .otto-subtitle {
        font-size: 0.9rem;
        color: #7A003E;
        opacity: 0.7;
        margin-top: 0.25rem;
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
    }
    
    .welcome-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: #FFFFFF;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: none !important;
        padding: 0.5rem 0 !important;
    }
    
    .stChatMessage[data-testid="user-message"] [data-testid="stMarkdownContainer"],
    div[class*="user"] [data-testid="stMarkdownContainer"] {
        background: #f8f9fa !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border-left: 4px solid #7A003E !important;
        color: #000000 !important;
        margin-bottom: 1rem !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] [data-testid="stMarkdownContainer"],
    div[class*="assistant"] [data-testid="stMarkdownContainer"] {
        background: #7A003E !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border-right: 4px solid #FFFFFF !important;
        color: #FFFFFF !important;
        margin-bottom: 1rem !important;
    }
    
    .stChatMessage p {
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Sources box */
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
    }
    
    .sources-list {
        color: #000000 !important;
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
        color: #FFFFFF !important;
        background: #7A003E !important;
    }
    
    input::placeholder, textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
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
# Header with Integrated Portrait
# ============================================================================

portrait_base64 = get_portrait_base64()

if portrait_base64:
    # Portrait found - show integrated header with image
    st.markdown(f"""
    <div class="otto-header">
        <div class="header-content">
            <img src="data:image/jpeg;base64,{portrait_base64}" class="portrait-circle" alt="Otto von Guericke">
            <div class="title-section">
                <div class="otto-title">OttoPilot</div>
                <div class="otto-subtitle">Powered by Gemini</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # No portrait - show header with placeholder
    st.markdown("""
    <div class="otto-header">
        <div class="header-content">
            <div class="portrait-placeholder">🎓</div>
            <div class="title-section">
                <div class="otto-title">OttoPilot</div>
                <div class="otto-subtitle">Powered by Gemini</div>
            </div>
        </div>
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
# Chat Interface
# ============================================================================

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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


if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = st.session_state.chatbot.ask(prompt)

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


# ============================================================================
# Footer - Compact Popover
# ============================================================================

st.markdown("---")

with st.popover("Contact Info"):
    st.markdown("**Contact:** vishnutalwar03@gmail.com")
    st.markdown("⚠️ *Independent project · Not affiliated with OVGU*")
    st.markdown("*Visit [ovgu.de](https://www.ovgu.de) for official information*")
    st.markdown("*Made by Vishnu Talwar*")
