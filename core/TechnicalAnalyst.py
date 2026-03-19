import pandas as pd

class TechnicalAnalyst:
    """Calculates mathematical indicators for market confluence."""
    
    def calculate_rsi(self, prices, period=14):
        """Relative Strength Index to identify Overbought/Oversold."""
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def get_confluence(self, sentiment_score, rsi):
        """Checks if Sentiment and Technicals align."""
        if sentiment_score > 0.2 and rsi < 30:
            return "STRONG BUY (Oversold + Bullish News)"
        if sentiment_score < -0.2 and rsi > 70:
            return "STRONG SELL (Overbought + Bearish News)"
        return "Neutral / Wait"
