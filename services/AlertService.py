import requests
import os

class VanguardDiscordDispatcher:
    """Sends rich media alerts to Discord for Vanguard Nexus."""
    def __init__(self):
        # Ensure this is set in your Streamlit / GitHub Secrets
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def post_intelligence(self, intel, ticker="BTC"):
        """Posts a formatted embed to the configured Discord channel."""
        if not self.webhook_url:
            print("⚠️ Discord Webhook URL missing. Skipping alert.")
            return

        # Visual indicator: Green for Bullish, Red for Bearish
        color = 3066993 if intel['aggregate_score'] >= 0 else 15158332 
        
        payload = {
            "username": "Vanguard Nexus Bot",
            "embeds": [{
                "title": f"🛡️ Intel Update: {ticker}",
                "color": color,
                "fields": [
                    {"name": "Score", "value": f"`{intel['aggregate_score']}`", "inline": True},
                    {"name": "Stance", "value": f"**{intel['sentiment_label']}**", "inline": True},
                    {"name": "Samples", "value": f"{intel['sample_size']}", "inline": True}
                ],
                "footer": {"text": "Vanguard Nexus Intelligence Hub"}
            }]
        }

        try:
            # Bandit B113 Fix: Added timeout
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            print(f"Discord Dispatch Error: {e}")
