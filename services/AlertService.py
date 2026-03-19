import requests
import os

class VanguardDiscordDispatcher:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def post_zenith_signal(self, ticker, intel):
        if not self.webhook_url: return

        zones = intel['zones']
        payload = {
            "username": "Zenith Command",
            "embeds": [{
                "title": f"🛡️ ZENITH SIGNAL: {ticker}",
                "description": f"**Signal:** {intel['confluence_signal']}",
                "color": 16753920 if "BUY" in intel['confluence_signal'] else 15158332,
                "fields": [
                    {"name": "Price", "value": f"${intel['current_price']}", "inline": True},
                    {"name": "RSI", "value": f"{intel['rsi']}", "inline": True},
                    {"name": "Sentiment", "value": f"{intel['aggregate_score']}", "inline": True},
                    {"name": "Entry", "value": f"`{zones['entry']}`", "inline": True},
                    {"name": "Stop Loss", "value": f"`{zones['sl']}`", "inline": True},
                    {"name": "Take Profit", "value": f"`{zones['tp']}`", "inline": True}
                ],
                "footer": {"text": "Vanguard Nexus Zenith Edition • 2026"}
            }]
        }
        requests.post(self.webhook_url, json=payload, timeout=10)
