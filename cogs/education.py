"""
Education Cog - Trading terms, tips, and daily educational content
Posts daily educational videos/lessons to help new traders
Uses ! prefix commands (NOT slash commands)
"""
import discord
from discord.ext import commands, tasks
from datetime import datetime, time
from zoneinfo import ZoneInfo
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

# Daily educational lessons - cycles monthly (30 lessons)
DAILY_LESSONS = [
    {
        "title": "What Are Futures Contracts?",
        "description": "Futures are standardized contracts to buy or sell an asset at a predetermined price on a specific future date. Unlike stocks, futures use leverage - meaning you control a large position with a small amount of capital (margin). ES (S&P 500 futures) and NQ (Nasdaq futures) are the most popular for day traders.",
        "key_takeaway": "Futures let you trade both directions (long AND short) with leverage, but that leverage amplifies both gains and losses.",
        "search_query": "futures+trading+for+beginners+explained",
        "topic": "Futures Basics"
    },
    {
        "title": "Understanding Candlestick Charts",
        "description": "Each candlestick shows 4 prices: Open, High, Low, Close (OHLC). Green/white candles mean price closed higher than it opened (bullish). Red/black candles mean price closed lower (bearish). The body shows the range between open and close. The wicks (shadows) show the high and low extremes.",
        "key_takeaway": "Learn to read candlesticks before any indicator - they are the foundation of all chart analysis.",
        "search_query": "how+to+read+candlestick+charts+beginners",
        "topic": "Chart Reading"
    },
    {
        "title": "Support and Resistance Levels",
        "description": "Support is a price level where buyers step in (price bounces up). Resistance is where sellers step in (price bounces down). These levels form because traders remember where price reversed before. The more times a level is tested, the stronger it becomes - but when it finally breaks, the move is often significant.",
        "key_takeaway": "Draw support/resistance as zones (not exact lines) and watch for price reaction at these levels before entering trades.",
        "search_query": "support+and+resistance+trading+tutorial",
        "topic": "Technical Analysis"
    },
    {
        "title": "The 1% Risk Rule",
        "description": "Never risk more than 1% of your total account on a single trade. If you have a $10,000 account, your maximum loss per trade should be $100. Calculate position size using: Position Size = (Account Risk $) / (Stop Loss Distance in Points x Point Value). This ensures no single trade can blow up your account.",
        "key_takeaway": "Position sizing based on the 1% rule is the single most important skill for long-term survival as a trader.",
        "search_query": "1+percent+risk+rule+trading+position+sizing",
        "topic": "Risk Management"
    },
    {
        "title": "Risk-to-Reward Ratio Explained",
        "description": "Risk-to-reward (R:R) compares your potential loss to your potential gain. A 1:3 R:R means you risk $1 to potentially make $3. With a 1:3 ratio, you only need to win 25% of your trades to break even. Professional traders typically aim for a minimum of 1:2 R:R on every trade.",
        "key_takeaway": "Always calculate your R:R before entering a trade. If it's less than 1:2, the trade probably isn't worth taking.",
        "search_query": "risk+reward+ratio+trading+explained",
        "topic": "Risk Management"
    },
    {
        "title": "Market Order vs Limit Order vs Stop Order",
        "description": "**Market Order**: Executes immediately at the current price. Fast but you might get slippage. **Limit Order**: Only executes at your specified price or better. You control the price but might miss the trade. **Stop Order**: Triggers a market order when price reaches your stop level. Used for stop losses and breakout entries.",
        "key_takeaway": "Use limit orders for entries (control your price) and stop orders for protecting your capital (stop losses).",
        "search_query": "market+limit+stop+order+types+explained+trading",
        "topic": "Order Types"
    },
    {
        "title": "Trend Identification: Higher Highs & Higher Lows",
        "description": "An uptrend is defined by a series of higher highs (HH) and higher lows (HL). A downtrend is defined by lower highs (LH) and lower lows (LL). When this pattern breaks - like a lower low in an uptrend - it signals a potential trend change. Always trade in the direction of the trend on your trading timeframe.",
        "key_takeaway": "Before entering any trade, identify the trend. The trend is your friend until it ends.",
        "search_query": "higher+highs+higher+lows+trend+trading",
        "topic": "Technical Analysis"
    },
    {
        "title": "Moving Averages: EMA vs SMA",
        "description": "Moving averages smooth out price action to show the trend direction. **SMA (Simple)** gives equal weight to all periods. **EMA (Exponential)** gives more weight to recent prices, reacting faster to changes. Common settings: 9 EMA (fast/scalping), 20 EMA (short-term trend), 50 SMA (medium trend), 200 SMA (long-term trend).",
        "key_takeaway": "Price above the 200 SMA = bullish bias. Price below = bearish. Use the 9/20 EMA for entries in the trend direction.",
        "search_query": "moving+averages+EMA+SMA+trading+strategy",
        "topic": "Indicators"
    },
    {
        "title": "Volume: The Confirmation Tool",
        "description": "Volume measures how many contracts/shares traded in a period. High volume on a breakout confirms the move is real. Low volume on a breakout suggests it might fail (fake breakout). Volume should increase in the direction of the trend and decrease during pullbacks. Volume precedes price - watch for volume spikes.",
        "key_takeaway": "Never trust a breakout without volume confirmation. Volume is the fuel that drives price moves.",
        "search_query": "volume+analysis+trading+beginners+tutorial",
        "topic": "Volume Analysis"
    },
    {
        "title": "Trading Psychology: Emotional Control",
        "description": "Fear and greed are the two emotions that destroy traders. Fear causes you to exit winners too early and avoid valid setups. Greed causes you to hold losers too long and overtrade. The solution: follow your trading plan mechanically. Pre-define your entry, stop loss, and take profit BEFORE the trade. Then execute without emotion.",
        "key_takeaway": "The market doesn't care about your feelings. Create rules and follow them - that's how professionals operate.",
        "search_query": "trading+psychology+emotional+control+discipline",
        "topic": "Trading Psychology"
    },
    {
        "title": "Candlestick Patterns: Engulfing & Hammer",
        "description": "**Bullish Engulfing**: A large green candle completely covers the previous red candle. Signals buyers overwhelmed sellers. **Bearish Engulfing**: The opposite. **Hammer**: Small body at the top with a long lower wick. Shows sellers pushed price down but buyers fought back. Both are reversal signals at support/resistance levels.",
        "key_takeaway": "Candlestick patterns work best at key levels (support/resistance). A hammer at support = strong buy signal.",
        "search_query": "engulfing+hammer+candlestick+patterns+trading",
        "topic": "Candlestick Patterns"
    },
    {
        "title": "Chart Patterns: Head & Shoulders",
        "description": "Head and Shoulders is a reversal pattern with three peaks: left shoulder, head (highest), right shoulder. The neckline connects the two troughs. When price breaks below the neckline, it signals a trend reversal. Measure the distance from head to neckline - that's your price target. Inverse H&S is the bullish version.",
        "key_takeaway": "Head & Shoulders is one of the most reliable reversal patterns. Wait for the neckline break before entering.",
        "search_query": "head+and+shoulders+pattern+trading+tutorial",
        "topic": "Chart Patterns"
    },
    {
        "title": "Chart Patterns: Bull & Bear Flags",
        "description": "A flag pattern forms after a sharp move (the flagpole) followed by a tight consolidation (the flag). **Bull Flag**: Sharp move up, then a slight downward channel. Breakout above = continuation higher. **Bear Flag**: Sharp move down, then slight upward channel. Breakout below = continuation lower. These are continuation patterns.",
        "key_takeaway": "Flags are among the best patterns for day traders. The target equals the length of the flagpole from the breakout point.",
        "search_query": "bull+flag+bear+flag+pattern+day+trading",
        "topic": "Chart Patterns"
    },
    {
        "title": "Building a Trading Plan",
        "description": "Every successful trader has a written plan covering: 1) What markets to trade, 2) What setups to look for, 3) Entry rules, 4) Stop loss placement, 5) Take profit targets, 6) Position sizing rules, 7) Maximum daily loss limit, 8) Trading hours. Your plan removes emotions from decisions and gives you a framework to improve.",
        "key_takeaway": "If you don't have a written trading plan, you don't have a trading business - you have a gambling hobby.",
        "search_query": "how+to+create+trading+plan+step+by+step",
        "topic": "Trading Plan"
    },
    {
        "title": "Understanding Margin and Leverage",
        "description": "Margin is the deposit required to open a futures position. For ES futures (worth ~$300,000), day trading margin might be $500-$2,000. That's 150x-600x leverage. Leverage magnifies both profits AND losses. A 1% move in ES = $600 per contract. If you only have $2,000 margin, that's a 30% account swing on one contract.",
        "key_takeaway": "Leverage is a double-edged sword. Use the minimum position size until you're consistently profitable.",
        "search_query": "margin+leverage+futures+trading+explained",
        "topic": "Futures Basics"
    },
    {
        "title": "Pre-Market Routine for Day Traders",
        "description": "Before the market opens: 1) Check overnight price action and gap direction, 2) Review the economic calendar for high-impact events, 3) Identify key support/resistance levels, 4) Note the previous day's high, low, and close, 5) Set alerts at key levels, 6) Review your trading plan and rules. A solid pre-market routine sets you up for success.",
        "key_takeaway": "Spend 30-60 minutes preparing before the open. Most losing traders skip this step.",
        "search_query": "pre+market+routine+day+trading+preparation",
        "topic": "Day Trading"
    },
    {
        "title": "RSI: Relative Strength Index",
        "description": "RSI measures momentum on a scale of 0-100. Above 70 = overbought (price may pull back). Below 30 = oversold (price may bounce). But in strong trends, RSI can stay overbought/oversold for extended periods. The real power of RSI is divergence: when price makes a new high but RSI makes a lower high, the trend may be weakening.",
        "key_takeaway": "Don't blindly short because RSI is overbought. Instead, use RSI divergence at key levels for higher probability trades.",
        "search_query": "RSI+indicator+trading+strategy+divergence",
        "topic": "Indicators"
    },
    {
        "title": "Stop Loss Placement Strategies",
        "description": "Common stop loss methods: 1) **Structure-based**: Place stop below the last swing low (longs) or above swing high (shorts). 2) **ATR-based**: Use 1.5-2x the Average True Range. 3) **Moving average**: Stop below a key MA like the 20 EMA. Never use a fixed dollar amount - your stop should be based on market structure and volatility.",
        "key_takeaway": "Your stop loss defines your risk. Place it where the trade idea is invalidated, not based on what you can afford to lose.",
        "search_query": "where+to+place+stop+loss+trading+strategies",
        "topic": "Risk Management"
    },
    {
        "title": "The Power of Trading Journals",
        "description": "Top traders review every trade. Your journal should include: entry/exit price, position size, setup type, screenshot of the chart, what went right/wrong, emotional state during the trade, and the R-multiple result. After 50+ trades, patterns emerge: which setups work best, what time of day you trade best, and what mistakes you repeat.",
        "key_takeaway": "A trading journal turns your losses into lessons. Without one, you're doomed to repeat the same mistakes.",
        "search_query": "trading+journal+how+to+track+trades+improve",
        "topic": "Trading Improvement"
    },
    {
        "title": "Fibonacci Retracement Levels",
        "description": "Fibonacci levels (23.6%, 38.2%, 50%, 61.8%, 78.6%) show where price is likely to find support/resistance during a pullback. Draw Fib from swing low to swing high (uptrend) or high to low (downtrend). The 61.8% level (the 'golden ratio') is the most watched. Many institutional algorithms are programmed to react at Fib levels.",
        "key_takeaway": "Use Fibonacci with other confluence (support/resistance, moving averages) for the highest probability setups.",
        "search_query": "fibonacci+retracement+trading+tutorial+beginners",
        "topic": "Technical Analysis"
    },
    {
        "title": "Revenge Trading: How to Avoid It",
        "description": "Revenge trading is taking impulsive trades to recover losses. It's driven by emotion, not analysis. Signs: increasing position size after a loss, taking trades outside your plan, feeling angry at the market. Solution: set a max daily loss (e.g., 3% of account). When you hit it, STOP trading. Walk away. The market will be there tomorrow.",
        "key_takeaway": "Have a hard daily loss limit and honor it. No exceptions. The worst trading days come from trying to get even.",
        "search_query": "revenge+trading+how+to+stop+trading+psychology",
        "topic": "Trading Psychology"
    },
    {
        "title": "VWAP: Volume Weighted Average Price",
        "description": "VWAP is the average price weighted by volume throughout the day. It resets daily. Price above VWAP = bullish intraday bias. Price below = bearish. VWAP acts as dynamic support/resistance. Institutional traders use VWAP as a benchmark - they try to buy below VWAP and sell above it. It's one of the most important day trading indicators.",
        "key_takeaway": "Trade with VWAP, not against it. Look for entries at VWAP pullbacks in the direction of the trend.",
        "search_query": "VWAP+trading+strategy+day+trading+explained",
        "topic": "Indicators"
    },
    {
        "title": "Gap Trading Strategies",
        "description": "A gap occurs when price opens significantly higher or lower than the previous close. **Gap Up**: bullish sentiment. **Gap Down**: bearish sentiment. Gap fills happen when price returns to the previous close (~70% of gaps fill within 3 days). Gap and Go: when price gaps up and continues higher, don't fight it - trade with momentum.",
        "key_takeaway": "Don't automatically fade gaps. Wait to see if the gap holds or fills in the first 30 minutes before committing.",
        "search_query": "gap+trading+strategy+stocks+futures+beginners",
        "topic": "Day Trading"
    },
    {
        "title": "The Opening Range: First 15-30 Minutes",
        "description": "The opening range is the high and low of the first 15-30 minutes of trading. This range sets the tone for the day. A breakout above the opening range high is bullish. A breakdown below is bearish. Many professional traders wait for the opening range to form before making their first trade. It filters out the noise of the open.",
        "key_takeaway": "Be patient at the open. Let the opening range form, then trade the breakout or breakdown with the trend.",
        "search_query": "opening+range+breakout+trading+strategy",
        "topic": "Day Trading"
    },
    {
        "title": "Scaling In and Out of Positions",
        "description": "Instead of going all-in at once, you can scale into a position (add contracts as price confirms your idea) and scale out (take partial profits at targets). Example: Enter 3 contracts. Take profit on 1 at target 1, move stop to breakeven, take profit on 1 at target 2, let the last ride. This locks in profit while keeping upside.",
        "key_takeaway": "Scaling out turns your losers into smaller losses and your winners into bigger wins. It's a key edge for professional traders.",
        "search_query": "scaling+in+out+positions+trading+strategy",
        "topic": "Trade Management"
    },
    {
        "title": "Understanding Market Sessions",
        "description": "Each trading session has different characteristics. **Asian session** (6pm-2am ET): Low volatility, range-bound. **London session** (3am-12pm ET): Volatility picks up, trends start. **New York session** (9:30am-4pm ET): Highest volume and volatility, especially the first 2 hours. The best trading opportunities occur during London/NY overlap (8am-12pm ET).",
        "key_takeaway": "Trade during the session that matches your strategy. Scalpers need volatility (NY open). Swing traders can use any session.",
        "search_query": "trading+sessions+best+time+to+trade+futures",
        "topic": "Market Structure"
    },
    {
        "title": "Double Top and Double Bottom Patterns",
        "description": "**Double Top**: Price hits a resistance level twice and fails both times, forming an 'M' shape. Bearish reversal signal. **Double Bottom**: Price hits support twice and bounces both times, forming a 'W' shape. Bullish reversal signal. The pattern is confirmed when price breaks the neckline (the middle point between the two peaks/troughs).",
        "key_takeaway": "Double tops/bottoms are simple but effective. Wait for the neckline break and volume confirmation before entering.",
        "search_query": "double+top+double+bottom+pattern+trading",
        "topic": "Chart Patterns"
    },
    {
        "title": "Paper Trading: Practice Without Risk",
        "description": "Paper trading is simulated trading with virtual money. Every broker offers a paper/demo account. Use it to: test new strategies, learn the platform, build confidence, track performance over 50+ trades before going live. Treat paper trading seriously - follow your rules exactly as if real money were on the line.",
        "key_takeaway": "If you can't be profitable on paper, you won't be profitable with real money. Master the sim before going live.",
        "search_query": "paper+trading+simulator+practice+beginners",
        "topic": "Getting Started"
    },
    {
        "title": "Breakout Trading Strategy",
        "description": "Breakout trading enters when price breaks through a key level (support, resistance, or consolidation pattern). Key rules: 1) Identify a clear level that has been tested multiple times. 2) Wait for a close above/below the level (not just a wick). 3) Confirm with volume spike. 4) Enter on a retest of the broken level for lower risk.",
        "key_takeaway": "The retest entry after a breakout offers the best risk/reward. If price breaks out and retests the level as new support, that's your entry.",
        "search_query": "breakout+trading+strategy+tutorial+beginners",
        "topic": "Trading Strategies"
    },
    {
        "title": "Managing Winning Trades",
        "description": "Most traders focus on entries but winning is about exits. Strategies for managing winners: 1) Trailing stop - move stop up as price moves in your favor. 2) Partial exits at predetermined targets. 3) Time-based exits - close before end of session. 4) Indicator-based - exit when EMA crossover reverses. Don't let a winner turn into a loser.",
        "key_takeaway": "Move your stop to breakeven once price moves 1R in your favor. You can never lose money on a breakeven trade.",
        "search_query": "how+to+manage+winning+trades+trailing+stop",
        "topic": "Trade Management"
    },
]


class EducationCog(commands.Cog, name="Education"):
    def __init__(self, bot):
        self.bot = bot
        self.lesson_index = 0
        self.daily_education_post.start()

    def cog_unload(self):
        self.daily_education_post.cancel()

    @tasks.loop(time=time(hour=7, minute=0, tzinfo=ZoneInfo('America/Chicago')))
    async def daily_education_post(self):
        """Auto-post daily educational content at 7:00 AM CT on weekdays"""
        ct = ZoneInfo('America/Chicago')
        now = datetime.now(ct)
        if now.weekday() >= 5:
            return

        channel = self.bot.get_channel(TRADING_GLOSSARY_CHANNEL)
        if not channel:
            print(f"Education channel {TRADING_GLOSSARY_CHANNEL} not found")
            return

        lesson = DAILY_LESSONS[self.lesson_index % len(DAILY_LESSONS)]
        self.lesson_index += 1

        embed = self._build_lesson_embed(lesson)
        await channel.send(embed=embed)
        print(f"Daily education posted: {lesson['title']}")

    @daily_education_post.before_loop
    async def before_daily_education(self):
        await self.bot.wait_until_ready()

    def _build_lesson_embed(self, lesson):
        yt_url = f"https://www.youtube.com/results?search_query={lesson['search_query']}"

        embed = discord.Embed(
            title=f"Daily Lesson: {lesson['title']}",
            description=lesson['description'],
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Key Takeaway",
            value=lesson['key_takeaway'],
            inline=False
        )
        embed.add_field(
            name="Learn More",
            value=f"[Watch videos on this topic]({yt_url})",
            inline=False
        )
        embed.set_footer(text=f"Topic: {lesson['topic']} | Daily Trading Education")
        return embed

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

    @commands.command(name="lesson", help="Post today's educational lesson")
    async def lesson_command(self, ctx):
        """!lesson - Post the next educational lesson"""
        lesson = DAILY_LESSONS[self.lesson_index % len(DAILY_LESSONS)]
        self.lesson_index += 1
        embed = self._build_lesson_embed(lesson)
        await ctx.send(embed=embed)

    @commands.command(name="lessonlist", help="List all available lesson topics")
    async def lesson_list_command(self, ctx):
        """!lessonlist - List all lesson topics"""
        topics = [f"**{i+1}.** {l['title']} ({l['topic']})" for i, l in enumerate(DAILY_LESSONS)]
        # Split into chunks if too long
        chunk = "\n".join(topics[:15])
        embed = discord.Embed(
            title="Trading Education Lessons (1-15)",
            description=chunk,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        if len(topics) > 15:
            chunk2 = "\n".join(topics[15:])
            embed2 = discord.Embed(
                title=f"Trading Education Lessons (16-{len(topics)})",
                description=chunk2,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed2)

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
