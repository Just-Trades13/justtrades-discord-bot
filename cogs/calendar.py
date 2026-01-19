"""
Calendar Cog - Economic calendar and events
Uses ! prefix commands (NOT slash commands)
"""
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
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
        # Start auto-posting task
        self.weekly_calendar_post.start()

    def cog_unload(self):
        self.weekly_calendar_post.cancel()

    @tasks.loop(time=time(hour=6, minute=0, tzinfo=pytz.timezone('America/Chicago')))
    async def weekly_calendar_post(self):
        """Auto-post weekly calendar at 6:00 AM CT (Mondays only)"""
        now = datetime.now(self.ct)
        # Skip weekends
        if now.weekday() >= 5:
            return
        # Only post on Mondays
        if now.weekday() != 0:
            return

        channel = self.bot.get_channel(ECONOMIC_CALENDAR_CHANNEL)
        if not channel:
            return

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
                embed.add_field(
                    name=f"[{event.get('impact', 'MED')}] {event['event']}",
                    value=f"{event['date']} at {event.get('time', 'TBD')} CT\nForecast: {event.get('forecast', 'N/A')}",
                    inline=False
                )
        else:
            embed.description += "\n\n*No major economic events this week.*"

        embed.set_footer(text="Calendar Cog | Trade carefully around high-impact events!")
        await channel.send(embed=embed)

    @weekly_calendar_post.before_loop
    async def before_weekly_post(self):
        await self.bot.wait_until_ready()

    @commands.command(name="calendar", help="Show upcoming economic events. Usage: !calendar [days]")
    async def calendar_command(self, ctx, days: int = 7):
        """!calendar [days] - Show economic events for next N days"""
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
            await ctx.send(f"No economic events in the next {days} days.")
            return

        embed = discord.Embed(
            title=f"Economic Calendar - Next {days} Days",
            color=discord.Color.blue(),
            timestamp=now
        )

        for event in sorted(upcoming, key=lambda x: x['date']):
            embed.add_field(
                name=f"[{event.get('impact', 'MED')}] {event['event']}",
                value=f"{event['date']} at {event.get('time', 'TBD')} CT\nForecast: {event.get('forecast', 'N/A')}",
                inline=False
            )

        embed.set_footer(text="Calendar Cog")
        await ctx.send(embed=embed)

    @commands.command(name="eventadd", help="Add economic event. Usage: !eventadd 2026-01-30 08:30 GDP HIGH 2.5%")
    async def event_add_command(self, ctx, date: str = None, event_time: str = None, *, rest: str = None):
        """!eventadd <date> <time> <event_name> [impact] [forecast]"""
        if not all([date, event_time, rest]):
            await ctx.send("**Usage:** `!eventadd <YYYY-MM-DD> <HH:MM> <event_name> [HIGH/MEDIUM/LOW] [forecast]`\n"
                          "**Example:** `!eventadd 2026-01-30 08:30 GDP Report HIGH 2.5%`")
            return

        parts = rest.split()
        impact = "HIGH"
        forecast = "N/A"
        event_name_parts = parts

        if len(parts) >= 2:
            if parts[-2].upper() in ["HIGH", "MEDIUM", "LOW"]:
                impact = parts[-2].upper()
                forecast = parts[-1]
                event_name_parts = parts[:-2]
            elif parts[-1].upper() in ["HIGH", "MEDIUM", "LOW"]:
                impact = parts[-1].upper()
                event_name_parts = parts[:-1]

        event_name = " ".join(event_name_parts)

        new_event = {
            "date": date,
            "time": event_time,
            "event": event_name,
            "impact": impact,
            "forecast": forecast
        }
        self.events.append(new_event)

        await ctx.send(f"Added: **{event_name}** on {date} at {event_time} CT (Impact: {impact})")

    @commands.command(name="eventremove", help="Remove an event by name. Usage: !eventremove GDP")
    async def event_remove_command(self, ctx, *, event_name: str = None):
        """!eventremove <event_name> - Remove an event"""
        if not event_name:
            await ctx.send("**Usage:** `!eventremove <event_name>`")
            return

        original_count = len(self.events)
        self.events = [e for e in self.events if event_name.lower() not in e['event'].lower()]
        removed_count = original_count - len(self.events)

        if removed_count > 0:
            await ctx.send(f"Removed {removed_count} event(s) matching '{event_name}'")
        else:
            await ctx.send(f"No events found matching '{event_name}'")

    @commands.command(name="postcalendar", help="Post weekly calendar to #economic-calendar")
    async def post_calendar_command(self, ctx):
        """!postcalendar - Post weekly calendar to the economic calendar channel"""
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
                embed.add_field(
                    name=f"[{event.get('impact', 'MED')}] {event['event']}",
                    value=f"{event['date']} at {event.get('time', 'TBD')} CT\nForecast: {event.get('forecast', 'N/A')}",
                    inline=False
                )
        else:
            embed.description += "\n\n*No major economic events this week.*"

        embed.set_footer(text="Trade carefully around high-impact events!")

        channel = self.bot.get_channel(ECONOMIC_CALENDAR_CHANNEL)
        if channel and channel.id != ctx.channel.id:
            await channel.send(embed=embed)
            await ctx.send(f"Calendar posted to <#{ECONOMIC_CALENDAR_CHANNEL}>!")
        else:
            await ctx.send(embed=embed)

    @commands.command(name="eventlist", help="List all stored events")
    async def event_list_command(self, ctx):
        """!eventlist - List all events"""
        if not self.events:
            await ctx.send("No events stored.")
            return

        embed = discord.Embed(title="All Economic Events", color=discord.Color.blue())

        for event in sorted(self.events, key=lambda x: x['date'])[:25]:
            embed.add_field(
                name=f"[{event.get('impact', 'MED')}] {event['event']}",
                value=f"{event['date']} at {event.get('time', 'TBD')} CT",
                inline=True
            )

        if len(self.events) > 25:
            embed.set_footer(text=f"Showing 25 of {len(self.events)} events")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CalendarCog(bot))
