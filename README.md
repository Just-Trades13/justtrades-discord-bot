# JustTrades Discord Bot

Combined Discord bot for the JustTrades trading community. Runs on Railway for 24/7 uptime.

## Features

- **Market Data** - Live futures prices, any symbol lookup, daily bias posting
- **Education** - Trading term definitions, tips, glossary
- **Analysis** - Chart setups with R:R calculations, support/resistance levels
- **Trade Relay** - Trade alerts, results, and updates
- **Calendar** - Economic calendar and event tracking

## Commands

### Prefix Commands (!)
| Command | Description |
|---------|-------------|
| `!market` | Live futures prices (NQ, ES, YM, etc.) |
| `!price <symbol>` | Price for any symbol |
| `!bias <direction> <notes>` | Post daily bias |
| `!define <term>` | Trading term definition |
| `!terms` | List all trading terms |
| `!tip` | Random trading tip |
| `!alert <symbol> <BUY/SELL> <entry> <stop> <target>` | Trade alert |
| `!close <symbol> <WIN/LOSS> <pnl>` | Trade result |
| `!update <symbol> <text>` | Trade update |
| `!bothelp` | Show all commands |
| `!status` | Bot status |

### Slash Commands (/)
| Command | Description |
|---------|-------------|
| `/setup` | Post chart setup |
| `/levels` | Post S/R levels |
| `/calendar` | Economic calendar |
| `/event-add` | Add calendar event |
| `/post-calendar` | Post weekly calendar |

## Environment Variables

Set these in Railway:

| Variable | Description |
|----------|-------------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token (required) |
| `CHANNEL_DAILY_BIAS` | Daily bias channel ID |
| `CHANNEL_CHART_SETUPS` | Chart setups channel ID |
| `CHANNEL_TRADING_GLOSSARY` | Glossary channel ID |
| `CHANNEL_ECONOMIC_CALENDAR` | Calendar channel ID |
| `CHANNEL_TRADE_ALERTS` | Trade alerts channel ID |

## Deployment

1. Push to GitHub
2. Connect repo to Railway
3. Set environment variables
4. Deploy!

---
*JustTrades Bot - Railway Deployment*
