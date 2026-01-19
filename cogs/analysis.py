"""
Analysis Cog - Chart setups and technical analysis
Uses ! prefix commands (NOT slash commands)
"""
import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import pytz
import os

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

CHART_SETUPS_CHANNEL = int(os.environ.get('CHANNEL_CHART_SETUPS', '1367383497689268286'))
DAILY_BIAS_CHANNEL = int(os.environ.get('CHANNEL_DAILY_BIAS', '1358534746879037642'))

class AnalysisCog(commands.Cog, name="Analysis"):
    def __init__(self, bot):
        self.bot = bot
        self.ct = pytz.timezone('America/Chicago')
        # Start auto-posting task
        self.daily_bias_post.start()

    def cog_unload(self):
        self.daily_bias_post.cancel()

    def get_market_data(self):
        """Fetch real market data using yfinance"""
        if not YFINANCE_AVAILABLE:
            return None

        try:
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1mo")
            if spy_hist.empty:
                return None

            spy_price = spy_hist['Close'].iloc[-1]
            spy_prev = spy_hist['Close'].iloc[-2] if len(spy_hist) > 1 else spy_price
            spy_change = spy_price - spy_prev
            spy_change_pct = (spy_change / spy_prev) * 100 if spy_prev else 0
            spy_high_20 = spy_hist['High'].tail(20).max()
            spy_low_20 = spy_hist['Low'].tail(20).min()

            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="5d")
            vix_price = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 0

            nq = yf.Ticker("NQ=F")
            nq_hist = nq.history(period="5d")
            nq_price = nq_hist['Close'].iloc[-1] if not nq_hist.empty else 0
            nq_prev = nq_hist['Close'].iloc[-2] if len(nq_hist) > 1 else nq_price
            nq_change = nq_price - nq_prev

            es = yf.Ticker("ES=F")
            es_hist = es.history(period="5d")
            es_price = es_hist['Close'].iloc[-1] if not es_hist.empty else 0
            es_prev = es_hist['Close'].iloc[-2] if len(es_hist) > 1 else es_price
            es_change = es_price - es_prev

            return {
                'spy_price': spy_price, 'spy_change': spy_change, 'spy_change_pct': spy_change_pct,
                'spy_support': spy_low_20, 'spy_resistance': spy_high_20,
                'vix': vix_price, 'nq_price': nq_price, 'nq_change': nq_change,
                'es_price': es_price, 'es_change': es_change
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None

    def determine_bias(self, data):
        """Determine market bias based on data"""
        if not data:
            return "NEUTRAL", discord.Color.gold()

        spy_price = data['spy_price']
        support = data['spy_support']
        resistance = data['spy_resistance']
        vix = data['vix']

        range_size = resistance - support
        mid_point = support + (range_size / 2)

        if vix > 25:
            return "CAUTIOUS", discord.Color.orange()
        if spy_price > mid_point + (range_size * 0.3):
            return ("BULLISH", discord.Color.green()) if data['spy_change'] > 0 else ("NEUTRAL", discord.Color.gold())
        elif spy_price < mid_point - (range_size * 0.3):
            return ("BEARISH", discord.Color.red()) if data['spy_change'] < 0 else ("NEUTRAL", discord.Color.gold())
        else:
            if data['spy_change'] > 0:
                return "BULLISH", discord.Color.green()
            elif data['spy_change'] < 0:
                return "BEARISH", discord.Color.red()
            return "NEUTRAL", discord.Color.gold()

    @tasks.loop(time=time(hour=8, minute=30, tzinfo=pytz.timezone('America/Chicago')))
    async def daily_bias_post(self):
        """Auto-post daily bias at 8:30 AM CT (weekdays only)"""
        now = datetime.now(self.ct)
        if now.weekday() >= 5:
            return

        channel = self.bot.get_channel(DAILY_BIAS_CHANNEL)
        if not channel:
            return

        data = self.get_market_data()
        bias, color = self.determine_bias(data)

        embed = discord.Embed(title=f"Daily Market Bias: {bias}", color=color, timestamp=now)

        if data:
            spy_sign = "+" if data['spy_change'] >= 0 else ""
            nq_sign = "+" if data['nq_change'] >= 0 else ""
            es_sign = "+" if data['es_change'] >= 0 else ""

            embed.add_field(
                name="Live Market Data",
                value=f"**SPY:** ${data['spy_price']:.2f} ({spy_sign}{data['spy_change']:.2f}, {spy_sign}{data['spy_change_pct']:.2f}%)\n"
                      f"**NQ:** {data['nq_price']:,.2f} ({nq_sign}{data['nq_change']:.2f})\n"
                      f"**ES:** {data['es_price']:,.2f} ({es_sign}{data['es_change']:.2f})\n"
                      f"**VIX:** {data['vix']:.2f}",
                inline=False
            )
            embed.add_field(
                name="Key Levels (20-Day)",
                value=f"**Support:** ${data['spy_support']:.2f}\n**Resistance:** ${data['spy_resistance']:.2f}",
                inline=True
            )

        embed.set_footer(text="Analysis Cog | Auto-posted at 8:30 AM CT")
        await channel.send(embed=embed)

    @daily_bias_post.before_loop
    async def before_daily_bias(self):
        await self.bot.wait_until_ready()

    @commands.command(name="setup", help="Post a chart setup. Usage: !setup NQ long 21500 21480 21560 [notes]")
    async def setup_command(self, ctx, symbol: str = None, direction: str = None, entry: float = None, stop: float = None, target: float = None, *, notes: str = ""):
        """!setup <symbol> <long/short> <entry> <stop> <target> [notes]"""
        if not all([symbol, direction, entry, stop, target]):
            await ctx.send("**Usage:** `!setup <symbol> <long/short> <entry> <stop> <target> [notes]`\n"
                          "**Example:** `!setup NQ long 21500 21480 21560 Breaking resistance`")
            return

        now = datetime.now(self.ct)
        risk = abs(entry - stop)
        reward = abs(target - entry)
        rr_ratio = reward / risk if risk > 0 else 0

        color = discord.Color.green() if direction.lower() == "long" else discord.Color.red()

        embed = discord.Embed(title=f"{symbol.upper()} - {direction.upper()}", color=color, timestamp=now)
        embed.add_field(name="Entry", value=f"**{entry:,.2f}**", inline=True)
        embed.add_field(name="Stop Loss", value=f"**{stop:,.2f}**", inline=True)
        embed.add_field(name="Target", value=f"**{target:,.2f}**", inline=True)
        embed.add_field(name="Risk", value=f"{risk:,.2f} pts", inline=True)
        embed.add_field(name="Reward", value=f"{reward:,.2f} pts", inline=True)
        embed.add_field(name="R:R", value=f"1:{rr_ratio:.1f}", inline=True)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        embed.set_footer(text=f"Posted by {ctx.author.name}")

        channel = self.bot.get_channel(CHART_SETUPS_CHANNEL)
        if channel and channel.id != ctx.channel.id:
            await channel.send(embed=embed)
            await ctx.send(f"Chart setup posted to <#{CHART_SETUPS_CHANNEL}>!")
        else:
            await ctx.send(embed=embed)

    @commands.command(name="levels", help="Post S/R levels. Usage: !levels NQ 21400 21600 [21350] [21650] [notes]")
    async def levels_command(self, ctx, symbol: str = None, support1: float = None, resistance1: float = None, support2: float = None, resistance2: float = None, *, notes: str = ""):
        """!levels <symbol> <support1> <resistance1> [support2] [resistance2] [notes]"""
        if not all([symbol, support1, resistance1]):
            await ctx.send("**Usage:** `!levels <symbol> <support1> <resistance1> [support2] [resistance2] [notes]`")
            return

        now = datetime.now(self.ct)
        embed = discord.Embed(title=f"{symbol.upper()} Key Levels", color=discord.Color.blue(), timestamp=now)

        support_text = f"S1: **{support1:,.2f}**"
        if support2:
            support_text += f"\nS2: **{support2:,.2f}**"
        resistance_text = f"R1: **{resistance1:,.2f}**"
        if resistance2:
            resistance_text += f"\nR2: **{resistance2:,.2f}**"

        embed.add_field(name="Support", value=support_text, inline=True)
        embed.add_field(name="Resistance", value=resistance_text, inline=True)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        embed.set_footer(text=f"Posted by {ctx.author.name}")

        channel = self.bot.get_channel(CHART_SETUPS_CHANNEL)
        if channel and channel.id != ctx.channel.id:
            await channel.send(embed=embed)
            await ctx.send(f"Levels posted to <#{CHART_SETUPS_CHANNEL}>!")
        else:
            await ctx.send(embed=embed)

    @commands.command(name="dailybias", help="Post daily bias with live market data")
    async def dailybias_command(self, ctx):
        """!dailybias - Post daily market bias with real SPY/VIX data"""
        now = datetime.now(self.ct)

        async with ctx.typing():
            data = self.get_market_data()
            bias, color = self.determine_bias(data)

            embed = discord.Embed(title=f"Daily Market Bias: {bias}", color=color, timestamp=now)

            if data:
                spy_sign = "+" if data['spy_change'] >= 0 else ""
                nq_sign = "+" if data['nq_change'] >= 0 else ""
                es_sign = "+" if data['es_change'] >= 0 else ""

                embed.add_field(
                    name="Live Market Data",
                    value=f"**SPY:** ${data['spy_price']:.2f} ({spy_sign}{data['spy_change']:.2f}, {spy_sign}{data['spy_change_pct']:.2f}%)\n"
                          f"**NQ:** {data['nq_price']:,.2f} ({nq_sign}{data['nq_change']:.2f})\n"
                          f"**ES:** {data['es_price']:,.2f} ({es_sign}{data['es_change']:.2f})\n"
                          f"**VIX:** {data['vix']:.2f}",
                    inline=False
                )
                embed.add_field(
                    name="Key Levels (20-Day)",
                    value=f"**Support:** ${data['spy_support']:.2f}\n**Resistance:** ${data['spy_resistance']:.2f}",
                    inline=True
                )
            else:
                embed.add_field(name="Market Data", value="Unable to fetch live data.", inline=False)

            embed.set_footer(text=f"Requested by {ctx.author.name}")

        channel = self.bot.get_channel(DAILY_BIAS_CHANNEL)
        if channel and channel.id != ctx.channel.id:
            await channel.send(embed=embed)
            await ctx.send(f"Daily bias posted to <#{DAILY_BIAS_CHANNEL}>!")
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AnalysisCog(bot))
