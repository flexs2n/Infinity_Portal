# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

infinity_portal is an autonomous hedge fund trading system that uses multi-agent AI architecture for market analysis, risk management, and trade execution. It leverages the Swarms framework for agent orchestration with Claude and GPT models.

## Build & Development Commands

### Install Dependencies
```bash
# Using Poetry (recommended)
poetry install

# Using pip
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
pytest tests/
pytest tests/unit/
pytest tests/integration/
pytest --cov=infinity_portal tests/
```

### Linting & Formatting
```bash
# Ruff (line-length: 70)
ruff check .
ruff check --fix .

# Black (line-length: 70)
black .

# Other linters
flake8 .
mypy infinity_portal/
pylint infinity_portal/
```

### Running the API
```bash
# Development
python api/api.py

# Production
uvicorn api.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
# Build and run with docker-compose (includes PostgreSQL and Redis)
docker-compose up --build

# Run only the app container
docker build -t infinity_portal .
docker run -p 8000:8000 --env-file .env infinity_portal
```

API docs available at `http://localhost:8000/docs` (Swagger) or `http://localhost:8000/redoc`

## Architecture

### Multi-Agent System

The system uses hierarchical multi-agent architecture with specialized agents:

1. **Trading Director** - Orchestrates strategy, generates trading theses, makes final decisions
2. **Quantitative Analyst** - Technical indicator analysis (RSI, MACD, Bollinger), support/resistance
3. **Risk Manager** - Position sizing (Kelly Criterion), drawdown analysis, stop loss/take profit
4. **Execution Agent** - Generates structured trade orders, entry/exit points
5. **Sentiment Agent** - News and social media sentiment analysis

### Key Components

- `infinity_portal/main.py` - Core `infinity_portal` class orchestrating all agents
- `api/api.py` - FastAPI REST server
- `infinity_portal/divergence_detector.py` - Sentiment-price divergence detection
- `infinity_portal/exchange_monitor.py` - Multi-exchange price monitoring
- `infinity_portal/trader_interface.py` - Interactive trader Q&A system
- `infinity_portal/tools/` - Broker integrations (E*TRADE, TD Ameritrade, TradeStation)

### Data Flow

```
Market Data Sources (yfinance, Finnhub, NewsAPI, Twitter)
    ↓
Data Collectors (news_collector, price_data_collector, social_media_collector)
    ↓
Processing (divergence detection, sentiment aggregation, technical analysis)
    ↓
Multi-Agent System (Director → Quant → Risk → Execution)
    ↓
Output (JSON trade recommendations, risk assessments, logs)
```

### Feature Flags

```python
infinity_portal(
    enable_divergence_detection=True,    # Sentiment-price divergence
    enable_exchange_monitoring=False,    # Multi-exchange price comparison
    enable_interactive_mode=False,       # Human-in-the-loop trader Q&A
    enable_sentiment_analysis=True       # News/social sentiment
)
```

## Environment Setup

Copy `.env.example` to `.env` and configure:

**Required:**
- `OPENAI_API_KEY` - For GPT models
- `ANTHROPIC_API_KEY` - For Claude models

**Optional Data Sources:**
- `FINNHUB_API_KEY`, `NEWSAPI_KEY`, `ALPHAVANTAGE_API_KEY` - Financial data
- `TWITTER_BEARER_TOKEN` - Social sentiment

## Code Style

- Line length: 70 characters (ruff, black)
- Python 3.10+ (Poetry requires ^3.10)
- CI tests against Python 3.9, 3.10, 3.11

## Basic Usage

```python
from infinity_portal import infinity_portal

trading_system = infinity_portal(stocks=["NVDA"])
result = trading_system.run(task="Analyze NVIDIA for $50k allocation")
```
