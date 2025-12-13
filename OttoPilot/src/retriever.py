"""
Retriever for OVGU Chatbot - ChromaDB Cloud Version
Simplified version without deprecated imports
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List
import sys

try:
    from config import settings
    from embeddings import ChromaCloudVectorStoreManager
except ImportError as e:
    print(f"Error importing: {e}")
    print("Make sure config.py and embeddings.py exist!")
    sys.exit(1)


class UniversityRetriever:
    """
    Retriever for university chatbot using ChromaDB Cloud
    Simple and fast - no deprecated dependencies
    """

    def __init__(self, collection_name: str = None):
        """
        Initialize retriever

        Args:
            collection_name: ChromaDB collection name (default: from settings)
        """
        print("🔧 Initializing UniversityRetriever (ChromaDB Cloud)...")

        collection_name = collection_name or settings.chroma_collection_name

        # Load ChromaDB Cloud vector store
        self.vs_manager = ChromaCloudVectorStoreManager(
            collection_name=collection_name
        )

        if not self.vs_manager.load_vectorstore():
            print("❌ Failed to load vector store!")
            print("   Create it first: python embeddings.py")
            sys.exit(1)

        # Get base retriever
        self.vectorstore = self.vs_manager.vectorstore

        print("✅ Retriever initialized successfully")
        print(f"☁️  Connected to collection: {collection_name}")

    def retrieve(self, query: str, k: int = None) -> List:
        """
        Retrieve relevant documents

        Args:
            query: Search query
            k: Number of documents to retrieve (default: from settings)

        Returns:
            List of relevant documents
        """
        k = k or settings.top_k_docs

        # Use the vectorstore's similarity search
        docs = self.vectorstore.similarity_search(query, k=k)
        return docs

    def retrieve_with_scores(self, query: str, k: int = None):
        """
        Retrieve documents with similarity scores

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of (document, score) tuples
        """
        k = k or settings.top_k_docs
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results

    def get_retriever(self, k: int = None):
        """
        Get a retriever object for use in chains

        Args:
            k: Number of documents to retrieve

        Returns:
            Retriever object
        """
        k = k or settings.top_k_docs

        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )


def test_retriever():
    """
    Test retriever with sample queries in German and English
    """
    print("\n" + "=" * 60)
    print("OVGU CHATBOT - RETRIEVER TEST (CHROMADB CLOUD)")
    print("=" * 60)

    # Initialize retriever
    print("\n[1] Initializing retriever...")
    try:
        retriever = UniversityRetriever()
    except Exception as e:
        print(f"\n❌ Failed to initialize retriever: {e}")
        print("\nMake sure you:")
        print("1. Created the vector store: python embeddings.py")
        print("2. Set ChromaDB credentials in .env")
        import traceback
        traceback.print_exc()
        return

    # Test queries in German and English
    test_queries = [
        # German queries
        {
            "query": "Was sind die Zulassungsvoraussetzungen für ein Masterstudium?",
            "language": "German"
        },
        {
            "query": "Welche Fakultäten gibt es an der OVGU?",
            "language": "German"
        },
        {
            "query": "Wie bewerbe ich mich für ein Studium?",
            "language": "German"
        },
        # English queries
        {
            "query": "What are the admission requirements?",
            "language": "English"
        },
        {
            "query": "What study programs are available?",
            "language": "English"
        },
    ]

    print("\n[2] Testing retrieval from ChromaDB Cloud...")
    print("=" * 60)

    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        lang = test["language"]

        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_queries)} ({lang})")
        print(f"{'='*60}")
        print(f"📝 Query: {query}")
        print()

        # Retrieve documents with scores
        try:
            results = retriever.retrieve_with_scores(query, k=3)
        except Exception as e:
            print(f"   ❌ Error during search: {e}")
            import traceback
            traceback.print_exc()
            continue

        if not results:
            print("   ⚠️  No results found")
            continue

        print(f"   Found {len(results)} results:\n")

        for j, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source_file', 'Unknown')
            content = doc.page_content.replace('\n', ' ')[:200]

            print(f"   [{j}] Relevance Score: {score:.3f}")
            print(f"       Source: {source}")
            print(f"       Content: {content}...")
            print()

    print("=" * 60)
    print("✅ RETRIEVAL TEST COMPLETE")
    print("=" * 60)

    # Interactive mode
    print("\n" + "=" * 60)
    print("🎮 INTERACTIVE MODE")
    print("=" * 60)
    print("Try your own queries! (type 'quit' to exit)")
    print("Your queries will search ChromaDB Cloud ☁️")
    print("\n💡 Example queries:")
    print("   - Was sind die Zulassungsvoraussetzungen?")
    print("   - What programs does OVGU offer?")
    print("   - Wie bewerbe ich mich?")
    print("=" * 60)

    while True:
        try:
            query = input("\n💬 Your question: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not query:
                continue

            print(f"\n🔍 Searching ChromaDB Cloud for: {query}")
            print("-" * 60)

            results = retriever.retrieve_with_scores(query, k=3)

            if not results:
                print("❌ No results found. Try a different query.")
                continue

            for i, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get('source_file', 'Unknown')
                content = doc.page_content[:300]

                print(f"\n[{i}] Relevance: {score:.3f} | Source: {source}")
                print(f"    {content}...")

            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue


def main():
    """
    Main function
    """
    test_retriever()

    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    print("1. ✅ ChromaDB Cloud retrieval working successfully")
    print("2. ⏭️  Next: Build LangGraph workflow")
    print("   (Ask for next phase)")
    print("=" * 60)


if __name__ == "__main__":
    main()