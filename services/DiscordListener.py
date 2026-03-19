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

# --- Global Watchlist Storage ---
# In a larger app, this would be a database. For Zenith, we use an in-memory dictionary.
WATCHLIST = {} 

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🛡️ Zenith Command Online | Tracking Engine Active")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Price Action"))
    if not price_monitor.is_running():
        price_monitor.start()

# --- Background Task: The Sentry ---
@tasks.loop(minutes=2)
async def price_monitor():
    """Background loop that checks if any tracked assets hit SL or TP."""
    if not WATCHLIST:
        return

    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    worker = InferenceWorker()
    
    for ticker, data in list(WATCHLIST.items()):
        current_price = worker._get_live_spot_price(ticker)
        
        if current_price == 0:
            continue

        target_reached = False
        message = ""
        color = 0x3b82f6

        # Check TP
        if current_price >= data['tp']:
            message = f"🎯 **TAKE PROFIT REACHED:** `{ticker}` has hit target `${data['tp']:,.2f}` (Current: `${current_price:,.2f}`)"
            color = 0x22c55e
            target_reached = True
        
        # Check SL
        elif current_price <= data['sl']:
            message = f"🛑 **STOP LOSS TRIGGERED:** `{ticker}` has hit exit `${data['sl']:,.2f}` (Current: `${current_price:,.2f}`)"
            color = 0xef4444
            target_reached = True

        if target_reached:
            channel = bot.get_channel(data['channel_id'])
            if channel:
                embed = discord.Embed(title="🛡️ ZENITH ALERT", description=message, color=color)
                await channel.send(embed=embed)
            # Remove from watchlist after trigger
            del WATCHLIST[ticker]

# --- Commands ---

@bot.command(name='track')
async def track(ctx, ticker: str = "BTC"):
    """Runs a cycle and adds the asset to the persistent monitor."""
    ticker = ticker.upper()
    await ctx.send(f"🛰️ Scanning `{ticker}` and establishing price sentry...")

    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        raw = ingestor.fetch_latest_news(ticker)
        intel = worker.process_pending_data(raw, ticker=ticker)

        if not intel or intel['current_price'] == 0:
            await ctx.send("❌ Error: Could not establish a price baseline.")
            return

        # Add to Global Watchlist
        WATCHLIST[ticker] = {
            "entry": intel['zones']['entry'],
            "tp": intel['zones']['tp'],
            "sl": intel['zones']['sl'],
            "channel_id": ctx.channel.id
        }

        embed = discord.Embed(
            title=f"📡 MONITORING STARTED: {ticker}",
            description=f"Vanguard Nexus is now tracking `{ticker}` 24/7.",
            color=0x38bdf8
        )
        embed.add_field(name="Target (TP)", value=f"`${intel['zones']['tp']:,.2f}`", inline=True)
        embed.add_field(name="Floor (SL)", value=f"`${intel['zones']['sl']:,.2f}`", inline=True)
        embed.set_footer(text="Alerts will be sent to this channel upon target hit.")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠️ Track Failure: `{str(e)}`")

@bot.command(name='watchlist')
async def list_watchlist(ctx):
    """Shows all currently tracked assets."""
    if not WATCHLIST:
        await ctx.send("📭 Your watchlist is currently empty.")
        return

    embed = discord.Embed(title="📜 Active Zenith Watchlist", color=0x3b82f6)
    for ticker, d in WATCHLIST.items():
        embed.add_field(
            name=ticker, 
            value=f"Target: `${d['tp']:,.2f}` | Floor: `${d['sl']:,.2f}`", 
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name='zenith')
async def zenith(ctx, ticker: str = "BTC"):
    """Standard one-time analysis (maintained from previous update)."""
    # (Previous Zenith logic remains identical for one-off checks)
    ticker = ticker.upper()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    worker = InferenceWorker()
    raw = FinancialDataIngestor(api_key).fetch_latest_news(ticker)
    intel = worker.process_pending_data(raw, ticker=ticker)
    
    if intel:
        zones = intel['zones']
        embed = discord.Embed(title=f"🛡️ ZENITH REPORT: {ticker}", color=0x3b82f6)
        embed.add_field(name="Signal", value=f"**{intel['confluence_signal']}**", inline=False)
        embed.add_field(name="Price", value=f"`${intel['current_price']:,.2f}`", inline=True)
        embed.add_field(name="TP", value=f"`${zones['tp']:,.2f}`", inline=True)
        embed.add_field(name="SL", value=f"`${zones['sl']:,.2f}`", inline=True)
        await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token:
        bot.run(token)
    else:
        print("CRITICAL: DISCORD_BOT_TOKEN not found.")
