import os
import sys
import asyncio
import discord
from discord.ext import commands, tasks

# --- ROBUST PATH INJECTION ---
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker

WATCHLIST = {} 

# Ensure Intents are fully declared
intents = discord.Intents.default()
intents.message_content = True  # CRITICAL: Must be enabled in Portal too
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🛡️ Zenith Online | User: {bot.user} | ID: {bot.user.id}")
    if not price_monitor.is_running():
        price_monitor.start()

@bot.event
async def on_message(message):
    # Debug: This will show in GitHub Action logs
    if message.author == bot.user:
        return
    print(f"📩 Message detected: '{message.content}' from {message.author}")
    await bot.process_commands(message)

@tasks.loop(minutes=2)
async def price_monitor():
    if not WATCHLIST: return
    worker = InferenceWorker()
    for ticker, data in list(WATCHLIST.items()):
        current_price = worker._get_live_spot_price(ticker)
        if current_price == 0: continue
        
        triggered = False
        if current_price >= data['tp']:
            msg, color, triggered = f"🎯 TP HIT: `{ticker}` @ ${current_price:,.2f}", 0x22c55e, True
        elif current_price <= data['sl']:
            msg, color, triggered = f"🛑 SL HIT: `{ticker}` @ ${current_price:,.2f}", 0xef4444, True

        if triggered:
            channel = bot.get_channel(data['channel_id'])
            if channel:
                await channel.send(embed=discord.Embed(title="🛡️ ZENITH ALERT", description=msg, color=color))
            del WATCHLIST[ticker]

@bot.command(name='track')
async def track(ctx, ticker: str = "BTC"):
    ticker = ticker.upper()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    worker = InferenceWorker()
    
    await ctx.send(f"🛰️ Establishing sentry for `{ticker}`...")
    
    raw = FinancialDataIngestor(api_key).fetch_latest_news(ticker)
    intel = worker.process_pending_data(raw, ticker=ticker)
    
    if intel and intel['current_price'] > 0:
        WATCHLIST[ticker] = {
            "tp": intel['zones']['tp'],
            "sl": intel['zones']['sl'],
            "channel_id": ctx.channel.id
        }
        embed = discord.Embed(title=f"📡 MONITORING: {ticker}", color=0x38bdf8)
        embed.add_field(name="Target (TP)", value=f"`${intel['zones']['tp']:,.2f}`")
        embed.add_field(name="Floor (SL)", value=f"`${intel['zones']['sl']:,.2f}`")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Error: Could not fetch price. API limit?")

@bot.command(name='zenith')
async def zenith(ctx, ticker: str = "BTC"):
    ticker = ticker.upper()
    worker = InferenceWorker()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    raw = FinancialDataIngestor(api_key).fetch_latest_news(ticker)
    intel = worker.process_pending_data(raw, ticker=ticker)
    
    if intel:
        embed = discord.Embed(title=f"🛡️ ZENITH REPORT: {ticker}", color=0x3b82f6)
        embed.add_field(name="Signal", value=f"**{intel['confluence_signal']}**", inline=False)
        embed.add_field(name="Price", value=f"`${intel['current_price']:,.2f}`", inline=True)
        await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
