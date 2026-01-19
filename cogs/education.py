"""
Education Cog - Trading terms and tips
"""
import discord
from discord.ext import commands
import random
import os

TRADING_GLOSSARY_CHANNEL = int(os.environ.get('CHANNEL_TRADING_GLOSSARY', '1358534448332935420'))

TRADING_TERMS = {
    "support": {
        "title": "Support Level",
        "definition": "A price level where buying pressure is strong enough to prevent the price from declining further.",
        "example": "If NQ bounces off 21,000 multiple times, 21,000 is a support level."
    },
    "resistance": {
        "title": "Resistance Level",
        "definition": "A price level where selling pressure is strong enough to prevent the price from rising further.",
        "example": "If ES keeps failing to break above 6,100, that's a resistance level."
    },
    "breakout": {
        "title": "Breakout",
        "definition": "When price moves above resistance or below support with increased volume.",
        "example": "NQ breaking above 21,500 resistance with high volume signals a bullish breakout."
    },
    "pullback": {
        "title": "Pullback",
        "definition": "A temporary reversal in the direction of a trend, often providing entry opportunities.",
        "example": "After rallying 200 points, NQ pulls back 50 points before continuing higher."
    },
    "scalping": {
        "title": "Scalping",
        "definition": "A trading strategy that profits from small price changes, typically holding positions for seconds to minutes.",
        "example": "Buying NQ and selling 5-10 points higher within a few minutes."
    },
    "swing": {
        "title": "Swing Trading",
        "definition": "A trading style that holds positions for days to weeks to capture larger price moves.",
        "example": "Buying ES on Monday and holding until the expected move completes on Thursday."
    },
    "stoploss": {
        "title": "Stop Loss",
        "definition": "An order to sell a security when it reaches a certain price to limit potential losses.",
        "example": "Setting a stop loss 20 points below entry to limit risk."
    },
    "takeprofit": {
        "title": "Take Profit",
        "definition": "An order to close a position when it reaches a predetermined profit target.",
        "example": "Setting take profit 40 points above entry to lock in gains."
    },
    "riskreward": {
        "title": "Risk/Reward Ratio",
        "definition": "The ratio between potential loss and potential gain on a trade.",
        "example": "Risking 20 points to make 60 points = 1:3 risk/reward ratio."
    },
    "liquidity": {
        "title": "Liquidity",
        "definition": "How easily an asset can be bought or sold without affecting its price.",
        "example": "ES futures are highly liquid - you can enter/exit large positions easily."
    },
    "volatility": {
        "title": "Volatility",
        "definition": "The degree of price variation over time. Higher volatility = larger price swings.",
        "example": "During FOMC, volatility spikes as prices move rapidly."
    },
    "dca": {
        "title": "Dollar Cost Averaging (DCA)",
        "definition": "Investing a fixed amount at regular intervals regardless of price.",
        "example": "Buying $500 of SPY every week, regardless of the current price."
    },
    "fomo": {
        "title": "FOMO (Fear Of Missing Out)",
        "definition": "The anxiety that an exciting opportunity may be missed, leading to impulsive trades.",
        "example": "Chasing a stock after it's already up 20% because you don't want to miss more gains."
    },
    "fud": {
        "title": "FUD (Fear, Uncertainty, Doubt)",
        "definition": "Negative sentiment spread to cause panic selling.",
        "example": "Rumors about a company going bankrupt causing the stock to drop."
    },
}

TRADING_TIPS = [
    "**Tip:** Never risk more than 1-2% of your account on a single trade.",
    "**Tip:** Always have a trading plan before entering a position.",
    "**Tip:** The trend is your friend - trade with it, not against it.",
    "**Tip:** Cut losses quickly, let winners run.",
    "**Tip:** Don't revenge trade after a loss.",
    "**Tip:** Journal every trade to learn from your mistakes.",
    "**Tip:** Avoid trading during major news events unless you understand the risks.",
    "**Tip:** Position sizing is more important than win rate.",
    "**Tip:** Paper trade new strategies before using real money.",
    "**Tip:** Take breaks - overtrading leads to poor decisions.",
    "**Tip:** Focus on the process, not the outcome of individual trades.",
    "**Tip:** Higher timeframes show the bigger picture - always check them.",
    "**Tip:** Wait for confirmation before entering a trade.",
    "**Tip:** Never add to a losing position.",
    "**Tip:** Your edge comes from discipline, not predictions.",
]

class EducationCog(commands.Cog, name="Education"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="define", help="Define a trading term. Usage: !define support")
    async def define_command(self, ctx, term: str = None):
        """!define <term> - Get definition of a trading term"""
        if not term:
            available = ", ".join(TRADING_TERMS.keys())
            await ctx.send(f"Usage: `!define <term>`\n\n**Available terms:** {available}")
            return

        term_lower = term.lower().strip()

        if term_lower in TRADING_TERMS:
            info = TRADING_TERMS[term_lower]
            embed = discord.Embed(title=info['title'], color=discord.Color.blue())
            embed.add_field(name="Definition", value=info['definition'], inline=False)
            embed.add_field(name="Example", value=info['example'], inline=False)
            await ctx.send(embed=embed)
        else:
            available = ", ".join(TRADING_TERMS.keys())
            await ctx.send(f"Term '{term}' not found.\n\n**Available terms:** {available}")

    @commands.command(name="terms", help="List all available trading terms")
    async def terms_command(self, ctx):
        """!terms - List all available trading terms"""
        terms_list = "\n".join([f"- **{term}**" for term in TRADING_TERMS.keys()])
        embed = discord.Embed(
            title="Trading Terms",
            description=f"Use `!define <term>` to learn more:\n\n{terms_list}",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(name="tip", help="Get a random trading tip")
    async def tip_command(self, ctx):
        """!tip - Get a random trading tip"""
        tip = random.choice(TRADING_TIPS)
        embed = discord.Embed(title="Trading Tip", description=tip, color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name="postterm", help="Post a term to the glossary channel. Usage: !postterm support")
    async def post_term_command(self, ctx, term: str = None):
        """!postterm <term> - Post a term to the glossary channel"""
        if not term:
            await ctx.send("Usage: `!postterm <term>`")
            return

        term_lower = term.lower().strip()

        if term_lower not in TRADING_TERMS:
            available = ", ".join(TRADING_TERMS.keys())
            await ctx.send(f"Term '{term}' not found.\n\n**Available terms:** {available}")
            return

        info = TRADING_TERMS[term_lower]
        embed = discord.Embed(title=info['title'], color=discord.Color.blue())
        embed.add_field(name="Definition", value=info['definition'], inline=False)
        embed.add_field(name="Example", value=info['example'], inline=False)
        embed.set_footer(text=f"Posted by {ctx.author.name}")

        channel = self.bot.get_channel(TRADING_GLOSSARY_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await ctx.send(f"Posted '{term}' to glossary channel!")
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EducationCog(bot))
