import requests
import time
from datetime import datetime

class FinancialDataIngestor:
    """Retrieves real-time news for Vanguard Nexus with built-in Rate Limiting."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.last_call_time = 0
        self.min_interval = 15  # 15s interval = 4 calls per minute (Safe for Free Tier)

    def fetch_latest_news(self, ticker="BTC", limit=10):
        # --- Rate Limiter Implementation ---
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"⏳ Rate limit protection active. Waiting {round(wait_time, 2)}s...")
            time.sleep(wait_time)

        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "apikey": self.api_key,
            "sort": "LATEST"
        }
        
        try:
            self.last_call_time = time.time()
            # Bandit B113 Fix: Added timeout
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "Note" in data:
                print("⚠️ Alpha Vantage: API Rate Limit Warning Detected.")
                return []

            return self._normalize_data(data.get("feed", [])[:limit])
        except Exception as e:
            print(f"Ingestion Error: {e}")
            return []

    def _normalize_data(self, raw_feed):
        # Maintains feature parity with previous updates
        return [{
            "text": f"{art.get('title', '')}. {art.get('summary', '')}",
            "source": "official_news",
            "timestamp": art.get("time_published", ""),
            "url": art.get("url", ""),
            "relevance_score": art.get("overall_sentiment_score", 0)
        } for art in raw_feed]
