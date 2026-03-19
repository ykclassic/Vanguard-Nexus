import requests
import os

class VanguardDiscordDispatcher:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def post_intelligence(self, intel, ticker="BTC"):
        if not self.webhook_url:
            print("Discord Webhook URL missing in environment.")
            return
            
        color = 3066993 if intel['aggregate_score'] >= 0 else 15158332 
        payload = {
            "embeds": [{
                "title": f"🛡️ Vanguard Nexus Intel: {ticker}",
                "color": color,
                "fields": [
                    {"name": "Score", "value": f"{intel['aggregate_score']}", "inline": True},
                    {"name": "Stance", "value": f"{intel['sentiment_label']}", "inline": True}
                ]
            }]
        }
        requests.post(self.webhook_url, json=payload, timeout=10)
