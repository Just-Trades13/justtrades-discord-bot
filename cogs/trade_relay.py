"""
Trade Relay Cog - Trade alerts and signals
"""
import discord
from discord.ext import commands
from datetime import datetime
import pytz
import os

TRADE_ALERTS_CHANNEL = int(os.environ.get('CHANNEL_TRADE_ALERTS', '1358534900780630067'))

class TradeRelayCog(commands.Cog, name="Trade Relay"):
    def __init__(self, bot):
        self.bot = bot
        self.ct = pytz.timezone('America/Chicago')

    @commands.command(name="alert", help="Post a trade alert. Usage: !alert NQ BUY 21500 21480 21560 [notes]")
    async def alert_command(self, ctx, symbol: str = None, action: str = None, price: float = None, stop: float = None, target: float = None, *, notes: str = ""):
        """!alert <symbol> <BUY/SELL> <entry> <stop> <target> [notes]"""
        if not all([symbol, action, price, stop, target]):
            await ctx.send("Usage: `!alert <symbol> <BUY/SELL> <entry> <stop> <target> [notes]`\nExample: `!alert NQ BUY 21500 21480 21560 Breaking resistance`")
            return

        now = datetime.now(self.ct)

        # Calculate R:R
        risk = abs(price - stop)
        reward = abs(target - price)
        rr_ratio = reward / risk if risk > 0 else 0

        if action.upper() == "BUY":
            color = discord.Color.green()
            action_text = "LONG"
        else:
            color = discord.Color.red()
            action_text = "SHORT"

        embed = discord.Embed(
            title=f"TRADE ALERT: {symbol.upper()}",
            color=color,
            timestamp=now
        )
        embed.add_field(name="Action", value=f"**{action_text}**", inline=True)
        embed.add_field(name="Entry", value=f"**{price:,.2f}**", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="Stop Loss", value=f"**{stop:,.2f}**", inline=True)
        embed.add_field(name="Target", value=f"**{target:,.2f}**", inline=True)
        embed.add_field(name="R:R", value=f"**1:{rr_ratio:.1f}**", inline=True)

        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)

        embed.set_footer(text=f"Alert by {ctx.author.name} | {now.strftime('%I:%M %p CT')}")

        channel = self.bot.get_channel(TRADE_ALERTS_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await ctx.send("Trade alert posted to #trade-alerts!")
        else:
            await ctx.send(embed=embed)

    @commands.command(name="close", help="Post trade result. Usage: !close NQ WIN 45 [notes]")
    async def close_command(self, ctx, symbol: str = None, result: str = None, pnl: float = None, *, notes: str = ""):
        """!close <symbol> <WIN/LOSS> <pnl> [notes]"""
        if not all([symbol, result, pnl is not None]):
            await ctx.send("Usage: `!close <symbol> <WIN/LOSS> <pnl> [notes]`\nExample: `!close NQ WIN 45 Hit target perfectly`")
            return

        now = datetime.now(self.ct)

        if result.upper() == "WIN":
            color = discord.Color.green()
            result_text = "WINNER"
        else:
            color = discord.Color.red()
            result_text = "LOSS"

        sign = "+" if pnl >= 0 else ""

        embed = discord.Embed(
            title=f"{symbol.upper()} - {result_text}",
            description=f"**{sign}{pnl:,.2f} points**",
            color=color,
            timestamp=now
        )

        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)

        embed.set_footer(text=f"Closed by {ctx.author.name}")

        channel = self.bot.get_channel(TRADE_ALERTS_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await ctx.send("Trade close posted to #trade-alerts!")
        else:
            await ctx.send(embed=embed)

    @commands.command(name="update", help="Post trade update. Usage: !update NQ Stop moved to breakeven")
    async def update_command(self, ctx, symbol: str = None, *, update_text: str = None):
        """!update <symbol> <update text>"""
        if not symbol or not update_text:
            await ctx.send("Usage: `!update <symbol> <update text>`\nExample: `!update NQ Stop moved to breakeven`")
            return

        now = datetime.now(self.ct)

        embed = discord.Embed(
            title=f"{symbol.upper()} Update",
            description=f"**{update_text}**",
            color=discord.Color.blue(),
            timestamp=now
        )

        embed.set_footer(text=f"Update by {ctx.author.name}")

        channel = self.bot.get_channel(TRADE_ALERTS_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await ctx.send("Update posted to #trade-alerts!")
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TradeRelayCog(bot))
