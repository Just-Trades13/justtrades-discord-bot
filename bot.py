#!/usr/bin/env python3
"""
JustTrades Combined Discord Bot
All bots merged into one for Railway deployment
Uses ! prefix commands (NOT slash commands)
"""
import discord
from discord.ext import commands
import os
import logging
from datetime import datetime
import pytz

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
        logger.info("All commands use ! prefix")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the markets | !bothelp"
            )
        )

bot = JustTradesBot()

@bot.command(name="bothelp")
async def bot_help(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="JustTrades Bot Commands",
        description="All-in-one trading Discord bot\n**All commands use `!` prefix**",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Market Data",
        value="`!market` - Live futures prices\n`!price <symbol>` - Any symbol price\n`!bias <direction> <notes>` - Post daily bias\n`!markethelp` - Market commands help",
        inline=False
    )

    embed.add_field(
        name="Analysis",
        value="`!setup <symbol> <long/short> <entry> <stop> <target>` - Chart setup\n`!levels <symbol> <S1> <R1>` - S/R levels\n`!dailybias` - AI daily bias with live data",
        inline=False
    )

    embed.add_field(
        name="Education",
        value="`!define <term>` - Trading term definition\n`!terms` - List all terms\n`!tip` - Random trading tip\n`!eduhelp` - Education commands help",
        inline=False
    )

    embed.add_field(
        name="Trade Relay",
        value="`!alert <symbol> <BUY/SELL> <entry> <stop> <target>` - Trade alert\n`!close <symbol> <WIN/LOSS> <pnl>` - Trade result\n`!update <symbol> <text>` - Trade update\n`!tradehelp` - Trade commands help",
        inline=False
    )

    embed.add_field(
        name="Calendar",
        value="`!calendar [days]` - Economic calendar\n`!eventadd` - Add event\n`!eventlist` - List events\n`!postcalendar` - Post to channel",
        inline=False
    )

    embed.add_field(
        name="Auto-Posting",
        value="**Daily Bias:** 8:30 AM CT (weekdays)\n**Weekly Calendar:** Mondays 6:00 AM CT",
        inline=False
    )

    embed.set_footer(text="JustTrades Bot | Railway Deployment | All ! prefix commands")
    await ctx.send(embed=embed)

@bot.command(name="status")
async def bot_status(ctx):
    """Show bot status"""
    now = datetime.now(bot.ct)

    embed = discord.Embed(
        title="Bot Status",
        color=discord.Color.green()
    )
    embed.add_field(name="Status", value="Online", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guilds", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Time (CT)", value=now.strftime("%I:%M %p"), inline=True)
    embed.add_field(name="Prefix", value="`!`", inline=True)
    embed.set_footer(text="JustTrades Bot | Railway Deployment")

    await ctx.send(embed=embed)

@bot.command(name="channels")
async def channels_command(ctx):
    """Show configured channels"""
    embed = discord.Embed(
        title="Configured Channels",
        color=discord.Color.blue()
    )

    for name, channel_id in CHANNELS.items():
        channel = bot.get_channel(channel_id)
        status = f"<#{channel_id}>" if channel else f"Not found ({channel_id})"
        embed.add_field(name=name.replace('_', ' ').title(), value=status, inline=True)

    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
