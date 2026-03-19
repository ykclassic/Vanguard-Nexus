import os
import discord
from discord.ext import commands
import sys
import asyncio

# Path Injection
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🛡️ Vanguard Nexus Online | Logged in as: {bot.user}")
    # Activity Status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Market Cycles"))

@bot.command(name='zenith')
async def zenith(ctx, ticker: str = "BTC"):
    ticker = ticker.upper()
    await ctx.send(f"🛰️ **Vanguard Nexus** is scanning `{ticker}`... Standby.")
    
    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        raw = ingestor.fetch_latest_news(ticker)
        intel = worker.process_pending_data(raw, ticker=ticker)

        if not intel or intel.get('current_price', 0) == 0:
            await ctx.send("❌ **Error:** API Rate limited or ticker invalid.")
            return

        zones = intel['zones']
        embed = discord.Embed(
            title=f"🛡️ ZENITH REPORT: {ticker}",
            color=0x22c55e if "BUY" in intel['confluence_signal'] else 0xef4444,
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="Signal", value=f"**{intel['confluence_signal']}**", inline=False)
        embed.add_field(name="Spot Price", value=f"${intel['current_price']:,.2f}", inline=True)
        embed.add_field(name="RSI", value=f"{intel['rsi']}", inline=True)
        
        embed.add_field(name="🟢 Entry", value=f"`${zones['entry']:,.2f}`", inline=True)
        embed.add_field(name="🎯 TP", value=f"`${zones['tp']:,.2f}`", inline=True)
        embed.add_field(name="🔴 SL", value=f"`${zones['sl']:,.2f}`", inline=True)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Engine Failure: `{str(e)}`")

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_BOT_TOKEN not found.")
