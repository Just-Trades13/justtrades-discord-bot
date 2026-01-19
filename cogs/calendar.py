"""
Calendar Cog - Economic calendar and events
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import json
import os

ECONOMIC_CALENDAR_CHANNEL = int(os.environ.get('CHANNEL_ECONOMIC_CALENDAR', '1359875411470716959'))

# Default economic events
DEFAULT_EVENTS = [
    {"date": "2026-01-21", "time": "08:30", "event": "Existing Home Sales", "impact": "MEDIUM", "forecast": "TBD"},
    {"date": "2026-01-23", "time": "10:00", "event": "Michigan Consumer Sentiment", "impact": "MEDIUM", "forecast": "TBD"},
    {"date": "2026-01-29", "time": "14:00", "event": "FOMC Interest Rate Decision", "impact": "HIGH", "forecast": "TBD"},
    {"date": "2026-01-29", "time": "14:30", "event": "Fed Chair Press Conference", "impact": "HIGH", "forecast": "N/A"},
    {"date": "2026-01-30", "time": "08:30", "event": "GDP (Q4 Advance)", "impact": "HIGH", "forecast": "TBD"},
    {"date": "2026-01-31", "time": "08:30", "event": "Core PCE Price Index", "impact": "HIGH", "forecast": "TBD"},
    {"date": "2026-02-07", "time": "08:30", "event": "Non-Farm Payrolls (NFP)", "impact": "HIGH", "forecast": "TBD"},
    {"date": "2026-02-12", "time": "08:30", "event": "CPI (Consumer Price Index)", "impact": "HIGH", "forecast": "TBD"},
]

class CalendarCog(commands.Cog, name="Calendar"):
    def __init__(self, bot):
        self.bot = bot
        self.ct = pytz.timezone('America/Chicago')
        self.events = DEFAULT_EVENTS.copy()

    @app_commands.command(name="calendar", description="Show upcoming economic events")
    @app_commands.describe(days="Number of days to look ahead (default: 7)")
    async def calendar_command(self, interaction: discord.Interaction, days: int = 7):
        now = datetime.now(self.ct)
        cutoff = now + timedelta(days=days)

        upcoming = []
        for event in self.events:
            try:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                event_date = self.ct.localize(event_date)
                if now.date() <= event_date.date() <= cutoff.date():
                    upcoming.append(event)
            except:
                continue

        if not upcoming:
            await interaction.response.send_message(f"No economic events in the next {days} days.")
            return

        embed = discord.Embed(
            title=f"Economic Calendar - Next {days} Days",
            color=discord.Color.blue(),
            timestamp=now
        )

        for event in sorted(upcoming, key=lambda x: x['date']):
            impact_emoji = "HIGH" if event.get('impact') == "HIGH" else "MED" if event.get('impact') == "MEDIUM" else "LOW"
            embed.add_field(
                name=f"[{impact_emoji}] {event['event']}",
                value=f"{event['date']} at {event.get('time', 'TBD')} CT\nForecast: {event.get('forecast', 'N/A')}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="event-add", description="Add an economic event to the calendar")
    @app_commands.describe(
        date="Date (YYYY-MM-DD)",
        time="Time in CT (HH:MM)",
        event_name="Event name",
        impact="Impact level (HIGH, MEDIUM, LOW)",
        forecast="Forecast value (optional)"
    )
    async def event_add_command(
        self,
        interaction: discord.Interaction,
        date: str,
        time: str,
        event_name: str,
        impact: str = "HIGH",
        forecast: str = "N/A"
    ):
        new_event = {
            "date": date,
            "time": time,
            "event": event_name,
            "impact": impact.upper(),
            "forecast": forecast
        }
        self.events.append(new_event)

        await interaction.response.send_message(f"Added: **{event_name}** on {date} at {time} CT")

    @app_commands.command(name="post-calendar", description="Post the weekly calendar to the economic-calendar channel")
    async def post_calendar_command(self, interaction: discord.Interaction):
        now = datetime.now(self.ct)
        cutoff = now + timedelta(days=7)

        upcoming = []
        for event in self.events:
            try:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                event_date = self.ct.localize(event_date)
                if now.date() <= event_date.date() <= cutoff.date():
                    upcoming.append(event)
            except:
                continue

        embed = discord.Embed(
            title="Weekly Economic Calendar",
            description=f"Week of {now.strftime('%B %d, %Y')}",
            color=discord.Color.gold(),
            timestamp=now
        )

        if upcoming:
            for event in sorted(upcoming, key=lambda x: x['date']):
                impact_emoji = "HIGH" if event.get('impact') == "HIGH" else "MED" if event.get('impact') == "MEDIUM" else "LOW"
                embed.add_field(
                    name=f"[{impact_emoji}] {event['event']}",
                    value=f"{event['date']} at {event.get('time', 'TBD')} CT\nForecast: {event.get('forecast', 'N/A')}",
                    inline=False
                )
        else:
            embed.description += "\n\n*No major economic events this week.*"

        embed.set_footer(text="Trade carefully around high-impact events!")

        channel = self.bot.get_channel(ECONOMIC_CALENDAR_CHANNEL)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("Calendar posted!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CalendarCog(bot))
