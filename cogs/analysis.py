"""
Analysis Cog - Chart setups and technical analysis
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import pytz
import os

CHART_SETUPS_CHANNEL = int(os.environ.get('CHANNEL_CHART_SETUPS', '1367383497689268286'))

class AnalysisCog(commands.Cog, name="Analysis"):
    def __init__(self, bot):
        self.bot = bot
        self.ct = pytz.timezone('America/Chicago')

    @app_commands.command(name="setup", description="Post a chart setup to the chart-setups channel")
    @app_commands.describe(
        symbol="Trading symbol (e.g., NQ, ES, AAPL)",
        direction="Long or Short",
        entry="Entry price",
        stop="Stop loss price",
        target="Target price",
        notes="Additional notes about the setup"
    )
    async def setup_command(
        self,
        interaction: discord.Interaction,
        symbol: str,
        direction: str,
        entry: float,
        stop: float,
        target: float,
        notes: str = ""
    ):
        now = datetime.now(self.ct)

        # Calculate R:R
        risk = abs(entry - stop)
        reward = abs(target - entry)
        rr_ratio = reward / risk if risk > 0 else 0

        if direction.lower() == "long":
            color = discord.Color.green()
            dir_text = "LONG"
        else:
            color = discord.Color.red()
            dir_text = "SHORT"

        embed = discord.Embed(
            title=f"{symbol.upper()} - {dir_text}",
            color=color,
            timestamp=now
        )
        embed.add_field(name="Entry", value=f"**{entry:,.2f}**", inline=True)
        embed.add_field(name="Stop Loss", value=f"**{stop:,.2f}**", inline=True)
        embed.add_field(name="Target", value=f"**{target:,.2f}**", inline=True)
        embed.add_field(name="Risk", value=f"{risk:,.2f} pts", inline=True)
        embed.add_field(name="Reward", value=f"{reward:,.2f} pts", inline=True)
        embed.add_field(name="R:R", value=f"1:{rr_ratio:.1f}", inline=True)

        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)

        embed.set_footer(text=f"Posted by {interaction.user.name}")

        channel = self.bot.get_channel(CHART_SETUPS_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("Chart setup posted!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="levels", description="Post key support/resistance levels")
    @app_commands.describe(
        symbol="Trading symbol",
        support1="First support level",
        resistance1="First resistance level",
        support2="Second support level (optional)",
        resistance2="Second resistance level (optional)",
        notes="Additional notes"
    )
    async def levels_command(
        self,
        interaction: discord.Interaction,
        symbol: str,
        support1: float,
        resistance1: float,
        support2: float = None,
        resistance2: float = None,
        notes: str = ""
    ):
        now = datetime.now(self.ct)

        embed = discord.Embed(
            title=f"{symbol.upper()} Key Levels",
            color=discord.Color.blue(),
            timestamp=now
        )

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

        embed.set_footer(text=f"Posted by {interaction.user.name}")

        channel = self.bot.get_channel(CHART_SETUPS_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("Levels posted!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AnalysisCog(bot))
