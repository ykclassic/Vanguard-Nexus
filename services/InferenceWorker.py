import os
import requests
from core.SentimentEngine import MarketSentimentEngine
from core.TechnicalAnalyst import TechnicalAnalyst
from services.ServiceRegistry import ServiceRegistry
from services.AlertService import VanguardDiscordDispatcher

class InferenceWorker:
    """The Zenith Engine: Re-engineered for bulletproof Crypto data parsing."""
    
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.analyst = TechnicalAnalyst()
        self.dispatcher = VanguardDiscordDispatcher()
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    def _get_live_spot_price(self, ticker):
        """Fetches the absolute latest exchange rate (Spot Price)."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": ticker,
            "to_currency": "USD",
            "apikey": self.api_key
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            # Key: "Realtime Currency Exchange Rate" -> "5. Exchange Rate"
            rate_data = data.get("Realtime Currency Exchange Rate", {})
            return float(rate_data.get("5. Exchange Rate", 0.0))
        except:
            return 0.0

    def _get_historical_series(self, ticker):
        """Fetches historical close prices for RSI calculation."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": ticker,
            "market": "USD",
            "apikey": self.api_key
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            series = data.get("Time Series (Digital Currency Daily)", {})
            # Extract the USD close price: "4b. close (USD)"
            return [float(v["4b. close (USD)"]) for v in list(series.values())[:20]][::-1]
        except:
            return []

    def process_pending_data(self, raw_news, ticker="BTC"):
        """Executes Zenith Cycle with explicit zero-prevention."""
        if not raw_news: return None
        
        # 1. Live Price & Sentiment
        current_price = self._get_live_spot_price(ticker)
        intel = self.engine.calculate_weighted_sentiment(raw_news)
        
        # 2. Historicals for RSI
        history = self._get_historical_series(ticker)
        rsi_val = self.analyst.calculate_rsi(history) if len(history) >= 14 else 50.0
        
        # 3. Zenith Signal Logic
        signal = self.analyst.get_confluence(intel['aggregate_score'], rsi_val)
        
        # 4. Tactical Zone Logic (Prevention of 0.0)
        vol = intel.get('volatility', 0.02)
        if current_price > 0:
            zones = {
                "entry": round(current_price, 2),
                "sl": round(current_price * (1 - (vol * 1.5)), 2),
                "tp": round(current_price * (1 + (vol * 3.0)), 2)
            }
        else:
            # Emergency Fallback for UI if API is throttled
            zones = {"entry": 0.0, "sl": 0.0, "tp": 0.0}

        intel.update({
            "current_price": current_price,
            "rsi": round(rsi_val, 2),
            "confluence_signal": signal,
            "zones": zones
        })
        
        ServiceRegistry.save_state(f"zenith_{ticker}", intel)
        self.dispatcher.post_zenith_signal(ticker, intel)
        
        return intel
