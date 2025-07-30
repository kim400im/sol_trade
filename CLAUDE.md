# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cryptocurrency trading bot that uses GPT-4 for trading decisions on Bitget futures. The bot analyzes multiple timeframe charts and makes BUY/SELL decisions based on consensus across different granularities (1m, 3m, 5m candles).

## Core Architecture

### Main Components
- **trade_loop.py**: Main execution loop that monitors positions, gets chart data, queries GPT, and executes trades
- **bitget_api.py**: All Bitget API interactions (chart data, positions, orders, balance)
- **gpt_interface.py**: OpenAI GPT-4 integration for trading decisions
- **trade_logic.py**: Trade execution logic (currently minimal, just calls bitget_api)
- **logger.py**: Excel-based trade logging with pandas
- **utils.py**: Utility functions (IP, time, Windows audio beeps)

### Key Flow
1. Main loop checks for active positions every 30 seconds
2. If position exists: monitors for TP/SL conditions
3. If no position: gets chart data for multiple timeframes
4. Queries GPT-4 for each timeframe (buy/sell decision)
5. Only trades if ALL timeframes agree (consensus required)
6. Sets fixed TP/SL deltas of $200
7. Logs all trades to Excel with unique IDs

## Development Commands

### Setup and Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run the trading bot
python trade_loop.py
```

### Environment Variables Required
Create a `.env` file with:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4 calls
- `BG_ACCESS_KEY`, `BG_SECRET_KEY`, `BG_PASSPHARASE`: Bitget API credentials
- `ORDER_AMOUNT_USD`: Trading amount in USD (currently hardcoded to 50000 in trade_loop.py)

### Configuration
Key parameters in `trade_loop.py`:
- `granularities = ["3m", "5m", "1m"]`: Timeframes for analysis
- `candlenum = 100`: Number of candles to analyze
- `price_change_threshold = 100`: Minimum price change to trigger analysis
- `TP_DELTA = SL_DELTA = 200`: Take profit and stop loss distances

## Code Patterns

### API Authentication
Bitget API uses HMAC-SHA256 signatures with timestamp, method, path, and body. All API functions follow this pattern with proper headers.

### Error Handling
The main loop has try/catch with 10-second sleep on errors. Individual functions print errors but don't halt execution.

### Logging
Uses pandas DataFrame with Excel output. Each trade gets a UUID and tracks entry/exit with timestamps, prices, and reasons.

### GPT Integration
Sends compressed OHLCV data as text, requires single-word "buy" or "sell" response. Includes risk management context (delta threshold).

## Important Notes

- **Cross-platform**: Audio notifications removed for Linux compatibility
- **Production system**: Trades real money on Bitget futures
- **Fixed risk**: $5 TP/SL deltas for Solana trading
- **Consensus required**: All timeframes must agree for trade execution
- **No manual testing**: No test framework - runs live trades only