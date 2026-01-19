#!/usr/bin/env python3
"""
JustTrades Combined Discord Bot
All bots merged into one for Railway deployment
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import logging
from datetime import datetime, timedelta
import pytz
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('JustTradesBot')

# Environment variables for tokens and config
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
if not TOKEN:
    raise SystemExit("Missing DISCORD_BOT_TOKEN environment variable")

# Channel IDs (set via environment or defaults)
CHANNELS = {
    'news_headlines': int(os.environ.get('CHANNEL_NEWS_HEADLINES', '1420078847629590608')),
    'daily_bias': int(os.environ.get('CHANNEL_DAILY_BIAS', '1358534746879037642')),
    'breaking_news': int(os.environ.get('CHANNEL_BREAKING_NEWS', '1347337500380893296')),
    'live_trades': int(os.environ.get('CHANNEL_LIVE_TRADES', '1347337979751829659')),
    'trade_setups': int(os.environ.get('CHANNEL_TRADE_SETUPS', '1347337927637602365')),
    'chart_setups': int(os.environ.get('CHANNEL_CHART_SETUPS', '1367383497689268286')),
    'trading_glossary': int(os.environ.get('CHANNEL_TRADING_GLOSSARY', '1358534448332935420')),
    'economic_calendar': int(os.environ.get('CHANNEL_ECONOMIC_CALENDAR', '1359875411470716959')),
    'trade_alerts': int(os.environ.get('CHANNEL_TRADE_ALERTS', '1358534900780630067')),
}

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

class JustTradesBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.ct = pytz.timezone('America/Chicago')

    async def setup_hook(self):
        # Load all cogs
        await self.load_extension('cogs.market_data')
        await self.load_extension('cogs.education')
        await self.load_extension('cogs.analysis')
        await self.load_extension('cogs.trade_relay')
        await self.load_extension('cogs.calendar')
        logger.info("All cogs loaded successfully")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")

        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the markets | !help"
            )
        )

bot = JustTradesBot()

@bot.command(name="bothelp")
async def bot_help(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="JustTrades Bot Commands",
        description="All-in-one trading Discord bot",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Market Data",
        value="`!market` - Live futures prices\n`!price <symbol>` - Any symbol price\n`!bias <direction> <notes>` - Post daily bias",
        inline=False
    )

    embed.add_field(
        name="Education",
        value="`!define <term>` - Trading term definition\n`!terms` - List all terms\n`!tip` - Random trading tip",
        inline=False
    )

    embed.add_field(
        name="Trade Relay",
        value="`!alert <symbol> <BUY/SELL> <entry> <stop> <target>` - Post trade alert\n`!close <symbol> <WIN/LOSS> <pnl>` - Post trade result\n`!update <symbol> <text>` - Trade update",
        inline=False
    )

    embed.add_field(
        name="Slash Commands",
        value="`/setup` - Post chart setup\n`/levels` - Post S/R levels\n`/calendar` - Economic calendar\n`/event-add` - Add calendar event",
        inline=False
    )

    embed.set_footer(text="JustTrades Bot | Running on Railway")
    await ctx.send(embed=embed)

@bot.command(name="status")
async def bot_status(ctx):
    """Show bot status"""
    now = datetime.now(bot.ct)
    uptime = datetime.utcnow() - bot.user.created_at.replace(tzinfo=None)

    embed = discord.Embed(
        title="Bot Status",
        color=discord.Color.green()
    )
    embed.add_field(name="Status", value="Online", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guilds", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Time (CT)", value=now.strftime("%I:%M %p"), inline=True)
    embed.set_footer(text="JustTrades Bot | Railway Deployment")

    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
