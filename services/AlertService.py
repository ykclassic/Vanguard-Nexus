# Inside VanguardDiscordDispatcher...
def post_signal(self, ticker, zones, stance):
    payload = {
        "embeds": [{
            "title": f"⚡ ZENITH SIGNAL: {ticker}",
            "color": 16753920, # Gold color for signals
            "fields": [
                {"name": "Action", "value": f"**{stance}**", "inline": False},
                {"name": "Entry Zone", "value": f"`{zones['entry']}`", "inline": True},
                {"name": "Stop Loss", "value": f"`{zones['sl']}`", "inline": True},
                {"name": "Take Profit", "value": f"`{zones['tp']}`", "inline": True}
            ],
            "footer": {"text": "Automated by Vanguard Nexus Prophet Engine"}
        }]
    }
    requests.post(self.webhook_url, json=payload, timeout=10)
