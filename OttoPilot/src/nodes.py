"""
LangGraph Nodes for OVGU Chatbot

"""

from typing import TypedDict, List, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from tavily import TavilyClient
import operator

try:
    from config import settings
    from retriever import UniversityRetriever
    from prompts import (
        CLASSIFICATION_PROMPT,
        RAG_ANSWER_PROMPT,
        WEB_ENHANCED_PROMPT,
        CHITCHAT_PROMPT,
        prepare_context,
        prepare_conversation_history,
        format_sources,
        parse_classification_response,
        detect_language,
        get_response_template
    )
except ImportError as e:
    print(f"Error importing: {e}")
    print("Make sure all required files exist!")
    import sys
    sys.exit(1)


# ============================================================================
# State Definition
# ============================================================================

class ChatbotState(TypedDict):
    """State that flows through the graph"""
    messages: Annotated[List, operator.add]
    query: str
    query_type: str
    intent: str
    retrieved_docs: List
    web_results: List
    answer: str
    sources: List[str]
    language: str
    confidence: float


# ============================================================================
# Initialize Components
# ============================================================================

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    temperature=settings.temperature,
    google_api_key=settings.google_api_key
)

try:
    retriever = UniversityRetriever()
    print("[INFO] Retriever initialized")
except Exception as e:
    print(f"[WARN] Could not initialize retriever: {e}")
    retriever = None

try:
    tavily_client = TavilyClient(api_key=settings.tavily_api_key)
    print("[INFO] Tavily client initialized")
except Exception as e:
    print(f"[WARN] Could not initialize Tavily: {e}")
    tavily_client = None


# ============================================================================
# Node 1: Classify Query
# ============================================================================

def classify_query_node(state: ChatbotState) -> ChatbotState:
    """Classify the user query and detect language"""
    print("\n[NODE] Classifying query...")

    # Handle input from LangGraph Studio
    if "query" not in state or not state["query"]:
        if state.get("messages"):
            last_message = state["messages"][-1]
            if hasattr(last_message, "content"):
                state["query"] = last_message.content
            elif isinstance(last_message, dict):
                state["query"] = last_message.get("content", "")
            else:
                state["query"] = str(last_message)
        else:
            state["query"] = ""

    query = state["query"]

    # Detect language
    language = detect_language(query)
    state["language"] = language
    lang_name = 'German' if language == 'de' else 'English'
    print(f"       Language detected: {lang_name}")
    print(f"       Query: {query}")

    try:
        response = llm.invoke(CLASSIFICATION_PROMPT.format_messages(query=query))
        classification = parse_classification_response(response.content)

        print(f"       Query Type: {classification['query_type']}")
        print(f"       Intent: {classification['intent']}")

        state["query_type"] = classification["query_type"]
        state["intent"] = classification["intent"]

    except Exception as e:
        print(f"       [WARN] Classification error: {e}")
        state["query_type"] = "rag"
        state["intent"] = "general_info"

    return state


# ============================================================================
# Node 2: Retrieve Documents with SIMILARITY SCORES
# ============================================================================

def retrieve_documents_node(state: ChatbotState) -> ChatbotState:
    """
    Retrieve relevant documents from vector store
    IMPROVED: Checks similarity scores to ensure relevance
    """
    print("\n[NODE] Retrieving documents...")

    if retriever is None:
        print("       [WARN] Retriever not available")
        state["retrieved_docs"] = []
        return state

    query = state["query"]

    try:
        # Try to get documents with scores
        try:
            results_with_scores = retriever.retrieve_with_scores(query, k=settings.top_k_docs)

            # CRITICAL: Filter by similarity threshold
            # Lower score in ChromaDB = more similar
            SIMILARITY_THRESHOLD = 0.3  # Adjust this (lower = stricter)

            filtered_docs = []
            for doc, score in results_with_scores:
                print(f"       Doc: {doc.metadata.get('source_file', 'Unknown')}, Score: {score:.3f}")

                if score <= SIMILARITY_THRESHOLD:
                    filtered_docs.append(doc)
                    print(f"         ACCEPTED (score {score:.3f} <= threshold {SIMILARITY_THRESHOLD})")
                else:
                    print(f"         REJECTED (score {score:.3f} > threshold {SIMILARITY_THRESHOLD})")

            docs = filtered_docs

        except AttributeError:
            # Fallback: retrieve_with_scores not available
            print("       [INFO] Using standard retrieval (no scores)")
            docs = retriever.retrieve(query, k=settings.top_k_docs)

        print(f"       Retrieved {len(docs)} relevant documents")

        if docs:
            first_doc = docs[0]
            source = first_doc.metadata.get('source_file', 'Unknown')
            preview = first_doc.page_content[:100].replace('\n', ' ')
            print(f"       Top result from: {source}")
            print(f"       Preview: {preview}...")
        else:
            print(f"         No relevant documents found (all below similarity threshold)")
            print(f"       Will fallback to web search")

        state["retrieved_docs"] = docs

    except Exception as e:
        print(f"       [WARN] Retrieval error: {e}")
        import traceback
        traceback.print_exc()
        state["retrieved_docs"] = []

    return state


# ============================================================================
# Node 3: Web Search - ALWAYS FOCUSED ON OVGU MAGDEBURG
# ============================================================================

def web_search_node(state: ChatbotState) -> ChatbotState:
    """
    Search the web using Tavily

    """
    print("\n[NODE] Searching web with Tavily (OVGU-focused)...")
    print("       Reason: No relevant documents found in RAG database")

    if tavily_client is None:
        print("       [ERROR] Tavily not initialized!")
        print("       Check TAVILY_API_KEY in .env")
        state["web_results"] = []
        return state

    original_query = state["query"]

    # CRITICAL: Always add OVGU context to web searches
    # This ensures results are always about OVGU Magdeburg
    ovgu_enhanced_query = f"{original_query} Otto-von-Guericke-Universität Magdeburg OVGU"

    # For German queries, use German university name
    language = state.get("language", "en")
    if language == "de":
        ovgu_enhanced_query = f"{original_query} Otto-von-Guericke-Universität Magdeburg"
    else:
        ovgu_enhanced_query = f"{original_query} Otto von Guericke University Magdeburg OVGU"

    try:
        print(f"       Original query: {original_query}")
        print(f"       Enhanced query: {ovgu_enhanced_query}")

        # Search with OVGU-specific query
        response = tavily_client.search(
            query=ovgu_enhanced_query,
            max_results=settings.tavily_max_results,
            search_depth=settings.tavily_search_depth,
            # Optional: Include domain filter for better results
            include_domains=["ovgu.de"]  # Prioritize official OVGU site
        )

        results = response.get('results', [])

        print(f"    Found {len(results)} web results (OVGU-focused)")

        if results:
            print(f"       Top 3 OVGU-related results:")
            for i, result in enumerate(results[:3], 1):
                print(f"         {i}. {result.get('title', 'No title')}")
                print(f"            URL: {result.get('url', 'No URL')}")
        else:
            print(f"      No OVGU-related web results found")

        state["web_results"] = results

    except Exception as e:
        print(f"       [ERROR] Web search failed: {e}")
        import traceback
        traceback.print_exc()
        state["web_results"] = []

    return state


# ============================================================================
# Node 4: Generate Answer (RAG) with MEMORY
# ============================================================================

def generate_rag_answer_node(state: ChatbotState) -> ChatbotState:
    """Generate answer using retrieved documents"""
    language = state.get("language", "en")
    lang_name = 'DE' if language == 'de' else 'EN'
    print(f"\n[NODE] Generating RAG answer ({lang_name})...")

    query = state["query"]
    docs = state.get("retrieved_docs", [])

    if not docs:
        print("       [WARN] No documents found")
        state["answer"] = ""
        state["sources"] = []
        return state

    try:
        # Prepare document context
        context = prepare_context(docs, max_length=3000, language=language)

        # Prepare conversation history
        conversation_history = prepare_conversation_history(
            state.get("messages", []),
            max_messages=3
        )

        # Generate answer with context and history
        response = llm.invoke(
            RAG_ANSWER_PROMPT.format_messages(
                conversation_history=conversation_history,
                context=context,
                question=query
            )
        )

        answer = response.content

        sources = [doc.metadata.get('source_file', 'Unknown') for doc in docs]
        unique_sources = list(set(sources))

        print(f"       Answer generated ({len(answer)} chars)")
        print(f"       Used conversation history: {len(conversation_history)} chars")
        print(f"       Sources: {', '.join(unique_sources[:3])}")

        state["answer"] = answer
        state["sources"] = unique_sources

    except Exception as e:
        print(f"       [ERROR] Generation error: {e}")
        import traceback
        traceback.print_exc()
        state["answer"] = ""
        state["sources"] = []

    return state


# ============================================================================
# Node 5: Generate Web Answer  - OVGU CONTEXT ENFORCED
# ============================================================================

def generate_web_answer_node(state: ChatbotState) -> ChatbotState:
    """
    Generate answer using web search results
    UPDATED: Reminds LLM to focus on OVGU even with web results
    """
    language = state.get("language", "en")
    lang_name = 'DE' if language == 'de' else 'EN'
    print(f"\n[NODE] Generating web answer ({lang_name}) - OVGU context")

    query = state["query"]
    web_results = state.get("web_results", [])

    if not web_results:
        print("       [WARN] No web results found")
        state["answer"] = get_response_template('no_information', language)
        state["sources"] = []
        return state

    try:
        # Prepare web context with OVGU emphasis
        web_context = ""
        sources = []

        print(f"       Processing {len(web_results)} OVGU-related web results...")

        for i, result in enumerate(web_results[:3], 1):
            title = result.get('title', 'No title')
            content = result.get('content', '')
            url = result.get('url', '')

            web_context += f"[OVGU Source {i}: {title}]\n{content}\n\n"
            sources.append(f"{title} ({url})")
            print(f"         {i}. {title}")

        # Prepare conversation history
        conversation_history = prepare_conversation_history(
            state.get("messages", []),
            max_messages=3
        )

        # Enhanced prompt to emphasize OVGU context
        ovgu_reminder = (
            "IMPORTANT: These web results are specifically about Otto-von-Guericke-Universität Magdeburg (OVGU). "
            "Focus your answer on OVGU-specific information.\n\n"
            if language == 'en' else
            "WICHTIG: Diese Web-Ergebnisse beziehen sich speziell auf die Otto-von-Guericke-Universität Magdeburg (OVGU). "
            "Fokussiere deine Antwort auf OVGU-spezifische Informationen.\n\n"
        )

        enhanced_context = ovgu_reminder + web_context

        # Generate answer using web context and history
        response = llm.invoke(
            WEB_ENHANCED_PROMPT.format_messages(
                conversation_history=conversation_history,
                web_context=enhanced_context,
                question=query
            )
        )

        answer = response.content

        print(f"        Web answer generated ({len(answer)} chars)")
        print(f"       Used conversation history: {len(conversation_history)} chars")
        print(f"       OVGU-focused sources: {len(sources)} web pages")

        state["answer"] = answer
        state["sources"] = sources

    except Exception as e:
        print(f"       [ERROR] Generation error: {e}")
        import traceback
        traceback.print_exc()
        state["answer"] = get_response_template('error', language)
        state["sources"] = []

    return state


# ============================================================================
# Node 6: Generate Chitchat with MEMORY
# ============================================================================

def generate_chitchat_node(state: ChatbotState) -> ChatbotState:
    """Generate casual conversation response"""
    language = state.get("language", "en")
    lang_name = 'DE' if language == 'de' else 'EN'
    print(f"\n[NODE] Generating chitchat ({lang_name})...")

    query = state["query"]

    try:
        query_lower = query.lower()

        # Quick responses for common phrases
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'hallo', 'guten tag', 'moin']):
            state["answer"] = get_response_template('greeting', language)
            state["sources"] = []
            return state

        if any(word in query_lower for word in ['thank', 'thanks', 'danke', 'vielen dank']):
            state["answer"] = get_response_template('thanks', language)
            state["sources"] = []
            return state

        if any(word in query_lower for word in ['bye', 'goodbye', 'tschüss', 'auf wiedersehen', 'ciao']):
            state["answer"] = get_response_template('goodbye', language)
            state["sources"] = []
            return state

        # Generate response with conversation context
        conversation_history = prepare_conversation_history(
            state.get("messages", []),
            max_messages=5
        )

        response = llm.invoke(
            CHITCHAT_PROMPT.format_messages(
                conversation_history=conversation_history,
                query=query
            )
        )

        state["answer"] = response.content
        state["sources"] = []

        print(f"       Chitchat response generated")

    except Exception as e:
        print(f"       [WARN] Error: {e}")
        state["answer"] = get_response_template('greeting', language)
        state["sources"] = []

    return state


# ============================================================================
# Node 7: Format Final Response
# ============================================================================

def format_response_node(state: ChatbotState) -> ChatbotState:
    """Format the final response with sources"""
    language = state.get("language", "en")
    lang_name = 'DE' if language == 'de' else 'EN'
    print(f"\n[NODE] Formatting response ({lang_name})...")

    answer = state.get("answer", "")
    sources = state.get("sources", [])

    if sources and state.get("query_type") in ["rag", "web", "hybrid"]:
        if state.get("web_results"):
            # Web sources - already formatted with URLs
            header = "\n\nSources:" if language == 'en' else "\n\nQuellen:"
            source_text = header + "\n" + "\n".join([f"- {s}" for s in sources])
        else:
            # Document sources
            source_text = format_sources(
                [type('obj', (object,), {'metadata': {'source_file': s}})() for s in sources],
                language=language
            )
        answer = answer + source_text

    state["answer"] = answer

    if "messages" not in state:
        state["messages"] = []

    state["messages"].append(HumanMessage(content=state["query"]))
    state["messages"].append(AIMessage(content=answer))

    print("        Response formatted and ready!")
    print(f"       Conversation length: {len(state['messages'])} messages")

    return state


# ============================================================================
# CRITICAL: Routing Functions with AGGRESSIVE WEB FALLBACK
# ============================================================================

def route_after_classification(state: ChatbotState) -> str:
    """Determine next node after classification"""
    query_type = state.get("query_type", "rag")

    routing = {
        "rag": "retrieve_documents",
        "chitchat": "generate_chitchat",
        "web": "web_search",
        "hybrid": "retrieve_documents"
    }

    next_node = routing.get(query_type, "retrieve_documents")
    print(f"\n[ROUTE] Classification: {query_type} -> {next_node}")

    return next_node


def should_generate_answer(state: ChatbotState) -> str:
    """
    CRITICAL: Aggressive web fallback
    Route to web if NO documents or insufficient quality
    """
    docs = state.get("retrieved_docs", [])

    if not docs or len(docs) == 0:
        # NO documents at all - MUST use web
        print(f"\n[ROUTE]  NO documents found -> web_search (FALLBACK)")
        print(f"        Reason: Query not in RAG database")
        print(f"        Will search for OVGU-specific information online")
        return "web_search"
    elif len(docs) == 1:
        # Only 1 document - could be marginal relevance
        # Still try RAG but log it
        print(f"\n[ROUTE]   Only 1 document found -> generate_rag_answer (marginal)")
        print(f"        Warning: Limited information available")
        return "generate_rag_answer"
    else:
        # 2+ documents - good confidence
        print(f"\n[ROUTE]  Found {len(docs)} documents -> generate_rag_answer")
        return "generate_rag_answer"


def route_after_web_search(state: ChatbotState) -> str:
    """Route after web search based on results"""
    web_results = state.get("web_results", [])

    if web_results and len(web_results) > 0:
        print(f"\n[ROUTE]  Found {len(web_results)} OVGU web results -> generate_web_answer")
        return "generate_web_answer"
    else:
        print(f"\n[ROUTE]  No OVGU web results found -> generate_chitchat (final fallback)")
        print(f"        Will inform user that information is not available")
        return "generate_chitchat"


# ============================================================================
# Export all nodes
# ============================================================================

__all__ = [
    'ChatbotState',
    'classify_query_node',
    'retrieve_documents_node',
    'web_search_node',
    'generate_rag_answer_node',
    'generate_web_answer_node',
    'generate_chitchat_node',
    'format_response_node',
    'route_after_classification',
    'should_generate_answer',
    'route_after_web_search'
]