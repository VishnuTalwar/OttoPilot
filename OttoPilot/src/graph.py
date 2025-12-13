"""
LangGraph Workflow for OVGU Chatbot
"""

from langgraph.graph import StateGraph, END
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from nodes import (
        ChatbotState,
        classify_query_node,
        retrieve_documents_node,
        web_search_node,
        generate_rag_answer_node,
        generate_web_answer_node,
        generate_chitchat_node,
        format_response_node,
        route_after_classification,
        should_generate_answer,
        route_after_web_search
    )
except ImportError as e:
    print(f"Error importing nodes: {e}")
    print("Make sure nodes.py exists!")
    import sys
    sys.exit(1)


# ============================================================================
# Build the Graph -
# ============================================================================

def create_chatbot_graph():
    """
    Create the LangGraph workflow
    
    KEY FIX: When query_type="web", go DIRECTLY to web_search
             Don't retrieve documents first!
    """
    workflow = StateGraph(ChatbotState)
    
    # Add all nodes
    workflow.add_node("classify_query", classify_query_node)
    workflow.add_node("retrieve_documents", retrieve_documents_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate_rag_answer", generate_rag_answer_node)
    workflow.add_node("generate_web_answer", generate_web_answer_node)
    workflow.add_node("generate_chitchat", generate_chitchat_node)
    workflow.add_node("format_response", format_response_node)
    
    # Set entry point
    workflow.set_entry_point("classify_query")
    

    # If query_type="web" → go DIRECTLY to web_search
    # If query_type="rag" → retrieve_documents (then fallback to web if no docs)
    # If query_type="chitchat" → generate_chitchat
    workflow.add_conditional_edges(
        "classify_query",
        route_after_classification,
        {
            "retrieve_documents": "retrieve_documents",  # For "rag" queries
            "web_search": "web_search",                 # For "web" queries - DIRECT
            "generate_chitchat": "generate_chitchat"   # For chitchat
        }
    )
    
    # After retrieve_documents: if no docs, fallback to web_search
    workflow.add_conditional_edges(
        "retrieve_documents",
        should_generate_answer,
        {
            "generate_rag_answer": "generate_rag_answer",  # Has docs
            "web_search": "web_search"                     # No docs - FALLBACK
        }
    )
    
    # After web_search: generate answer or fallback to chitchat
    workflow.add_conditional_edges(
        "web_search",
        route_after_web_search,
        {
            "generate_web_answer": "generate_web_answer",  # Has web results
            "generate_chitchat": "generate_chitchat"      # No results
        }
    )
    
    # All generation nodes go to format_response
    workflow.add_edge("generate_rag_answer", "format_response")
    workflow.add_edge("generate_web_answer", "format_response")
    workflow.add_edge("generate_chitchat", "format_response")
    
    # Format response goes to END
    workflow.add_edge("format_response", END)
    
    return workflow.compile()


# Export for LangGraph Studio
graph = create_chatbot_graph()


# ============================================================================
# Chatbot Class
# ============================================================================

class OVGUChatbot:
    """
    Main chatbot class with web search fallback
    """
    
    def __init__(self):
        """Initialize the chatbot"""
        print("\n" + "="*60)
        print("OVGU CHATBOT - INITIALIZING")
        print("="*60)
        
        self.graph = create_chatbot_graph()
        self.conversation_history = []
        
        print("[INFO] Chatbot ready!")
        print("[INFO] Features:")
        print("       - RAG from internal documents")
        print("       - Web search fallback (Tavily)")
        print("       - Bilingual support (EN/DE)")

        print("       - query_type='web' -> direct to web_search")
        print("       - query_type='rag' -> retrieve_documents -> fallback to web if no docs")
        print("="*60 + "\n")
    
    def ask(self, query: str) -> str:
        """
        Ask the chatbot a question
        
        Args:
            query: User question
        
        Returns:
            Chatbot answer
        """
        print(f"\n{'='*60}")
        print(f"Question: {query}")
        print(f"{'='*60}")
        
        initial_state = ChatbotState(
            messages=self.conversation_history.copy(),
            query=query,
            query_type="",
            intent="",
            retrieved_docs=[],
            web_results=[],
            answer="",
            sources=[],
            language="de",
            confidence=0.0
        )
        
        try:
            result = self.graph.invoke(initial_state)
            
            answer = result.get("answer", "Sorry, I could not generate an answer.")
            
            self.conversation_history = result.get("messages", [])
            
            print(f"\n{'='*60}")
            print(f"[INFO] Answer generated!")
            print(f"{'='*60}\n")
            
            return answer
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return "Sorry, there was an error processing your question."
    
    def chat(self):
        """
        Start interactive chat session
        """
        print("\n" + "="*60)
        print("OVGU CHATBOT - INTERACTIVE MODE")
        print("="*60)
        print("\nAsk questions about OVGU!")
        print("Type 'quit' to exit.\n")
        print("Examples:")
        print("  - Was sind die Zulassungsvoraussetzungen? (RAG)")
        print("  - What are the admission requirements? (RAG)")
        print("  - What is the weather in Magdeburg? (WEB)")
        print("="*60 + "\n")
        
        while True:
            try:
                query = input("You: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q', 'tschuess', 'bye']:
                    print("\nGoodbye!")
                    break
                
                answer = self.ask(query)
                
                print(f"\nBot: {answer}\n")
                print("-"*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}\n")
                continue
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("[INFO] Conversation reset!")


# ============================================================================
# Visualization
# ============================================================================

def visualize_graph():
    """
    Print a visual representation of the graph
    """
    print("\n" + "="*60)
    print("LANGGRAPH WORKFLOW VISUALIZATION ")
    print("="*60)
    print("""
    
    START
      |
    [classify_query] --> Determine query type
      |
      |-> "rag" ---------> [retrieve_documents]
      |                        |
      |                   Check if docs found
      |                        |
      |                   |-> YES -> [generate_rag_answer]
      |                   |-> NO  -> [web_search] (FALLBACK)
      |                                   |
      |                              Check web results
      |                                   |
      |                              |-> YES -> [generate_web_answer]
      |                              |-> NO  -> [generate_chitchat]
      |
      |-> "web" ---------> [web_search] (DIRECT - NO DOCS CHECK)
      |                         |
      |                    [generate_web_answer]
      |
      |-> "chitchat" ----> [generate_chitchat]
      
      |
    [format_response] --> Add sources & format
      |
    END
    
    KEY FIX: query_type="web" goes DIRECTLY to web_search!
    
    """)
    print("="*60 + "\n")


# ============================================================================
# Main Function
# ============================================================================

def main():
    """
    Main function to run the chatbot
    """
    visualize_graph()
    
    chatbot = OVGUChatbot()
    
    print("\n" + "="*60)
    print("TESTING CHATBOT")
    print("="*60 + "\n")
    
    test_questions = [
        "Hallo!",  # Should be chitchat
        "Was sind die Zulassungsvoraussetzungen?",  # Should use RAG
        "What is the weather in Magdeburg today?",  # Should use WEB directly
    ]
    
    for question in test_questions:
        answer = chatbot.ask(question)
        print(f"\nAnswer:\n{answer}\n")
        print("-"*60)
        input("\nPress Enter to continue...")
    
    print("\n" + "="*60)
    print("Starting interactive mode...")
    print("="*60 + "\n")
    
    chatbot.chat()


if __name__ == "__main__":
    main()