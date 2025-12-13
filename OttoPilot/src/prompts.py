"""
Bilingual Prompt Templates for OVGU Chatbot

"""

from langchain_core.prompts import ChatPromptTemplate
import re


# ============================================================================
# Language Detection
# ============================================================================

def detect_language(text: str) -> str:
    """
     language detection for German/English

    Uses multiple signals:
    1. German-specific characters (ä, ö, ü, ß)
    2. German-specific words
    3. English-specific words
    4. Word patterns
    5. Single-word dictionary lookup

    Args:
        text: Input text

    Returns:
        'de' for German, 'en' for English
    """
    if not text:
        return 'en'

    text_lower = text.lower().strip()

    # Signal 1: German umlauts and ß (very strong indicator)
    german_chars = ['ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü']
    has_german_chars = any(char in text for char in german_chars)

    if has_german_chars:
        return 'de'

    # Signal 2: Single word queries - direct dictionary lookup
    words = text_lower.split()
    if len(words) == 1:
        # Dictionary of common single words
        german_single_words = {
            'hallo', 'danke', 'bitte', 'ja', 'nein', 'guten', 'tag', 'morgen',
            'abend', 'tschüss', 'wie', 'was', 'wo', 'wann', 'warum', 'wer',
            'studium', 'universität', 'bewerbung', 'fakultät', 'semester',
            'wetter', 'heute', 'morgen', 'gestern', 'jetzt', 'hier', 'dort',
            'gut', 'schlecht', 'klein', 'groß', 'neu', 'alt', 'schnell', 'langsam'
        }

        english_single_words = {
            'hello', 'thanks', 'please', 'yes', 'no', 'good', 'morning',
            'evening', 'bye', 'goodbye', 'how', 'what', 'where', 'when', 'why', 'who',
            'study', 'university', 'application', 'faculty', 'semester',
            'weather', 'today', 'tomorrow', 'yesterday', 'now', 'here', 'there',
            'good', 'bad', 'small', 'big', 'new', 'old', 'fast', 'slow'
        }

        if text_lower in german_single_words:
            return 'de'
        if text_lower in english_single_words:
            return 'en'

    # Signal 3: Strong German indicators
    strong_german_words = [
        'die', 'der', 'das', 'und', 'ist', 'sind', 'ein', 'eine', 'ich',
        'wie', 'was', 'wo', 'wann', 'welche', 'welcher', 'welches',
        'studium', 'universität', 'bewerbung', 'fakultät', 'semester',
        'zulassungsvoraussetzungen', 'studiengang', 'voraussetzungen',
        'studiengänge', 'bewerbe', 'bewerben', 'gibt', 'kann', 'muss',
        'möchte', 'werden', 'haben', 'wird', 'auf', 'für', 'mit',
        'an', 'bei', 'zum', 'zur', 'vom', 'im', 'am', 'über', 'unter'
    ]

    # Signal 4: Strong English indicators
    strong_english_words = [
        'the', 'is', 'are', 'and', 'what', 'where', 'when', 'how', 'which',
        'study', 'university', 'application', 'faculty', 'semester',
        'admission', 'requirements', 'program', 'programs', 'apply',
        'can', 'must', 'should', 'would', 'will', 'have', 'has',
        'on', 'for', 'with', 'at', 'from', 'in', 'about', 'under'
    ]

    # Count matches (exact word matching)
    german_score = 0
    english_score = 0

    for word in words:
        if word in strong_german_words:
            german_score += 2
        if word in strong_english_words:
            english_score += 2

    # Signal 5: German word patterns (compound words, verb positions)
    # German tends to have longer words
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

    # German words tend to be longer
    if avg_word_length > 6:
        german_score += 1

    # Signal 6: Common German question starters
    german_question_starters = ['wie', 'was', 'wo', 'wann', 'warum', 'welche', 'welcher', 'welches']
    if any(text_lower.startswith(starter) for starter in german_question_starters):
        german_score += 3

    # Signal 7: Common English question starters
    english_question_starters = ['what', 'where', 'when', 'why', 'which', 'how', 'who']
    if any(text_lower.startswith(starter) for starter in english_question_starters):
        english_score += 3

    # Make decision
    if german_score > english_score:
        return 'de'
    elif english_score > german_score:
        return 'en'
    else:
        # Default to English if unclear (more international)
        return 'en'


# ============================================================================
# Query Classification
# ============================================================================

CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a query classifier for a university chatbot.

Classify queries into these categories:

**Query Types:**
- "rag": Questions about university info that should be in documents (programs, admission, policies, etc.)
- "web": Questions about current events, weather, news, real-time information
- "chitchat": Greetings, thanks, casual conversation

**CRITICAL RULES:**
1. If query is about OVGU/university information → "rag" (even if you're not sure it's in docs)
2. If query is about current/real-time info (weather, today, now, current) → "web"
3. If query is greeting/thanks/goodbye → "chitchat"
4. When in doubt about university topics → "rag" (let the system try docs first, then fallback to web)

**Intent Categories:**
admission, course, policy, event, housing, financial_aid, sports, general_info, chitchat, current_info

Respond ONLY in this format:
QUERY_TYPE: [rag|web|chitchat]
INTENT: [category]
REASONING: [brief explanation]"""),
    ("human", "{query}")
])


# ============================================================================
# System Prompts with Context
# ============================================================================

SYSTEM_PROMPT = """You are a helpful assistant for Otto-von-Guericke University Magdeburg (OVGU).
Du bist ein hilfreicher Assistent für die Otto-von-Guericke-Universität Magdeburg (OVGU).

Your tasks / Deine Aufgaben:
- Answer questions about OVGU clearly and precisely
- Beantworte Fragen über die OVGU klar und präzise
- Use the provided information / Nutze die bereitgestellten Informationen
- Be friendly and student-oriented / Sei freundlich und studentenorientiert
- Respond in the SAME LANGUAGE as the question (English or German)
- Antworte in der GLEICHEN SPRACHE wie die Frage (Englisch oder Deutsch)
- Remember context from previous messages in the conversation
- Erinnere dich an den Kontext aus vorherigen Nachrichten

Important / Wichtig:
- If you don't know the answer, say so honestly
- Wenn du die Antwort nicht weißt, sage es ehrlich
- Don't make up information / Erfinde keine Informationen
- Always cite your sources / Zitiere immer deine Quellen
- Use conversation history to provide better answers
- Nutze den Gesprächsverlauf für bessere Antworten"""


# ============================================================================
# RAG Answer Generation with Context
# ============================================================================

RAG_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an OVGU assistant. Answer based on provided documents AND conversation history.
Du bist ein OVGU-Assistent. Beantworte basierend auf Dokumenten UND Gesprächsverlauf.

Rules / Regeln:
1. Use information from context AND previous conversation / Nutze Infos aus Kontext UND vorherigem Gespräch
2. If context is insufficient, say: "I don't have this information." / 
   "Diese Information habe ich nicht."
3. Reference previous messages when relevant / Verweise auf frühere Nachrichten wenn relevant
4. Answer directly and clearly / Antworte direkt und klar
5. Cite sources: [Source: Document name] / [Quelle: Dokumentname]
6. Be friendly and helpful / Sei freundlich und hilfsbereit
7. **CRITICAL: Respond in the SAME LANGUAGE as the current question**
   **KRITISCH: Antworte in der GLEICHEN SPRACHE wie die aktuelle Frage**
   
Language Detection Rules:
- Look at the CURRENT question only for language
- "Was sind..." → Answer in German
- "What are..." → Answer in English
- "Wie..." → German
- "How..." → English"""),
    ("human", """Previous conversation (for context only):
{conversation_history}

Context from OVGU documents:
{context}

Current question: {question}

Answer in the SAME LANGUAGE as the current question:""")
])


# ============================================================================
# FIXED: Web-Enhanced Answer with STRICT Language Control
# ============================================================================

WEB_ENHANCED_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an OVGU assistant with access to web information and conversation history.
Du bist ein OVGU-Assistent mit Zugriff auf Web-Informationen und Gesprächsverlauf.

**CRITICAL LANGUAGE RULE:**
You MUST respond in the SAME LANGUAGE as the user's CURRENT question.
Du MUSST in der GLEICHEN SPRACHE wie die AKTUELLE Frage des Benutzers antworten.

**How to determine response language:**
1. Look at the CURRENT question ONLY (ignore web content language)
2. If question starts with English words (what, how, where, when, who) → Answer in ENGLISH
3. If question starts with German words (was, wie, wo, wann, wer, welche) → Answer in GERMAN
4. If question contains "the", "is", "are", "can" → Answer in ENGLISH
5. If question contains "die", "der", "das", "ist", "sind" → Answer in GERMAN

**Examples:**
- Question: "What is the weather in Berlin?" → Answer in ENGLISH (even if web results are in German)
- Question: "Wie ist das Wetter in Berlin?" → Answer in GERMAN (even if web results are in English)
- Question: "How do I apply?" → Answer in ENGLISH
- Question: "Wie bewerbe ich mich?" → Answer in GERMAN

Rules / Regeln:
1. Use web information to answer the question / Nutze Web-Informationen
2. Consider previous conversation for context / Berücksichtige vorheriges Gespräch
3. Cite sources correctly / Zitiere Quellen korrekt
4. **TRANSLATE web content if needed to match question language**
   **ÜBERSETZE Web-Inhalte wenn nötig, um zur Fragesprache zu passen**
5. **Response language = Question language (NOT web content language)**
   **Antwortsprache = Fragesprache (NICHT Web-Inhalts-Sprache)**"""),
    ("human", """Previous conversation:
{conversation_history}

Web information (may be in different language - translate if needed):
{web_context}

Current question (THIS determines your response language): {question}

**IMPORTANT: Answer in the SAME LANGUAGE as the question above, regardless of web content language.**""")
])


# ============================================================================
# Chitchat Response with Memory
# ============================================================================

CHITCHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly OVGU assistant.
Du bist ein freundlicher OVGU-Assistent.

Respond naturally to small talk.
Antworte natürlich auf Smalltalk.

Remember previous conversation.
Erinnere dich an vorheriges Gespräch.

**IMPORTANT: Respond in the SAME LANGUAGE as the user's current message.**
**WICHTIG: Antworte in der GLEICHEN SPRACHE wie die aktuelle Nachricht."""),
    ("human", """Previous conversation:
{conversation_history}

Current message: {query}

Respond naturally in the SAME LANGUAGE:""")
])


# ============================================================================
# Response Templates
# ============================================================================

RESPONSE_TEMPLATES = {
    'no_information': {
        'en': "I don't have specific information about that in my knowledge base. Let me search the web for you...",
        'de': "Ich habe keine spezifischen Informationen dazu in meiner Wissensdatenbank. Lass mich im Web für dich suchen..."
    },
    'error': {
        'en': "I'm sorry, there was an error processing your question. Please try again.",
        'de': "Entschuldigung, es gab einen Fehler bei der Verarbeitung deiner Frage. Bitte versuche es erneut."
    },
    'greeting': {
        'en': "Hello! I'm the OVGU chatbot. How can I help you today?",
        'de': "Hallo! Ich bin der OVGU Chatbot. Wie kann ich dir heute helfen?"
    },
    'thanks': {
        'en': "You're welcome! If you have any other questions about OVGU, feel free to ask!",
        'de': "Gern geschehen! Wenn du weitere Fragen zur OVGU hast, frag gerne!"
    },
    'goodbye': {
        'en': "Goodbye! Feel free to come back if you have more questions about OVGU!",
        'de': "Auf Wiedersehen! Komm gerne zurück, wenn du weitere Fragen zur OVGU hast!"
    }
}


def get_response_template(template_name: str, language: str = 'en') -> str:
    """Get a response template in the specified language"""
    return RESPONSE_TEMPLATES.get(template_name, {}).get(language,
                                                          RESPONSE_TEMPLATES[template_name]['en'])


# ============================================================================
# Source Citation Format
# ============================================================================

def format_sources(documents, language: str = 'en'):
    """Format document sources for citation"""
    if not documents:
        return ""

    sources = []
    seen_sources = set()

    for doc in documents:
        source = doc.metadata.get('source_file', 'Unknown' if language == 'en' else 'Unbekannt')
        if source not in seen_sources:
            sources.append(f"- {source}")
            seen_sources.add(source)

    header = "\n\nSources:" if language == 'en' else "\n\nQuellen:"
    return header + "\n" + "\n".join(sources)


# ============================================================================
# Context Preparation with Conversation History
# ============================================================================

def prepare_context(documents, max_length: int = 3000, language: str = 'en'):
    """Prepare context from retrieved documents"""
    if not documents:
        return ""

    context_parts = []
    current_length = 0

    doc_label = "Document" if language == 'en' else "Dokument"
    source_label = "Source" if language == 'en' else "Quelle"

    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get('source_file', 'Unknown' if language == 'en' else 'Unbekannt')
        content = doc.page_content.strip()

        doc_text = f"[{doc_label} {i} - {source_label}: {source}]\n{content}\n"

        if current_length + len(doc_text) > max_length:
            break

        context_parts.append(doc_text)
        current_length += len(doc_text)

    return "\n".join(context_parts)


def prepare_conversation_history(messages, max_messages: int = 5) -> str:
    """
    Prepare conversation history for context

    Args:
        messages: List of messages
        max_messages: Maximum number of recent messages to include

    Returns:
        Formatted conversation history string
    """
    if not messages:
        return "No previous conversation."

    # Take last N messages
    recent_messages = messages[-max_messages * 2:] if len(messages) > max_messages * 2 else messages

    history_parts = []
    for msg in recent_messages:
        if hasattr(msg, 'type'):
            role = "User" if msg.type == "human" else "Assistant"
            content = msg.content
        elif isinstance(msg, dict):
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
        else:
            continue

        history_parts.append(f"{role}: {content}")

    return "\n".join(history_parts) if history_parts else "No previous conversation."


# ============================================================================
# Helper Functions
# ============================================================================

def parse_classification_response(response: str) -> dict:
    """Parse the classification response from LLM"""
    lines = response.strip().split('\n')
    result = {
        'query_type': 'rag',
        'intent': 'general_info',
        'reasoning': ''
    }

    for line in lines:
        if line.startswith('QUERY_TYPE:'):
            result['query_type'] = line.split(':', 1)[1].strip().lower()
        elif line.startswith('INTENT:'):
            result['intent'] = line.split(':', 1)[1].strip().lower()
        elif line.startswith('REASONING:'):
            result['reasoning'] = line.split(':', 1)[1].strip()

    return result


# ============================================================================
# Export all
# ============================================================================

__all__ = [
    'SYSTEM_PROMPT',
    'CLASSIFICATION_PROMPT',
    'RAG_ANSWER_PROMPT',
    'WEB_ENHANCED_PROMPT',
    'CHITCHAT_PROMPT',
    'detect_language',
    'get_response_template',
    'format_sources',
    'prepare_context',
    'prepare_conversation_history',
    'parse_classification_response',
    'RESPONSE_TEMPLATES'
]