# Data Inspector - Review scraped content before processing

from pathlib import Path
import json
from typing import Dict, List
from collections import Counter
import os


class DataInspector:
    """
    Inspect and analyze scraped data before processing
    """

    def __init__(self, data_dir: str = "/Users/deepaktalwar/Desktop/OttoPilot/data/raw"):
        self.data_dir = Path(data_dir)

    def get_file_stats(self) -> Dict:
        """Get statistics about scraped files"""
        if not self.data_dir.exists():
            return {"error": "Data directory not found"}

        files = list(self.data_dir.glob("*"))

        stats = {
            "total_files": len(files),
            "file_types": Counter(),
            "total_size_mb": 0,
            "files_by_type": {}
        }

        for file in files:
            if file.is_file():
                ext = file.suffix.lower()
                stats["file_types"][ext] += 1
                stats["total_size_mb"] += file.stat().st_size / (1024 * 1024)

                if ext not in stats["files_by_type"]:
                    stats["files_by_type"][ext] = []
                stats["files_by_type"][ext].append(file.name)

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)

        return stats

    def preview_files(self, n: int = 3) -> None:
        """Preview first n files of each type"""
        stats = self.get_file_stats()

        if "error" in stats:
            print(f"❌ {stats['error']}")
            return

        print("\n" + "=" * 80)
        print("📄 FILE PREVIEWS")
        print("=" * 80)

        for ext, files in stats["files_by_type"].items():
            print(f"\n{ext.upper()} Files (showing {min(n, len(files))} of {len(files)}):")
            print("-" * 80)

            for i, filename in enumerate(files[:n], 1):
                filepath = self.data_dir / filename
                print(f"\n{i}. {filename}")
                print(f"   Size: {filepath.stat().st_size / 1024:.1f} KB")

                # Preview content for text files
                if ext in ['.txt', '.md']:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read(500)  # First 500 chars
                            print(f"   Preview: {content[:200]}...")
                    except Exception as e:
                        print(f"   Could not preview: {e}")

    def check_content_quality(self) -> None:
        """Check for potential issues in scraped content"""
        print("\n" + "=" * 80)
        print("🔍 CONTENT QUALITY CHECK")
        print("=" * 80)

        issues = []
        text_files = list(self.data_dir.glob("*.txt"))

        for file in text_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check file size
                if len(content) < 100:
                    issues.append(f"⚠️  {file.name}: Very short content ({len(content)} chars)")

                # Check for mostly non-text content
                non_text_ratio = sum(1 for c in content if not c.isprintable()) / len(content)
                if non_text_ratio > 0.3:
                    issues.append(f"⚠️  {file.name}: High non-printable character ratio")

                # Check for repeated content
                lines = content.split('\n')
                if len(lines) > 10:
                    unique_lines = len(set(lines))
                    if unique_lines / len(lines) < 0.5:
                        issues.append(f"⚠️  {file.name}: High content repetition")

            except Exception as e:
                issues.append(f"❌ {file.name}: Could not read file - {e}")

        if issues:
            print("\n⚠️  Issues found:\n")
            for issue in issues[:10]:  # Show first 10
                print(f"  {issue}")

            if len(issues) > 10:
                print(f"\n  ... and {len(issues) - 10} more issues")
        else:
            print("\n✅ No major issues detected!")

    def show_metadata(self) -> None:
        """Show scraping metadata if available"""
        metadata_file = self.data_dir / "scrape_metadata.json"

        if not metadata_file.exists():
            print("\n📋 No metadata file found")
            return

        print("\n" + "=" * 80)
        print("📋 SCRAPING METADATA")
        print("=" * 80)

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        print(f"\nTotal documents: {len(metadata)}")

        if metadata:
            print("\nSample entries:")
            for i, entry in enumerate(metadata[:3], 1):
                print(f"\n{i}. {entry.get('filename', 'Unknown')}")
                print(f"   URL: {entry.get('url', 'Unknown')}")
                print(f"   Title: {entry.get('title', 'Unknown')}")
                print(f"   Length: {entry.get('length', 0):,} chars")

    def generate_report(self) -> None:
        """Generate comprehensive inspection report"""
        print("\n" + "=" * 80)
        print("📊 DATA COLLECTION REPORT")
        print("=" * 80)

        stats = self.get_file_stats()

        if "error" in stats:
            print(f"\n❌ {stats['error']}")
            print("\nMake sure you have run the scraper first!")
            return

        # Overall statistics
        print(f"\n📁 Directory: {self.data_dir}")
        print(f"📦 Total Files: {stats['total_files']}")
        print(f"💾 Total Size: {stats['total_size_mb']} MB")

        # File type breakdown
        print("\n📄 File Types:")
        for ext, count in stats['file_types'].most_common():
            print(f"   {ext:10s}: {count:3d} files")

        # Show metadata
        self.show_metadata()

        # Preview files
        self.preview_files(n=2)

        # Quality check
        self.check_content_quality()

        # Recommendations
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)

        if stats['total_files'] == 0:
            print("\n⚠️  No files found!")
            print("   Run the scraper first: python src/collect_data.py")
        elif stats['total_files'] < 5:
            print("\n⚠️  Very few files collected")
            print("   Consider scraping more pages or sections")
        elif stats['total_files'] < 20:
            print("\n✓ Good starting collection")
            print("  Ready to proceed with document processing")
        else:
            print("\n✓ Comprehensive collection!")
            print("  Ready to build your vector store")

        # Check for PDFs
        pdf_count = stats['file_types'].get('.pdf', 0)
        if pdf_count == 0:
            print("\n💡 No PDFs found")
            print("   PDFs often contain valuable structured information")
            print("   Consider running the document downloader")
        else:
            print(f"\n✓ Found {pdf_count} PDF(s)")

        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("""
1. Review the files in data/raw/
2. Remove any unwanted or low-quality files
3. Run document processor to create chunks:
   python src/document_processor.py

4. Build vector store:
   python src/embeddings.py

5. Test retrieval:
   python src/retriever.py
""")
        print("=" * 80)


def clean_bad_files(data_dir: str = "/Users/deepaktalwar/Desktop/OttoPilot/data/raw", min_size: int = 100):
    """
    Remove files that are too small or likely low-quality

    Args:
        data_dir: Directory to clean
        min_size: Minimum file size in bytes
    """
    data_path = Path(data_dir)
    removed = []

    for file in data_path.glob("*.txt"):
        if file.stat().st_size < min_size:
            print(f"Removing: {file.name} (too small)")
            file.unlink()
            removed.append(file.name)

    if removed:
        print(f"\n✓ Removed {len(removed)} low-quality files")
    else:
        print("\n✓ No files removed")

    return removed


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("🔎 DATA INSPECTOR")
    print("=" * 80)

    inspector = DataInspector("data/raw")

    # Generate full report
    inspector.generate_report()

    # Optional: Clean bad files
    print("\n" + "=" * 80)
    print("🧹 CLEANUP (Optional)")
    print("=" * 80)

    response = input("\nDo you want to remove very small files (<100 bytes)? (y/n): ")

    if response.lower() == 'y':
        clean_bad_files("data/raw", min_size=100)

    print("\n Inspection complete!")