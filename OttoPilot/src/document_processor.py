"""
Document Processor for OVGU Chatbot
Loads documents from data/raw and chunks them for embedding
"""

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


from typing import List
from pathlib import Path
import sys

# Import config
try:
    from config import settings
except ImportError:
    print("Error: config.py not found. Make sure you created it!")
    sys.exit(1)


class DocumentProcessor:
    """
    Process documents from raw format into chunks suitable for embedding
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        print(f"📋 DocumentProcessor initialized")
        print(f"   Chunk size: {self.chunk_size}")
        print(f"   Chunk overlap: {self.chunk_overlap}")

    def load_documents(self, data_dir: str = None) -> List:
        """
        Load all documents from data directory

        Args:
            data_dir: Directory containing documents (default: from settings)

        Returns:
            List of loaded documents
        """
        if data_dir is None:
            data_dir = settings.data_dir

        data_path = Path(data_dir)

        if not data_path.exists():
            print(f" Error: Directory {data_dir} does not exist!")
            print(f"   Make sure you ran the scraper first.")
            return []

        documents = []
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md']

        print(f"\n🔍 Scanning directory: {data_dir}")
        print(f"   Looking for: {', '.join(supported_extensions)}")
        print("=" * 60)

        # Find all files
        all_files = list(data_path.rglob("*"))
        file_count = 0

        for file_path in all_files:
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in supported_extensions:
                continue

            try:
                # Choose appropriate loader based on file type
                if file_path.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                elif file_path.suffix.lower() in [".docx", ".doc"]:
                    loader = Docx2txtLoader(str(file_path))
                elif file_path.suffix.lower() in [".txt", ".md"]:
                    loader = TextLoader(str(file_path), encoding='utf-8')
                else:
                    continue

                # Load the document
                docs = loader.load()

                # Add metadata
                for doc in docs:
                    doc.metadata["source_file"] = file_path.name
                    doc.metadata["file_type"] = file_path.suffix
                    doc.metadata["file_path"] = str(file_path)

                documents.extend(docs)
                file_count += 1
                print(f"✓ Loaded: {file_path.name} ({len(docs)} pages)")

            except Exception as e:
                print(f"✗ Error loading {file_path.name}: {e}")

        print("=" * 60)
        print(f" Successfully loaded {len(documents)} document(s) from {file_count} file(s)")

        if len(documents) == 0:
            print("\n  Warning: No documents loaded!")
            print("   Make sure you have files in data/raw/")
            print("   Run the scraper first: python scrape_ovgu_optimized.py")

        return documents

    def chunk_documents(self, documents: List) -> List:
        """
        Split documents into smaller chunks

        Args:
            documents: List of documents to chunk

        Returns:
            List of document chunks
        """
        if not documents:
            print(" No documents to chunk!")
            return []

        print(f"\n Chunking {len(documents)} document(s)...")

        # Split documents
        chunks = self.text_splitter.split_documents(documents)

        print(f" Created {len(chunks)} chunks")

        # Show statistics
        chunk_lengths = [len(chunk.page_content) for chunk in chunks]
        avg_length = sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0

        print(f"\n Chunk Statistics:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Average chunk size: {avg_length:.0f} characters")
        print(f"   Min chunk size: {min(chunk_lengths) if chunk_lengths else 0}")
        print(f"   Max chunk size: {max(chunk_lengths) if chunk_lengths else 0}")

        return chunks

    def process(self, data_dir: str = None) -> List:
        """
        Complete processing pipeline: load + chunk

        Args:
            data_dir: Directory containing documents

        Returns:
            List of document chunks ready for embedding
        """
        print("\n" + "=" * 60)
        print(" DOCUMENT PROCESSING PIPELINE")
        print("=" * 60)

        # Load documents
        documents = self.load_documents(data_dir)

        if not documents:
            return []

        # Chunk documents
        chunks = self.chunk_documents(documents)

        # Preview first chunk
        if chunks:
            print("\n" + "=" * 60)
            print(" Preview of First Chunk:")
            print("=" * 60)
            first_chunk = chunks[0]
            print(f"Source: {first_chunk.metadata.get('source_file', 'Unknown')}")
            print(f"Content: {first_chunk.page_content[:300]}...")
            print("=" * 60)

        print(f"\n Processing complete!")
        print(f"   Ready for embedding: {len(chunks)} chunks")

        return chunks


def main():
    """
    Main function to run document processing
    """
    print("\n" + "=" * 60)
    print("OVGU CHATBOT - DOCUMENT PROCESSOR")
    print("=" * 60)

    # Create processor
    processor = DocumentProcessor()

    # Process documents
    chunks = processor.process()

    if chunks:
        print("\n" + "=" * 60)
        print("🎯 NEXT STEPS")
        print("=" * 60)
        print("1.  Documents processed successfully")
        print("2.   Next: Create vector store")
        print("   Run: python embeddings.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  NO DOCUMENTS PROCESSED")
        print("=" * 60)
        print("Make sure you have files in data/raw/")
        print("Run the scraper first: python scrape_ovgu_optimized.py")
        print("=" * 60)

    return chunks


if __name__ == "__main__":
    main()