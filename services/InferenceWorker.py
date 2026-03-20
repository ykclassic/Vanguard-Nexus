import os
import requests
import sys

# --- ROBUST PATH INJECTION ---
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from core.SentimentEngine import MarketSentimentEngine
from core.TechnicalAnalyst import TechnicalAnalyst
from services.ServiceRegistry import ServiceRegistry
from services.AlertService import VanguardDiscordDispatcher

class InferenceWorker:
    """
    The Zenith Engine: Optimized for Futures Triage.
    Automatically switches between Binance and Bybit to bypass regional 
    restrictions while providing real-time data source tracking.
    """
    
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.analyst = TechnicalAnalyst()
        self.dispatcher = VanguardDiscordDispatcher()
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    def _get_live_price(self, ticker):
        """
        Fetches live Futures price using a 3-tier exchange triage.
        Returns: (float price, str source_name)
        """
        symbol = f"{ticker}USDT"

        # 1. Primary: Binance USD-M Futures (Preferred for liquidity)
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                price = float(response.json().get("price", 0.0))
                if price > 0:
                    return price, "Binance Futures"
        except Exception:
            pass 
            
        # 2. Secondary: Bybit Linear Futures (Bypasses GitHub/US IP blocks)
        try:
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = float(data['result']['list'][0]['lastPrice'])
                if price > 0:
                    return price, "Bybit Futures"
        except Exception:
            pass 
            
        # 3. Tertiary: Alpha Vantage (Spot Fallback)
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": ticker,
                "to_currency": "USD",
                "apikey": self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            rate_data = data.get("Realtime Currency Exchange Rate", {})
            price = float(rate_data.get("5. Exchange Rate", 0.0))
            if price > 0:
                return price, "Alpha Vantage (Spot)"
        except Exception:
            return 0.0, "None (Connection Failed)"

    def _get_historical_series(self, ticker):
        """Fetches historical close prices for RSI calculation via triage."""
        symbol = f"{ticker}USDT"

        # Try Binance Futures
        try:
            url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1d&limit=20"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return [float(candle[4]) for candle in res.json()]
        except Exception: pass

        # Try Bybit Futures
        try:
            url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=D&limit=20"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                series = [float(candle[4]) for candle in data['result']['list']]
                return series[::-1] # Convert from Newest->Oldest to Oldest->Newest
        except Exception: pass

        return []

    def process_pending_data(self, raw_news, ticker="BTC"):
        """
        Executes a full Zenith Cycle.
        Ensures results are generated dynamically and not hardcoded.
        """
        # 1. Gather Price and identify Source
        current_price, source_name = self._get_live_price(ticker)
        
        # 2. Analyze Sentiment
        intel = self.engine.calculate_weighted_sentiment(raw_news)
        
        # 3. Analyze Technicals (RSI)
        history = self._get_historical_series(ticker)
        rsi_val = self.analyst.calculate_rsi(history) if len(history) >= 14 else 50.0
        
        # 4. Generate Confluence Signal
        signal = self.analyst.get_confluence(intel['aggregate_score'], rsi_val)
        
        # 5. Tactical Execution Logic (1:2 Risk-to-Reward)
        # We use a volatility-adjusted risk based on sentiment scores
        raw_vol = intel.get('volatility', 0.02)
        trade_risk_pct = min(max(raw_vol * 0.05, 0.01), 0.10) # Floor of 1%, Cap of 10%
        
        if current_price > 0:
            zones = {
                "entry": round(current_price, 2),
                "sl": round(current_price * (1 - trade_risk_pct), 2),
                "tp": round(current_price * (1 + (trade_risk_pct * 2.0)), 2)
            }
        else:
            zones = {"entry": 0.0, "sl": 0.0, "tp": 0.0}

        # 6. Final Intel Assembly
        intel.update({
            "current_price": current_price,
            "source": source_name,
            "rsi": round(rsi_val, 2),
            "confluence_signal": signal,
            "zones": zones
        })
        
        # Save state and dispatch alerts
        ServiceRegistry.save_state(f"zenith_{ticker}", intel)
        self.dispatcher.post_zenith_signal(ticker, intel)
        
        return intel
