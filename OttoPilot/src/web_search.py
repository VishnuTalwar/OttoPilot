# Web_search module
from typing import List, Dict, Optional
from tavily import TavilyClient
from config import settings


class WebSearcher:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.tavily_api_key
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
            self.enabled = True
        else:
            self.enabled = False
            print("⚠ Tavily API key not found. Web search disabled.")

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the web using Tavily"""
        if not self.enabled:
            return []

        try:
            # Add university name to search for better results
            enhanced_query = f"{query} site:https://www.ovgu.de/"

            response = self.client.search(
                query=enhanced_query,
                max_results=max_results,
                search_depth="basic"  # or "advanced" for more thorough
            )

            results = []
            for item in response.get('results', []):
                results.append({
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'content': item.get('content'),
                    'score': item.get('score', 0)
                })

            return results

        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def format_results(self, results: List[Dict]) -> str:
        """Format search results for LLM context"""
        if not results:
            return "No web results found."

        formatted = "Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   {result['content'][:300]}...\n\n"

        return formatted


# Test
if __name__ == "__main__":
    searcher = WebSearcher()

    if searcher.enabled:
        query = "upcoming university events this week"
        results = searcher.search(query, max_results=3)

        print(f"Query: {query}\n")
        print(searcher.format_results(results))
    else:
        print("Set TAVILY_API_KEY in .env to test web search")