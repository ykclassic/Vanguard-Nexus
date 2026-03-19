import os
import requests
from core.SentimentEngine import MarketSentimentEngine
from core.TechnicalAnalyst import TechnicalAnalyst
from services.ServiceRegistry import ServiceRegistry
from services.AlertService import VanguardDiscordDispatcher

class InferenceWorker:
    """The Zenith Engine: Synchronizes Sentiment, Technicals, and Signals."""
    
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.analyst = TechnicalAnalyst()
        self.dispatcher = VanguardDiscordDispatcher()
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    def _get_realtime_price_data(self, ticker):
        """Fetches latest price and 14-period history for RSI calculation."""
        url = "https://www.alphavantage.co/query"
        # For Crypto, we use the Exchange Rate endpoint for spot price
        params = {
            "function": "CRYPTO_INTRADAY",
            "symbol": ticker,
            "market": "USD",
            "interval": "5min",
            "apikey": self.api_key
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            time_series = data.get("Time Series Crypto (5min)", {})
            prices = [float(v["4. close"]) for v in list(time_series.values())[:20]]
            return prices[::-1] # Return in chronological order
        except Exception as e:
            print(f"Price Fetch Error: {e}")
            return []

    def process_pending_data(self, raw_news, ticker="BTC"):
        """Executes the full Zenith Confluence Cycle."""
        if not raw_news: return None
        
        # 1. Calculate Sentiment
        intel = self.engine.calculate_weighted_sentiment(raw_news)
        
        # 2. Fetch Technicals
        price_history = self._get_realtime_price_data(ticker)
        rsi_val = self.analyst.calculate_rsi(price_history) if price_history else 50
        current_price = price_history[-1] if price_history else 0
        
        # 3. Generate Confluence Signal
        confluence = self.analyst.get_confluence(intel['aggregate_score'], rsi_val)
        
        # 4. Generate Trade Zones (SL/TP)
        volatility = intel.get('volatility', 0.02)
        zones = {
            "entry": round(current_price, 2),
            "sl": round(current_price * (1 - (volatility * 1.5)), 2),
            "tp": round(current_price * (1 + (volatility * 3.0)), 2)
        }

        # Update Intelligence Object
        intel.update({
            "rsi": round(rsi_val, 2),
            "confluence_signal": confluence,
            "zones": zones,
            "current_price": current_price
        })
        
        # 5. Save and Dispatch
        ServiceRegistry.save_state(f"zenith_{ticker}", intel)
        self.dispatcher.post_zenith_signal(ticker, intel)
        
        return intel
