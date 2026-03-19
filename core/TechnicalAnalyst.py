import pandas as pd

class TechnicalAnalyst:
    """Mathematical engine for Technical Indicator Confluence."""
    
    def calculate_rsi(self, prices, period=14):
        """Calculates the Relative Strength Index (RSI)."""
        if len(prices) < period: return 50
        
        series = pd.Series(prices)
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def get_confluence(self, sentiment, rsi):
        """Logic-gate for high-probability signals."""
        if sentiment > 0.15 and rsi < 40:
            return "🔥 STRONG BUY (Bullish Sentiment + Low RSI)"
        elif sentiment < -0.15 and rsi > 60:
            return "❄️ STRONG SELL (Bearish Sentiment + High RSI)"
        elif sentiment > 0.1:
            return "📈 LEAN BULLISH"
        elif sentiment < -0.1:
            return "📉 LEAN BEARISH"
        return "⚖️ NEUTRAL"
