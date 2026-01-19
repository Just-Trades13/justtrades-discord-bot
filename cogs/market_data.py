"""
Market Data Cog - Live prices and daily bias
"""
import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime
import pytz
import os

DAILY_BIAS_CHANNEL = int(os.environ.get('CHANNEL_DAILY_BIAS', '1358534746879037642'))

FUTURES_SYMBOLS = {
    "NQ=F": "NQ (Nasdaq)",
    "ES=F": "ES (S&P 500)",
    "YM=F": "YM (Dow)",
    "RTY=F": "RTY (Russell)",
    "GC=F": "Gold",
    "CL=F": "Crude Oil",
}

class MarketDataCog(commands.Cog, name="Market Data"):
    def __init__(self, bot):
        self.bot = bot
        self.ct = pytz.timezone('America/Chicago')

    def get_market_data(self):
        """Fetch current market data"""
        data = {}
        for symbol, name in FUTURES_SYMBOLS.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                price = info.get('lastPrice', 0)
                prev_close = info.get('previousClose', price)
                change = price - prev_close if prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0
                data[symbol] = {
                    'name': name,
                    'price': price,
                    'change': change,
                    'change_pct': change_pct
                }
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
        return data

    @commands.command(name="market", help="Get live prices for major futures")
    async def market_command(self, ctx):
        """!market - Get live market data"""
        async with ctx.typing():
            data = self.get_market_data()
            now = datetime.now(self.ct)

            embed = discord.Embed(
                title="Live Market Data",
                description=f"Updated: {now.strftime('%I:%M %p CT')}",
                color=discord.Color.blue()
            )

            for symbol, info in data.items():
                arrow = "+" if info['change'] >= 0 else ""
                color_indicator = "green" if info['change'] >= 0 else "red"
                embed.add_field(
                    name=info['name'],
                    value=f"**{info['price']:,.2f}**\n{arrow}{info['change']:,.2f} ({arrow}{info['change_pct']:.2f}%)",
                    inline=True
                )

            await ctx.send(embed=embed)

    @commands.command(name="price", help="Get price for a symbol. Usage: !price AAPL")
    async def price_command(self, ctx, symbol: str = None):
        """!price <symbol> - Get price for any symbol"""
        if not symbol:
            await ctx.send("Usage: `!price <symbol>` (e.g., `!price AAPL` or `!price NQ=F`)")
            return

        async with ctx.typing():
            try:
                ticker = yf.Ticker(symbol.upper())
                info = ticker.fast_info
                price = info.get('lastPrice', 0)
                prev_close = info.get('previousClose', price)
                change = price - prev_close if prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0

                sign = "+" if change >= 0 else ""
                color = discord.Color.green() if change >= 0 else discord.Color.red()

                embed = discord.Embed(title=f"{symbol.upper()}", color=color)
                embed.add_field(name="Price", value=f"**${price:,.2f}**", inline=True)
                embed.add_field(name="Change", value=f"{sign}{change:,.2f} ({sign}{change_pct:.2f}%)", inline=True)

                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"Error fetching {symbol}: {str(e)}")

    @commands.command(name="bias", help="Post daily bias. Usage: !bias bullish Looking for higher highs")
    async def bias_command(self, ctx, direction: str = None, *, notes: str = ""):
        """!bias <bullish/bearish/neutral> <notes> - Post daily market bias"""
        if not direction:
            await ctx.send("Usage: `!bias <bullish/bearish/neutral> <notes>`\nExample: `!bias bullish Looking for continuation above 21500`")
            return

        now = datetime.now(self.ct)

        if direction.lower() == "bullish":
            color = discord.Color.green()
            emoji = "BULLISH"
        elif direction.lower() == "bearish":
            color = discord.Color.red()
            emoji = "BEARISH"
        else:
            color = discord.Color.gold()
            emoji = "NEUTRAL"

        embed = discord.Embed(
            title=f"Daily Bias: {emoji}",
            description=notes if notes else "No additional notes",
            color=color,
            timestamp=now
        )
        embed.set_footer(text=f"Posted by {ctx.author.name}")

        channel = self.bot.get_channel(DAILY_BIAS_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await ctx.send("Daily bias posted to #daily-bias channel!")
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MarketDataCog(bot))
