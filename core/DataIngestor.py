import requests
from datetime import datetime

class FinancialDataIngestor:
    """Retrieves real-time news for Vanguard Nexus with security-hardened timeouts."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch_latest_news(self, ticker="BTC", limit=10):
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "apikey": self.api_key,
            "sort": "LATEST"
        }
        try:
            # Bandit B113 Fix: Added explicit 10-second timeout
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "Information" in data:
                return []
                
            return self._normalize_data(data.get("feed", [])[:limit])
        except requests.exceptions.Timeout:
            print(f"Ingestion Error: Connection to {self.base_url} timed out.")
            return []
        except Exception as e:
            print(f"Ingestion Error: {e}")
            return []

    def _normalize_data(self, raw_feed):
        return [{
            "text": f"{art.get('title', '')}. {art.get('summary', '')}",
            "source": "official_news",
            "timestamp": art.get("time_published", ""),
            "url": art.get("url", ""),
            "relevance_score": art.get("overall_sentiment_score", 0)
        } for art in raw_feed]
