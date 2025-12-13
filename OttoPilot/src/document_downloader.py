# PDF and Document Downloader for University Websites
# Downloads PDFs, DOCX, and other documents from university pages

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time
from typing import List, Set
import re


class DocumentDownloader:
    """
    Finds and downloads PDF, DOCX, and other documents from university websites
    """

    def __init__(self, base_url: str, output_dir: str = "data/raw"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.domain = urlparse(base_url).netloc
        self.downloaded: Set[str] = set()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Document extensions to download
        self.doc_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.xlsx']

    def is_document_url(self, url: str) -> bool:
        """Check if URL points to a document"""
        parsed = urlparse(url)
        return any(parsed.path.lower().endswith(ext) for ext in self.doc_extensions)

    def clean_filename(self, url: str) -> str:
        """Generate clean filename from URL"""
        parsed = urlparse(url)
        filename = Path(parsed.path).name

        # Clean the filename
        filename = re.sub(r'[^\w\-_.]', '_', filename)

        return filename

    def download_document(self, url: str) -> bool:
        """Download a single document"""
        if url in self.downloaded:
            return False

        try:
            print(f"  Downloading: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            # Generate filename
            filename = self.clean_filename(url)
            filepath = self.output_dir / filename

            # Handle duplicate filenames
            counter = 1
            while filepath.exists():
                stem = filepath.stem
                suffix = filepath.suffix
                filepath = self.output_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            # Save document
            with open(filepath, 'wb') as f:
                f.write(response.content)

            self.downloaded.add(url)
            print(f"  ✓ Saved: {filepath.name} ({len(response.content) / 1024:.1f} KB)")
            return True

        except Exception as e:
            print(f"  ✗ Error downloading {url}: {e}")
            return False

    def find_documents_on_page(self, page_url: str) -> List[str]:
        """Find all document links on a page"""
        try:
            response = requests.get(page_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            document_urls = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(page_url, link['href'])

                # Check if it's a document and from same domain
                if self.is_document_url(absolute_url):
                    parsed = urlparse(absolute_url)
                    if parsed.netloc == self.domain or not parsed.netloc:
                        document_urls.append(absolute_url)

            return document_urls

        except Exception as e:
            print(f"✗ Error accessing {page_url}: {e}")
            return []

    def download_from_page(self, page_url: str, delay: float = 1.0):
        """Find and download all documents from a specific page"""
        print(f"\n🔍 Searching for documents on: {page_url}")

        doc_urls = self.find_documents_on_page(page_url)

        if not doc_urls:
            print("  No documents found on this page")
            return

        print(f"  Found {len(doc_urls)} document(s)")

        for url in doc_urls:
            self.download_document(url)
            time.sleep(delay)

    def download_from_pages(self, page_urls: List[str], delay: float = 1.0):
        """Download documents from multiple pages"""
        print(f"🚀 Scanning {len(page_urls)} page(s) for documents\n")

        for page_url in page_urls:
            self.download_from_page(page_url, delay)

        print(f"\n✅ Download complete!")
        print(f"   Total documents downloaded: {len(self.downloaded)}")
        print(f"   Saved to: {self.output_dir}")

    def download_specific_docs(self, doc_urls: List[str], delay: float = 1.0):
        """Download specific document URLs directly"""
        print(f"🎯 Downloading {len(doc_urls)} specific document(s)\n")

        for url in doc_urls:
            self.download_document(url)
            time.sleep(delay)

        print(f"\n✅ Download complete!")
        print(f"   Documents downloaded: {len(self.downloaded)}")
        print(f"   Saved to: {self.output_dir}")


# ============================================================================
# Common University Document Patterns
# ============================================================================

def download_common_university_docs(base_url: str):
    """
    Download commonly available university documents
    """

    downloader = DocumentDownloader(base_url)

    # Common pages that usually have PDFs
    pages_to_check = [
        f"{base_url}/admissions",
        f"{base_url}/admissions/requirements",
        f"{base_url}/academics",
        f"{base_url}/academics/catalog",
        f"{base_url}/student-handbook",
        f"{base_url}/policies",
        f"{base_url}/downloads",
        f"{base_url}/resources"
    ]

    downloader.download_from_pages(pages_to_check, delay=2.0)


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # ========================================
    # OPTION 1: Scan specific pages for documents
    # ========================================
    """
    downloader = DocumentDownloader(
        base_url="https://www.youruniversity.edu",
        output_dir="data/raw"
    )

    pages_to_scan = [
        "https://www.youruniversity.edu/admissions",
        "https://www.youruniversity.edu/academics/catalog",
        "https://www.youruniversity.edu/student-life"
    ]

    downloader.download_from_pages(pages_to_scan, delay=2.0)
    """

    # ========================================
    # OPTION 2: Download specific document URLs
    # ========================================
    """
    downloader = DocumentDownloader(
        base_url="https://www.youruniversity.edu",
        output_dir="data/raw"
    )

    specific_docs = [
        "https://www.youruniversity.edu/docs/admission-requirements.pdf",
        "https://www.youruniversity.edu/docs/course-catalog.pdf",
        "https://www.youruniversity.edu/docs/student-handbook.pdf"
    ]

    downloader.download_specific_docs(specific_docs, delay=1.5)
    """

    # ========================================
    # OPTION 3: Download common university documents
    # ========================================
    """
    download_common_university_docs("https://www.youruniversity.edu")
    """

    print("=" * 80)
    print("UNIVERSITY DOCUMENT DOWNLOADER")
    print("=" * 80)
    print("\nReady to download! Uncomment one of the options above and run.")
    print("\nQuick start:")
    print("1. Replace 'youruniversity.edu' with your actual university domain")
    print("2. Choose a download strategy (Option 1, 2, or 3)")
    print("3. Uncomment the code for that option")
    print("4. Run: python src/document_downloader.py")
    print("\nDownloaded files will be saved to data/raw/\n")
    print("=" * 80)