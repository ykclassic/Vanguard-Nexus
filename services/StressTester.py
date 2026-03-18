import time
import random
from core.SentimentEngine import MarketSentimentEngine
from services.ServiceRegistry import ServiceRegistry

class VanguardStressTester:
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.samples = ["Surge imminent!", "Crash predicted.", "Neutral volume."]

    def run_test(self, count=5000):
        payload = [{"text": random.choice(self.samples), "source": "social_media"} for _ in range(count)]
        start = time.perf_counter()
        results = self.engine.calculate_weighted_sentiment(payload)
        end = time.perf_counter()
        
        report = {
            "items": count,
            "seconds": round(end - start, 4),
            "throughput": round(count / (end - start), 2),
            "final_score": results["aggregate_score"]
        }
        ServiceRegistry.save_state("stress_test", report)
        return report

if __name__ == "__main__":
    tester = VanguardStressTester()
    print(tester.run_test())
