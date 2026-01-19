#!/bin/bash
# JustTrades Discord Bot - Railway Deploy Script

echo "==================================="
echo "JustTrades Discord Bot Deployment"
echo "==================================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo ""
echo "Step 1: Logging into Railway..."
railway login

# Create new project or link to existing
echo ""
echo "Step 2: Creating Discord Bot service..."
railway init --name justtrades-discord-bot

# Set environment variables
echo ""
echo "Step 3: Setting environment variables..."
echo "Enter your Discord Bot Token (from Discord Developer Portal):"
read -s DISCORD_TOKEN

railway variables set DISCORD_BOT_TOKEN="$DISCORD_TOKEN"
railway variables set CHANNEL_DAILY_BIAS="1358534746879037642"
railway variables set CHANNEL_NEWS_HEADLINES="1420078847629590608"
railway variables set CHANNEL_BREAKING_NEWS="1347337500380893296"
railway variables set CHANNEL_LIVE_TRADES="1347337979751829659"
railway variables set CHANNEL_TRADE_SETUPS="1347337927637602365"
railway variables set CHANNEL_CHART_SETUPS="1367383497689268286"
railway variables set CHANNEL_TRADING_GLOSSARY="1358534448332935420"
railway variables set CHANNEL_ECONOMIC_CALENDAR="1359875411470716959"
railway variables set CHANNEL_TRADE_ALERTS="1358534900780630067"

# Deploy
echo ""
echo "Step 4: Deploying to Railway..."
railway up --detach

echo ""
echo "==================================="
echo "Deployment complete!"
echo "Check status: railway status"
echo "View logs: railway logs"
echo "==================================="
