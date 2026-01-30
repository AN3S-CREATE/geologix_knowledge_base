"""
GeoLogix AI - Web Search Module
Provides web search capabilities using DuckDuckGo (no API key required).
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import re

class WebSearch:
    """Web search using DuckDuckGo Instant Answer API."""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.headers = {
            "User-Agent": "GeoLogix AI/1.0 (Enterprise Knowledge System)"
        }
    
    def search(self, query: str, max_results: int = 5) -> Dict:
        """
        Perform a web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # DuckDuckGo Instant Answer API
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Search failed with status {response.status_code}",
                    "results": []
                }
            
            data = response.json()
            results = []
            
            # Abstract (main result)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "Summary"),
                    "snippet": data.get("Abstract"),
                    "source": data.get("AbstractSource", ""),
                    "url": data.get("AbstractURL", ""),
                    "type": "abstract"
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "type": "related"
                    })
            
            # Infobox facts
            if data.get("Infobox"):
                facts = []
                for item in data["Infobox"].get("content", [])[:5]:
                    if item.get("label") and item.get("value"):
                        facts.append(f"{item['label']}: {item['value']}")
                if facts:
                    results.append({
                        "title": "Quick Facts",
                        "snippet": "\n".join(facts),
                        "type": "facts"
                    })
            
            return {
                "success": True,
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "results": results[:max_results],
                "source": "DuckDuckGo"
            }
            
        except requests.Timeout:
            return {
                "success": False,
                "error": "Search timed out",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def search_news(self, query: str, max_results: int = 5) -> Dict:
        """Search for news-related content."""
        return self.search(f"{query} news latest", max_results)
    
    def search_industry(self, query: str) -> Dict:
        """Search for mining/earthworks industry information."""
        industry_terms = "mining earthworks construction south africa"
        return self.search(f"{query} {industry_terms}", max_results=5)
    
    def format_for_context(self, search_results: Dict) -> str:
        """Format search results for AI context."""
        if not search_results.get("success") or not search_results.get("results"):
            return ""
        
        context = f"\n═══ WEB SEARCH RESULTS for '{search_results['query']}' ═══\n"
        
        for i, result in enumerate(search_results["results"], 1):
            context += f"\n[{i}] {result.get('title', 'Result')}\n"
            context += f"    {result.get('snippet', '')[:300]}\n"
            if result.get("url"):
                context += f"    Source: {result['url']}\n"
        
        context += f"\n(Search performed: {search_results['timestamp']})\n"
        return context
