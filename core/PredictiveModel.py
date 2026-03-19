import numpy as np
from services.ServiceRegistry import ServiceRegistry

class VanguardProphet:
    """Predictive logic using sentiment velocity and price divergence."""
    
    def __init__(self):
        self.lookback_period = 10

    def predict_trend_shift(self, current_score, historical_scores):
        """Calculates if sentiment is accelerating or decelerating."""
        if len(historical_scores) < 2:
            return "Stable"
            
        # Sentiment Velocity: (Current - Previous)
        velocity = current_score - historical_scores[-1]
        
        # If velocity is high, a 'Breakout' is predicted
        if velocity > 0.15: return "Accelerating (Breakout Potential)"
        elif velocity < -0.15: return "Decelerating (Crash Risk)"
        return "Consolidating"

    def calculate_trade_zones(self, current_price, volatility):
        """Generates SL/TP based on ATR-style volatility."""
        # Risk-to-Reward 1:2 logic
        stop_loss = current_price * (1 - (volatility * 0.05))
        take_profit = current_price * (1 + (volatility * 0.10))
        
        return {
            "entry": round(current_price, 2),
            "sl": round(stop_loss, 2),
            "tp": round(take_profit, 2)
        }
