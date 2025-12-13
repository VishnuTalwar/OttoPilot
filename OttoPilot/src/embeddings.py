"""
Embeddings & Vector Store Manager for OVGU Chatbot
ChromaDB Cloud version - Uses cloud-hosted vector store
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from typing import List
import chromadb
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.config import settings
    from document_processor import DocumentProcessor
except ImportError as e:
    print(f"Error importing: {e}")
    print("Make sure config.py and document_processor.py exist!")
    sys.exit(1)


class ChromaCloudVectorStoreManager:
    """
    Manages ChromaDB Cloud vector store
    """

    def __init__(
            self,
            api_key: str = None,
            tenant: str = None,
            database: str = None,
            collection_name: str = "ovgu_chatbot"
    ):
        """
        Initialize ChromaDB Cloud Vector Store Manager

        Args:
            api_key: ChromaDB Cloud API key
            tenant: Your ChromaDB Cloud tenant ID
            database: Your database name
            collection_name: Name for the vector collection
        """
        self.collection_name = collection_name
        self.vectorstore = None

        # ChromaDB Cloud credentials
        self.api_key = api_key or settings.chroma_api_key
        self.tenant = tenant or settings.chroma_tenant
        self.database = database or settings.chroma_database

        # Validate credentials
        if not all([self.api_key, self.tenant, self.database]):
            print(" ChromaDB Cloud credentials missing!")
            print("\nRequired in .env or config.py:")
            print("  CHROMA_API_KEY=your_api_key")
            print("  CHROMA_TENANT=your_tenant_id")
            print("  CHROMA_DATABASE=your_database_name")
            sys.exit(1)

        # Initialize ChromaDB Cloud client
        print("🔧 Connecting to ChromaDB Cloud...")
        try:
            self.client = chromadb.CloudClient(
                api_key=self.api_key,
                tenant=self.tenant,
                database=self.database
            )
            print(" Connected to ChromaDB Cloud successfully!")
            print(f"   Tenant: {self.tenant}")
            print(f"   Database: {self.database}")
        except Exception as e:
            print(f" Failed to connect to ChromaDB Cloud: {e}")
            print("\nCheck your credentials:")
            print("  - API key is correct")
            print("  - Tenant ID is correct")
            print("  - Database name is correct")
            sys.exit(1)

        # Initialize Gemini embeddings
        print("\n🔧 Initializing Gemini Embeddings...")
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model,
                google_api_key=settings.google_api_key
            )
            print(" Embeddings initialized successfully")
        except Exception as e:
            print(f" Error initializing embeddings: {e}")
            print("   Check your GOOGLE_API_KEY in .env file")
            sys.exit(1)

    def create_vectorstore(self, chunks: List) -> bool:
        """
        Create vector store from document chunks in ChromaDB Cloud

        Args:
            chunks: List of document chunks to embed

        Returns:
            True if successful, False otherwise
        """
        if not chunks:
            print(" No chunks provided!")
            return False

        print(f"\n{'=' * 60}")
        print(" CREATING CHROMADB CLOUD VECTOR STORE")
        print(f"{'=' * 60}")
        print(f" Processing {len(chunks)} chunks")
        print(f"  Storage: ChromaDB Cloud")
        print(f" Collection: {self.collection_name}")
        print(f" Tenant: {self.tenant}")
        print(f" Database: {self.database}")
        print(f"\n This may take 2-3 minutes...")
        print(f"{'=' * 60}\n")

        try:
            # Check if collection already exists
            try:
                existing_collection = self.client.get_collection(
                    name=self.collection_name
                )
                print(f"️  Collection '{self.collection_name}' already exists!")
                response = input("Delete and recreate? (y/n): ").strip().lower()

                if response == 'y':
                    self.client.delete_collection(name=self.collection_name)
                    print(f"  Deleted existing collection")
                else:
                    print(f" Using existing collection")
                    self.vectorstore = Chroma(
                        client=self.client,
                        collection_name=self.collection_name,
                        embedding_function=self.embeddings
                    )
                    return True
            except Exception:
                # Collection doesn't exist, that's fine
                pass

            # Create new vector store in ChromaDB Cloud
            print("📤 Uploading documents to ChromaDB Cloud...")

            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                client=self.client,
                collection_name=self.collection_name
            )

            print(f" ChromaDB Cloud vector store created!")
            print(f"️  Collection: {self.collection_name}")
            print(f" Total documents: {len(chunks)}")

            # Test search
            print(f"\n Testing vector store...")
            test_results = self.vectorstore.similarity_search("OVGU", k=1)
            if test_results:
                print(f" Vector store is working!")
                print(f"   Test query returned {len(test_results)} result(s)")

            return True

        except Exception as e:
            print(f" Error creating vector store: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_vectorstore(self) -> bool:
        """
        Load existing vector store from ChromaDB Cloud

        Returns:
            True if successful, False otherwise
        """
        print(f"  Loading collection from ChromaDB Cloud...")
        print(f"   Collection: {self.collection_name}")
        print(f"   Tenant: {self.tenant}")
        print(f"   Database: {self.database}")

        try:
            # Check if collection exists
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                print(f" Collection '{self.collection_name}' not found!")
                print(f"\nAvailable collections: {collection_names}")
                print(f"\nCreate it first by running this script!")
                return False

            # Load the collection
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )

            print(" Vector store loaded successfully!")

            # Show collection stats
            collection = self.client.get_collection(name=self.collection_name)
            count = collection.count()
            print(f" Collection stats:")
            print(f"   Documents: {count}")

            return True

        except Exception as e:
            print(f" Error loading vector store: {e}")
            import traceback
            traceback.print_exc()
            return False

    def search(self, query: str, k: int = 5):
        """
        Search for relevant documents

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            print(" Vector store not initialized!")
            return []

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f" Search error: {e}")
            return []

    def get_retriever(self, k: int = None):
        """
        Get a retriever object for use in chains

        Args:
            k: Number of documents to retrieve

        Returns:
            Retriever object
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized!")

        k = k or settings.top_k_docs

        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )

    def list_collections(self):
        """
        List all collections in the database
        """
        try:
            collections = self.client.list_collections()
            print(f"\n Collections in database '{self.database}':")
            for i, col in enumerate(collections, 1):
                print(f"   {i}. {col.name}")
            return collections
        except Exception as e:
            print(f" Error listing collections: {e}")
            return []

    def delete_collection(self, collection_name: str = None):
        """
        Delete a collection

        Args:
            collection_name: Name of collection to delete (default: current collection)
        """
        collection_name = collection_name or self.collection_name

        try:
            self.client.delete_collection(name=collection_name)
            print(f" Deleted collection: {collection_name}")
            return True
        except Exception as e:
            print(f" Error deleting collection: {e}")
            return False


def main():
    """
    Main function to create ChromaDB Cloud vector store
    """
    print("\n" + "=" * 60)
    print("OVGU CHATBOT - CHROMADB CLOUD VECTOR STORE CREATOR")
    print("=" * 60)

    # Get ChromaDB credentials
    print("\n ChromaDB Cloud Configuration:")
    print("-" * 60)

    # Check if credentials are in config
    use_config = False
    try:
        chroma_api_key = settings.chroma_api_key
        chroma_tenant = settings.chroma_tenant
        chroma_database = settings.chroma_database

        if all([chroma_api_key, chroma_tenant, chroma_database]):
            print(f" Found credentials in config:")
            print(f"   Tenant: {chroma_tenant}")
            print(f"   Database: {chroma_database}")
            use_config = True
        else:
            print("️  Some credentials missing in config")
    except AttributeError:
        print("  ChromaDB credentials not found in config")

    # Ask for credentials if not in config
    if not use_config:
        print("\nEnter your ChromaDB Cloud credentials:")
        print("(You can also add these to config.py)")

        chroma_api_key = input("\nChromaDB API Key: ").strip()
        chroma_tenant = input("Tenant ID (default: 3f4a6571-5eb8-4b93-bd74-de15b8b8b6c8): ").strip()
        if not chroma_tenant:
            chroma_tenant = "3f4a6571-5eb8-4b93-bd74-de15b8b8b6c8"

        chroma_database = input("Database name (default: OttoPilot): ").strip()
        if not chroma_database:
            chroma_database = "OttoPilot"

    collection_name = input("\nCollection name (default: ovgu_chatbot): ").strip()
    if not collection_name:
        collection_name = "ovgu_chatbot"

    print("-" * 60)

    # Step 1: Process documents
    print("\n[STEP 1/3] Processing documents...")
    processor = DocumentProcessor()
    chunks = processor.process()

    if not chunks:
        print("\n No documents to process!")
        print("Run the scraper first: python scrape_ovgu_optimized.py")
        return

    # Step 2: Create ChromaDB Cloud vector store
    print("\n[STEP 2/3] Creating ChromaDB Cloud vector store...")
    vs_manager = ChromaCloudVectorStoreManager(
        api_key=chroma_api_key,
        tenant=chroma_tenant,
        database=chroma_database,
        collection_name=collection_name
    )

    success = vs_manager.create_vectorstore(chunks)

    if not success:
        print("\n Failed to create vector store!")
        return

    # Step 3: Test search
    print("\n[STEP 3/3] Testing search functionality...")
    print("=" * 60)

    test_queries = [
        "Was sind die Zulassungsvoraussetzungen?",  # German
        "What are the admission requirements?",  # English
        "Welche Studiengänge gibt es?",  # German
    ]

    for query in test_queries:
        print(f"\n Query: {query}")
        results = vs_manager.search(query, k=2)

        if results:
            print(f"   Found {len(results)} results:")
            for i, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get('source_file', 'Unknown')
                preview = doc.page_content[:100].replace('\n', ' ')
                print(f"\n   [{i}] Score: {score:.3f}")
                print(f"       Source: {source}")
                print(f"       Preview: {preview}...")
        else:
            print("   No results found")

    print("\n" + "=" * 60)
    print(" CHROMADB CLOUD VECTOR STORE CREATION COMPLETE!")
    print("=" * 60)
    print(f"  Storage: ChromaDB Cloud")
    print(f" Tenant: {vs_manager.tenant}")
    print(f" Database: {vs_manager.database}")
    print(f" Collection: {vs_manager.collection_name}")
    print(f" Total chunks: {len(chunks)}")

    print("\n" + "=" * 60)
    print(" NEXT STEPS")
    print("=" * 60)
    print("1.  ChromaDB Cloud vector store created successfully")
    print("2.   Next: Test retrieval")
    print("   Run: python retriever.py")
    print("\n Your data is now stored in ChromaDB Cloud!")
    print("   You can access it from anywhere with your credentials.")
    print("=" * 60)


if __name__ == "__main__":
    main()