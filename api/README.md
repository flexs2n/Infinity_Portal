# Wealth Management Evidence API

FastAPI backend for the trust-first wealth management platform. Serves static social media dataset analysis for stock movement events.

## Features

- **Static Data**: No live scraping, no external APIs
- **Evidence-Based**: Topics with supporting and counter-narratives
- **Confidence Metrics**: Coverage, sentiment coherence, and recency scoring
- **Export**: Generate markdown memos with disclaimers
- **CORS Enabled**: Configured for Next.js frontend on localhost:3000

## Installation

```bash
cd api
pip install -r requirements.txt
```

## Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once running, view interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### `GET /instruments`
Get all available stock instruments.

**Response:**
```json
[
  {
    "ticker": "BA",
    "name": "Boeing Co."
  }
]
```

### `GET /ticker/{ticker}/series`
Get price series for a ticker.

**Query Parameters:**
- `start` (optional): ISO datetime string to filter from
- `end` (optional): ISO datetime string to filter to

**Response:**
```json
[
  {
    "ticker": "BA",
    "ts": "2019-01-02T16:00:00Z",
    "price": 350.25,
    "volume": 4125000
  }
]
```

### `GET /ticker/{ticker}/events`
Get all movement events for a ticker.

**Response:**
```json
[
  {
    "id": "ba_737max_grounding",
    "ticker": "BA",
    "window_start": "2019-03-10T00:00:00Z",
    "window_end": "2019-03-16T23:59:59Z",
    "move_pct": -11.2,
    "vol_z": 8.5,
    "headline": "Discussion patterns associated with 737 MAX fleet grounding"
  }
]
```

### `GET /ticker/{ticker}/event/{event_id}`
Get detailed event analysis with topics, posts, and confidence metrics.

**Response:**
```json
{
  "event": { ... },
  "topics": [ ... ],
  "posts": [ ... ],
  "confidence": {
    "coverage": 85.0,
    "sentiment_coherence": 72.0,
    "recency": 90.0,
    "overall": 82.3
  }
}
```

### `POST /export`
Export event analysis as markdown memo.

**Request Body:**
```json
{
  "event_id": "ba_737max_grounding",
  "ticker": "BA",
  "selected_topics": null,
  "include_counter_narratives": true
}
```

**Response:**
```json
{
  "markdown": "# Stock Movement Analysis...",
  "filename": "BA_ba_737max_grounding_analysis_20240124.md"
}
```

## Project Structure

```
api/
├── main.py                 # FastAPI app entry point
├── models.py              # Pydantic request/response models
├── requirements.txt       # Python dependencies
├── routers/
│   ├── instruments.py     # GET /instruments
│   ├── ticker.py          # Ticker endpoints
│   └── export.py          # POST /export
└── services/
    ├── data_loader.py     # Load sample.json into memory
    └── calculations.py    # Confidence metrics
```

## Data Source

The API loads data from `/data/sample.json` on startup and caches it in memory. The dataset includes:
- 2 instruments (BA, AAPL)
- 6 events (3 per ticker)
- ~33 topics
- ~270 posts
- ~522 price points

## Key Design Decisions

1. **No Database**: All data loaded from JSON file for simplicity
2. **In-Memory Cache**: Fast responses, no disk I/O per request
3. **Correlation Language**: All copy avoids causal claims
4. **Confidence Metrics**: Transparent quality scoring
5. **No Buy/Sell Advice**: Strict compliance with non-advisory language

## Environment Variables

- `NEXT_PUBLIC_API_URL` (optional): Override API base URL (defaults to http://localhost:8000)

## Development

To modify data:
1. Edit `/data/sample.json` directly, or
2. Run `/data/transform_boeing.py` to regenerate from Boeing_clean.csv
3. Restart server to reload data

## License

Proprietary - For wealth management professionals only.
