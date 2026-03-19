import os
import discord
from discord.ext import commands
import sys
import asyncio

# --- PATH INJECTOR: Root access for core/services ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker

# Initialize Bot with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🛡️ Vanguard Nexus Listener Online. Logged in as {bot.user}")

@bot.command(name='zenith')
async def zenith_cycle(ctx, ticker: str = "BTC"):
    """
    Executes a real-time Zenith intelligence cycle.
    Usage: !zenith BTC
    """
    ticker = ticker.upper()
    await ctx.send(f"🔄 **Initiating Zenith Cycle for {ticker}...** Gathering intelligence.")

    # Run the ingestion and inference pipeline
    try:
        # Note: In a production async environment, heavy blocking API calls 
        # should ideally be run in an executor, but for this scale, standard calls work.
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            await ctx.send("🚨 System Failure: Alpha Vantage API Key missing.")
            return

        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        raw_news = ingestor.fetch_latest_news(ticker)
        intel = worker.process_pending_data(raw_news, ticker=ticker)

        if not intel or intel.get('current_price', 0) == 0:
            await ctx.send(f"⚠️ **Data Unavailable:** Could not pull spot price for {ticker}. API may be rate-limited.")
            return

        # Build the Tactical Output Embed
        zones = intel['zones']
        color = 0x22c55e if "BUY" in intel['confluence_signal'] else 0xef4444 if "SELL" in intel['confluence_signal'] else 0x3b82f6

        embed = discord.Embed(
            title=f"🛡️ ZENITH TACTICAL TICKET: {ticker}",
            description=f"**Signal:** {intel['confluence_signal']}",
            color=color
        )
        
        embed.add_field(name="Current Price", value=f"${intel['current_price']:,.2f}", inline=True)
        embed.add_field(name="RSI (14)", value=f"{intel['rsi']}", inline=True)
        embed.add_field(name="Sentiment Score", value=f"{intel['aggregate_score']} ({intel['sentiment_label']})", inline=True)
        
        embed.add_field(name="🟢 Entry Zone", value=f"${zones['entry']:,.2f}", inline=True)
        embed.add_field(name="🎯 Take Profit", value=f"${zones['tp']:,.2f}", inline=True)
        embed.add_field(name="🔴 Stop Loss", value=f"${zones['sl']:,.2f}", inline=True)
        
        embed.set_footer(text="Vanguard Nexus • Zenith Command")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"🚨 **Engine Error:** Failed to execute cycle. Detail: `{e}`")

if __name__ == "__main__":
    # You must set your Discord Bot Token in your environment variables
    # This is DIFFERENT from the Webhook URL.
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("CRITICAL: DISCORD_BOT_TOKEN environment variable not found.")
