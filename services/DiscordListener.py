import os
import sys
import asyncio
import discord
from discord.ext import commands

# --- ROBUST PATH INJECTION ---
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🛡️ Zenith Command Online | Session Active")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Market Intelligence"))

@bot.command(name='zenith')
async def zenith(ctx, ticker: str = "BTC"):
    ticker = ticker.upper()
    status_msg = await ctx.send(f"🛰️ **Vanguard Nexus** scanning `{ticker}` news and technicals...")
    
    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        # Execute Intelligence Cycle
        raw_news = ingestor.fetch_latest_news(ticker)
        intel = worker.process_pending_data(raw_news, ticker=ticker)

        if not intel or intel.get('current_price', 0) == 0:
            await status_msg.edit(content=f"❌ **API Limit Reached:** Could not pull data for `{ticker}`. Try again in 60s.")
            return

        zones = intel['zones']
        embed_color = 0x22c55e if "BUY" in intel['confluence_signal'] else 0xef4444 if "SELL" in intel['confluence_signal'] else 0x3b82f6

        embed = discord.Embed(
            title=f"🛡️ ZENITH REPORT: {ticker}",
            color=embed_color,
            description=f"**Signal:** {intel['confluence_signal']}"
        )
        
        # 1. Market Metrics
        embed.add_field(name="Spot Price", value=f"`${intel['current_price']:,.2f}`", inline=True)
        embed.add_field(name="RSI (14)", value=f"`{intel['rsi']}`", inline=True)
        embed.add_field(name="Sentiment", value=f"`{intel['aggregate_score']}`", inline=True)
        
        # 2. Tactical Zones
        embed.add_field(name="🟢 Entry", value=f"`${zones['entry']:,.2f}`", inline=True)
        embed.add_field(name="🎯 TP", value=f"`${zones['tp']:,.2f}`", inline=True)
        embed.add_field(name="🔴 SL", value=f"`${zones['sl']:,.2f}`", inline=True)

        # 3. Intelligence Summary (New Feature)
        if raw_news:
            headlines = "\n".join([f"• {n['title'][:80]}..." for n in raw_news[:3]])
            embed.add_field(name="📰 Driving Intelligence", value=headlines, inline=False)

        embed.set_footer(text="Zenith Command • Verified Intelligence")
        await status_msg.edit(content=None, embed=embed)

    except Exception as e:
        await ctx.send(f"⚠️ **Engine Failure:** `{str(e)}`")

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token:
        bot.run(token)
    else:
        print("CRITICAL: DISCORD_BOT_TOKEN missing.")
