# Wealth Management Evidence Platform

Web application for financial advisors to analyze stock movements using static social media datasets. Shows correlation between discussion patterns and price changes. Not investment advice.

## Features

- Interactive price charts with event windows
- Topic analysis with supporting and counter-evidence
- Two-point interval selection for timeline analysis
- Topic trend visualization (weekly impressions)
- Client-safe mode for presentations
- Audit logging for compliance
- Markdown memo export with disclaimers

## Tech Stack

**Backend:** FastAPI, Pydantic, static JSON data  
**Frontend:** Next.js 14, Tailwind CSS, Recharts  
**Data:** Boeing Twitter dataset (12,826 posts), synthetic Apple data

## Quick Start

```bash
# Generate data
cd data && python3 transform_boeing.py

# Start backend (port 8000)
cd ../api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start frontend (port 3000)
cd ../web
npm install
npm run dev
```

Open `http://localhost:3000` for the app and `http://localhost:8000/docs` for API docs.

## Structure

```
├── data/                  # Data transformation
│   ├── sample.json
│   └── transform_boeing.py
├── api/                   # FastAPI backend
│   ├── main.py
│   ├── models.py
│   ├── routers/
│   └── services/
└── web/                   # Next.js frontend
    ├── app/
    ├── components/
    └── lib/
```

## API Endpoints

- `GET /instruments` - List tickers
- `GET /ticker/{ticker}/series` - Price history
- `GET /ticker/{ticker}/events` - Movement events
- `GET /ticker/{ticker}/event/{id}` - Event detail
- `GET /ticker/{ticker}/topic-map` - Top topic per event
- `GET /ticker/{ticker}/topic-trends` - Weekly topic trends
- `POST /export` - Generate markdown memo

## Routes

- `/` - Dashboard
- `/ticker/{ticker}` - Price chart and timeline
- `/ticker/{ticker}/event/{id}` - Event detail with evidence
- `/audit` - Audit log

## Limitations

- Correlation does not imply causation
- Social media represents retail sentiment only
- Static historical dataset
- Not investment advice

## License

Proprietary
