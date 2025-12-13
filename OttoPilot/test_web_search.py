
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Load env vars
load_dotenv()

from src.nodes import web_search_node, ChatbotState, generate_web_answer_node

def test_web_search():
    print("Testing Web Search...")
    
    state = ChatbotState(
        messages=[],
        query="What is the current stock price of Apple?",
        query_type="web",
        intent="info",
        retrieved_docs=[],
        web_results=[],
        answer="",
        sources=[],
        language="en",
        confidence=0.0
    )
    
    # Run web search node
    state = web_search_node(state)
    
    if state["web_results"]:
        print(f"✅ Found {len(state['web_results'])} results")
        for i, res in enumerate(state["web_results"][:2]):
            print(f"Result {i+1}: {res.get('title')} - {res.get('url')}")
            
        # Run generation node
        state = generate_web_answer_node(state)
        print(f"✅ Answer: {state['answer'][:100]}...")
    else:
        print("❌ No results found")

if __name__ == "__main__":
    test_web_search()
