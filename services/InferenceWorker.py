from core.SentimentEngine import MarketSentimentEngine
from services.ServiceRegistry import ServiceRegistry
from services.AlertService import VanguardDiscordDispatcher

class InferenceWorker:
    """The bridge between raw data ingestion and actionable intelligence."""
    
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.dispatcher = VanguardDiscordDispatcher()

    def process_pending_data(self, raw_data, ticker="BTC"):
        """
        Processes raw feed into sentiment and dispatches alerts.
        Accepts 'ticker' to resolve the TypeError in the UI.
        """
        if not raw_data:
            return None
        
        # 1. Generate Sentiment Analysis
        intelligence = self.engine.calculate_weighted_sentiment(raw_data)
        
        # 2. Update the Microservices Registry (system_state.json)
        ServiceRegistry.save_state("inference_service", intelligence)
        
        # 3. Trigger Discord Notification
        # We pass the ticker here so the Discord message is context-aware
        self.dispatcher.post_intelligence(intelligence, ticker=ticker)
        
        return intelligence
