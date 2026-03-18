import sys
import os
import time
import random

# Path Guard: Ensures 'core' and 'services' are findable from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.SentimentEngine import MarketSentimentEngine
from services.ServiceRegistry import ServiceRegistry

class VanguardStressTester:
    """Verifies system stability under high-velocity data influx."""
    def __init__(self):
        self.engine = MarketSentimentEngine()
        self.samples = [
            "Market surges as adoption hits record highs!",
            "Regulators announce strict new guidelines.",
            "Sudden flash crash wipes out positions.",
            "Institutional investors are accumulating."
        ]

    def run_test(self, count=1000):
        # Generate raw data (No hardcoding)
        payload = [
            {"text": random.choice(self.samples), "source": "social_media"} 
            for _ in range(count)
        ]
        
        start = time.perf_counter()
        results = self.engine.calculate_weighted_sentiment(payload)
        end = time.perf_counter()
        
        report = {
            "items": count,
            "seconds": round(end - start, 4),
            "throughput": round(count / (end - start), 2),
            "final_score": results["aggregate_score"]
        }
        
        # Save to Registry for UI/Logs
        ServiceRegistry.save_state("stress_test", report)
        return report

if __name__ == "__main__":
    tester = VanguardStressTester()
    print("🚀 Running Vanguard Nexus Stress Test...")
    report = tester.run_test(count=2000)
    print(f"✅ Success! Throughput: {report['throughput']} items/sec")
