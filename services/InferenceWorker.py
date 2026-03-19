import os
import requests
from core.SentimentEngine import MarketSentimentEngine
from core.TechnicalAnalyst import TechnicalAnalyst
from services.ServiceRegistry import ServiceRegistry
from services.AlertService import VanguardDiscordDispatcher

class InferenceWorker:
    """The Zenith Engine: Calibrated for Crypto Data Accuracy."""
    
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.analyst = TechnicalAnalyst()
        self.dispatcher = VanguardDiscordDispatcher()
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    def _get_realtime_price_data(self, ticker):
        """Robust price fetcher for Crypto and Equities."""
        url = "https://www.alphavantage.co/query"
        # Using DIGITAL_CURRENCY_DAILY for more reliable historical close data
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": ticker,
            "market": "USD",
            "apikey": self.api_key
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Navigate the complex Alpha Vantage Crypto JSON
            time_series_key = "Time Series (Digital Currency Daily)"
            if time_series_key not in data:
                print(f"⚠️ API Note: {data.get('Note', 'Check API Key limits')}")
                return []
            
            # Extract '4b. close (USD)' - specifically the USD value
            series = data[time_series_key]
            prices = [float(v["4b. close (USD)"]) for v in list(series.values())[:20]]
            return prices[::-1] # Past to Present
        except Exception as e:
            print(f"Price Calibration Error: {e}")
            return []

    def process_pending_data(self, raw_news, ticker="BTC"):
        """Executes Zenith Cycle with Zero-Value Protection."""
        if not raw_news: return None
        
        intel = self.engine.calculate_weighted_sentiment(raw_news)
        price_history = self._get_realtime_price_data(ticker)
        
        # Zero-Value Protection
        current_price = price_history[-1] if price_history else 0.0
        rsi_val = self.analyst.calculate_rsi(price_history) if len(price_history) >= 14 else 50.0
        
        # Calculate Signals
        signal = self.analyst.get_confluence(intel['aggregate_score'], rsi_val)
        
        # Calculate Zones (Only if price exists)
        vol = intel.get('volatility', 0.02)
        zones = {
            "entry": current_price,
            "sl": round(current_price * (1 - (vol * 1.2)), 2) if current_price > 0 else 0,
            "tp": round(current_price * (1 + (vol * 2.5)), 2) if current_price > 0 else 0
        }

        intel.update({
            "current_price": round(current_price, 2),
            "rsi": round(rsi_val, 2),
            "confluence_signal": signal,
            "zones": zones
        })
        
        ServiceRegistry.save_state(f"zenith_{ticker}", intel)
        self.dispatcher.post_zenith_signal(ticker, intel)
        
        return intel
