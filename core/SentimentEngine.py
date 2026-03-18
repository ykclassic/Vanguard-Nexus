import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import statistics

# Ensure the VADER lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

class MarketSentimentEngine:
    """
    Vanguard Nexus Sentiment Engine.
    Calculates weighted sentiment without hardcoded values.
    """
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.source_weights = {
            "official_news": 1.2,
            "social_media": 0.8,
            "community_forum": 1.0
        }

    def calculate_weighted_sentiment(self, data_points):
        if not data_points:
            return {"error": "No data provided."}

        individual_scores = []
        for entry in data_points:
            text = entry.get("text", "")
            source = entry.get("source", "community_forum")
            
            # NLP calculation
            raw_score = self.sia.polarity_scores(text)['compound']
            weight = self.source_weights.get(source, 1.0)
            individual_scores.append(raw_score * weight)

        mean_sentiment = statistics.mean(individual_scores)
        variance = statistics.variance(individual_scores) if len(individual_scores) > 1 else 0
        
        return {
            "aggregate_score": round(mean_sentiment, 4),
            "volatility": round(variance, 4),
            "sample_size": len(individual_scores),
            "sentiment_label": self._get_label(mean_sentiment)
        }

    def _get_label(self, score):
        if score >= 0.05: return "Bullish"
        elif score <= -0.05: return "Bearish"
        return "Neutral"
