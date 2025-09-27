"""
News fetching tool for getting latest news headlines.
"""

import requests
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class NewsTool(BaseTool):
    """LangChain tool for news information."""
    
    name = "news_fetcher"
    description = "Get latest news. Input can be 'general', 'technology', 'business', 'sports', or 'health'."
    
    def __init__(self, news_api_key=None):
        super().__init__()
        self.news_api_key = news_api_key
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get news information."""
        try:
            category = query.lower().strip() if query else 'general'
            
            if self.news_api_key:
                return self._get_news_api(category)
            else:
                return self._get_free_news()
                
        except Exception as e:
            return f"News fetch failed: {str(e)}"
    
    def _get_news_api(self, category):
        """Get news from NewsAPI."""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.news_api_key,
                'country': 'us',
                'category': category,
                'pageSize': 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    news_items = []
                    for article in articles:
                        title = article.get('title', 'No title')
                        description = article.get('description', 'No description')[:100]
                        news_items.append(f"{title}\n{description}...")
                    
                    return "Latest headlines:\n" + "\n---\n".join(news_items)
            
            return self._get_free_news()
            
        except Exception:
            return self._get_free_news()
    
    def _get_free_news(self):
        """Get news from free sources."""
        try:
            url = "https://rss.cnn.com/rss/edition.rss"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)
                
                news_items = []
                for item in root.findall('.//item')[:3]:
                    title = item.find('title').text if item.find('title') is not None else 'No title'
                    news_items.append(title)
                
                return "Latest headlines:\n" + "\n".join(news_items)
            
            return "Unable to fetch news at the moment."
            
        except Exception as e:
            return f"News unavailable: {str(e)}"