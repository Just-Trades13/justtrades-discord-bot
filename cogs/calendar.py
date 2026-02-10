"""
Calendar Cog - Forex Factory Economic Calendar Screenshots
Uses Playwright to capture USD-only economic calendar from forexfactory.com
Uses ! prefix commands (NOT slash commands)
"""
import discord
from discord.ext import commands, tasks
from datetime import datetime, time
from zoneinfo import ZoneInfo
import asyncio
import os

ECONOMIC_CALENDAR_CHANNEL = int(os.environ.get('CHANNEL_ECONOMIC_CALENDAR', '1359875411470716959'))
FOREX_FACTORY_URL = "https://www.forexfactory.com/calendar"
SCREENSHOT_PATH = "/tmp/calendar_screenshot.png"


async def capture_forex_factory_screenshot():
    """Capture screenshot of Forex Factory calendar filtered to USD only"""
    from playwright.async_api import async_playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1400, 'height': 1200},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            try:
                await page.goto(FOREX_FACTORY_URL, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(5)

                # Click the Filter button
                await page.click('span:has-text("Filter")')
                await asyncio.sleep(2)

                # Uncheck all non-USD currencies (1-8), keep USD (9) checked
                non_usd_ids = [
                    'currency_1_1',  # AUD
                    'currency_2_1',  # CAD
                    'currency_3_1',  # CHF
                    'currency_4_1',  # CNY
                    'currency_5_1',  # EUR
                    'currency_6_1',  # GBP
                    'currency_7_1',  # JPY
                    'currency_8_1',  # NZD
                ]

                for currency_id in non_usd_ids:
                    try:
                        checkbox = await page.query_selector(f'#{currency_id}')
                        if checkbox:
                            is_checked = await checkbox.is_checked()
                            if is_checked:
                                await checkbox.click()
                                await asyncio.sleep(0.2)
                    except Exception:
                        pass

                # Make sure USD (currency_9_1) is checked
                try:
                    usd_checkbox = await page.query_selector('#currency_9_1')
                    if usd_checkbox:
                        is_checked = await usd_checkbox.is_checked()
                        if not is_checked:
                            await usd_checkbox.click()
                            await asyncio.sleep(0.2)
                except Exception:
                    pass

                await asyncio.sleep(1)

                # Click Apply Filter
                await page.click('input[value="Apply Filter"]')
                await asyncio.sleep(3)

                # Count USD events
                usd_count = await page.evaluate('''
                    () => {
                        const cells = document.querySelectorAll("td.calendar__currency");
                        let count = 0;
                        cells.forEach(cell => {
                            if (cell.innerText.trim() === "USD") count++;
                        });
                        return count;
                    }
                ''')

                await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
                await browser.close()
                return True, usd_count

            except Exception as e:
                print(f"Error capturing screenshot: {e}")
                await browser.close()
                return False, 0
    except Exception as e:
        print(f"Playwright error: {e}")
        return False, 0


async def post_calendar_to_channel(channel):
    """Post the Forex Factory calendar screenshot to the specified channel"""
    ct = ZoneInfo('America/Chicago')
    now = datetime.now(ct)

    success, usd_count = await capture_forex_factory_screenshot()

    if not success or not os.path.exists(SCREENSHOT_PATH):
        return False, "Failed to capture calendar screenshot"

    file_size = os.path.getsize(SCREENSHOT_PATH)
    size_str = f"{file_size / (1024*1024):.1f}MB" if file_size > 1024*1024 else f"{file_size / 1024:.1f}KB"

    embed = discord.Embed(
        title="\U0001f1fa\U0001f1f8 FOREX FACTORY - USA ECONOMIC CALENDAR",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Source",
        value="USA-only economic events (step-by-step filtering)",
        inline=False
    )
    embed.add_field(
        name="URL",
        value=f"[{FOREX_FACTORY_URL}]({FOREX_FACTORY_URL})",
        inline=False
    )
    embed.add_field(name="Size", value=size_str, inline=True)
    embed.add_field(
        name="Time",
        value=now.strftime("%m/%d/%Y, %I:%M:%S %p CT"),
        inline=True
    )
    embed.add_field(
        name="Status",
        value=f"USD-only filtering - {usd_count} USD events",
        inline=False
    )

    file = discord.File(SCREENSHOT_PATH, filename="calendar.png")
    embed.set_image(url="attachment://calendar.png")

    await channel.send(embed=embed, file=file)
    return True, "Calendar posted successfully"


class CalendarCog(commands.Cog, name="Calendar"):
    def __init__(self, bot):
        self.bot = bot
        self.daily_calendar_post.start()

    def cog_unload(self):
        self.daily_calendar_post.cancel()

    @tasks.loop(time=time(hour=6, minute=0, tzinfo=ZoneInfo('America/Chicago')))
    async def daily_calendar_post(self):
        """Auto-post calendar at 6:00 AM CT on weekdays"""
        ct = ZoneInfo('America/Chicago')
        now = datetime.now(ct)
        # Skip weekends
        if now.weekday() >= 5:
            return

        channel = self.bot.get_channel(ECONOMIC_CALENDAR_CHANNEL)
        if not channel:
            print(f"Calendar channel {ECONOMIC_CALENDAR_CHANNEL} not found")
            return

        print(f"Auto-posting Forex Factory calendar at {now}")
        success, message = await post_calendar_to_channel(channel)
        if success:
            print(f"Daily calendar posted successfully")
        else:
            print(f"Daily calendar post failed: {message}")

    @daily_calendar_post.before_loop
    async def before_daily_post(self):
        await self.bot.wait_until_ready()

    @commands.command(name="calendar", help="Post Forex Factory economic calendar")
    async def calendar_command(self, ctx):
        """!calendar - Post Forex Factory USD economic calendar screenshot"""
        await ctx.send("Capturing Forex Factory calendar... (this may take a moment)")

        channel = self.bot.get_channel(ECONOMIC_CALENDAR_CHANNEL)
        if not channel:
            channel = ctx.channel

        success, message = await post_calendar_to_channel(channel)

        if success:
            if channel.id != ctx.channel.id:
                await ctx.send(f"Calendar posted to <#{ECONOMIC_CALENDAR_CHANNEL}>!")
        else:
            await ctx.send(f"Failed: {message}")

    @commands.command(name="calendarhere", help="Post calendar in current channel")
    async def calendar_here_command(self, ctx):
        """!calendarhere - Post calendar screenshot in current channel"""
        await ctx.send("Capturing Forex Factory calendar... (this may take a moment)")

        success, message = await post_calendar_to_channel(ctx.channel)
        if not success:
            await ctx.send(f"Failed: {message}")


async def setup(bot):
    await bot.add_cog(CalendarCog(bot))
