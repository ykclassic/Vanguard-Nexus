from core.SentimentEngine import MarketSentimentEngine
from services.ServiceRegistry import ServiceRegistry

class InferenceWorker:
    def __init__(self):
        self.engine = MarketSentimentEngine()

    def process_pending_data(self, raw_data):
        if not raw_data: return None
        intelligence = self.engine.calculate_weighted_sentiment(raw_data)
        ServiceRegistry.save_state("inference_service", intelligence)
        return intelligence
