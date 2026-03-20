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

# Global Monitor Storage
WATCHLIST = {} 

# Intent Configuration
intents = discord.Intents.default()
intents.message_content = True  
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"🛡️ Vanguard Nexus Active | Identity: {bot.user}")
    if not price_monitor.is_running():
        price_monitor.start()

# --- BACKGROUND MONITOR ---
@tasks.loop(minutes=2)
async def price_monitor():
    if not WATCHLIST: return
    worker = InferenceWorker()
    for ticker, data in list(WATCHLIST.items()):
        # Pulling price + source for the monitor logs
        current_price, source = worker._get_live_price(ticker)
        if current_price <= 0: continue
        
        triggered = False
        if current_price >= data['tp']:
            msg, color, triggered = f"🎯 **TAKE PROFIT HIT**\n`{ticker}` reached target `${current_price:,.2f}`", 0x22c55e, True
        elif current_price <= data['sl']:
            msg, color, triggered = f"🛑 **STOP LOSS HIT**\n`{ticker}` reached floor `${current_price:,.2f}`", 0xef4444, True

        if triggered:
            channel = bot.get_channel(data['channel_id'])
            if channel:
                embed = discord.Embed(title="🛡️ ZENITH PRICE ALERT", description=msg, color=color)
                embed.set_footer(text=f"Verified via {source}")
                await channel.send(embed=embed)
            del WATCHLIST[ticker]

# --- COMMAND REGISTRY ---

@bot.command(name='help')
async def help_cmd(ctx):
    """Displays the Vanguard Nexus Command Menu."""
    embed = discord.Embed(title="🛡️ Vanguard Nexus | Command Menu", color=0x3b82f6)
    embed.add_field(name="`!zenith <TICKER>`", value="Full intelligence report + Futures Price + Data Source.", inline=False)
    embed.add_field(name="`!track <TICKER>`", value="Sets a 24/7 price sentry for automated TP/SL alerts.", inline=False)
    embed.add_field(name="`!news <TICKER>`", value="View the top headlines currently influencing sentiment.", inline=False)
    embed.add_field(name="`!watchlist`", value="List all assets currently under active surveillance.", inline=False)
    embed.set_footer(text="Zenith Command v3.0 • Futures Enabled")
    await ctx.send(embed=embed)

@bot.command(name='zenith')
async def zenith(ctx, ticker: str = "BTC"):
    """Executes a cycle and identifies the source exchange."""
    ticker = ticker.upper()
    status = await ctx.send(f"🛰️ **Vanguard Nexus** querying {ticker} Futures triage...")
    
    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        raw_news = ingestor.fetch_latest_news(ticker)
        intel = worker.process_pending_data(raw_news, ticker=ticker)

        if not intel or intel['current_price'] == 0:
            await status.edit(content=f"❌ **Data Failure:** Connection to triage nodes failed for `{ticker}`.")
            return

        zones = intel['zones']
        embed = discord.Embed(
            title=f"🛡️ ZENITH REPORT: {ticker}",
            description=f"**Signal:** {intel['confluence_signal']}",
            color=0x22c55e if "BUY" in intel['confluence_signal'] else 0xef4444
        )
        
        embed.add_field(name="Futures Price", value=f"`${intel['current_price']:,.2f}`", inline=True)
        embed.add_field(name="Data Source", value=f"📡 `{intel['source']}`", inline=True)
        embed.add_field(name="RSI (14)", value=f"`{intel['rsi']}`", inline=True)
        
        embed.add_field(name="🟢 Entry", value=f"`${zones['entry']:,.2f}`", inline=True)
        embed.add_field(name="🎯 TP", value=f"`${zones['tp']:,.2f}`", inline=True)
        embed.add_field(name="🔴 SL", value=f"`${zones['sl']:,.2f}`", inline=True)

        embed.set_footer(text=f"Analysis driven by {intel['source']}")
        await status.edit(content=None, embed=embed)
    except Exception as e:
        await status.edit(content=f"⚠️ **Engine Error:** `{str(e)}`")

@bot.command(name='news')
async def news_headlines(ctx, ticker: str = "BTC"):
    """Directly fetch the headlines driving the Sentiment Score."""
    ticker = ticker.upper()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    ingestor = FinancialDataIngestor(api_key)
    
    await ctx.send(f"📰 Gathering latest intel for `{ticker}`...")
    articles = ingestor.fetch_latest_news(ticker)
    
    if not articles:
        await ctx.send("📭 No recent news found for this asset.")
        return

    embed = discord.Embed(title=f"📰 Intelligence Brief: {ticker}", color=0x3b82f6)
    for art in articles[:5]: # Show top 5
        embed.add_field(name=art['source'], value=f"[{art['title']}]({art['url']})", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='track')
async def track_asset(ctx, ticker: str = "BTC"):
    """Adds an asset to the background price monitor."""
    ticker = ticker.upper()
    worker = InferenceWorker()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    
    await ctx.send(f"🛰️ Establishing 24/7 Futures sentry for `{ticker}`...")
    
    raw = FinancialDataIngestor(api_key).fetch_latest_news(ticker)
    intel = worker.process_pending_data(raw, ticker=ticker)
    
    if intel and intel['current_price'] > 0:
        WATCHLIST[ticker] = {
            "tp": intel['zones']['tp'],
            "sl": intel['zones']['sl'],
            "channel_id": ctx.channel.id
        }
        await ctx.send(f"✅ **Monitoring Started.** Alerts for `{ticker}` will be sent here. (Source: {intel['source']})")
    else:
        await ctx.send("❌ Failed to initiate monitoring. Check API limits.")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
