# Quick Start Guide

Get the Trust-First Wealth Management platform running in 3 steps.

## Prerequisites

- Python 3.11+ with pip
- Node.js 18+ with npm
- Terminal access

## Step 1: Generate Data (Already Done!)

The sample data has already been generated in `data/sample.json`. If you need to regenerate:

```bash
cd data
python3 transform_boeing.py
cd ..
```

**What this creates:**
- 2 instruments: BA (Boeing), AAPL (Apple)
- 6 events: 3 for each ticker
- ~270 posts from social media
- ~522 price data points

## Step 2: Start the Backend

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/api']
INFO:     Uvicorn running on http://127.0.0.1:8000
✓ Loaded data: 270 posts, 6 events
```

**Test it:** Open `http://localhost:8000/docs` to see Swagger UI.

**Leave this terminal running.**

## Step 3: Start the Frontend

Open a **new terminal** window:

```bash
cd web
npm install
npm run dev
```

**Expected output:**
```
  ▲ Next.js 14.1.0
  - Local:        http://localhost:3000
  ✓ Ready in 2.5s
```

**Open the app:** `http://localhost:3000`

## What You'll See

### Dashboard (/)
- 2 instrument cards (BA, AAPL)
- Recent event previews
- Price snapshots

### Ticker Detail (/ticker/BA)
- Price chart with event windows highlighted
- List of 3 Boeing events

### Event Detail (/ticker/BA/event/ba_737max_grounding)
- Topics ranked by discussion share
- Confidence metrics (coverage, sentiment, recency)
- Click "View Evidence" to see posts
- Toggle "Client-Safe Mode" in header
- Click "Export Memo" to download markdown

### Audit Log (/audit)
- Track all your actions
- Export history
- Download JSON log

## Try These Features

### 1. Client-Safe Mode
1. Toggle "Client-Safe Mode" in the top-right header
2. Navigate to any event detail page
3. Click "View Evidence" on a topic
4. Notice handles are hidden: `@[hidden]`
5. Text is truncated to 50 chars

### 2. Evidence Panels
1. Go to `/ticker/BA/event/ba_737max_grounding`
2. Click the evidence count (e.g., "15 posts") on any topic
3. Modal opens with supporting posts
4. Switch to "Counter-Narrative" tab
5. See opposing viewpoints

### 3. Export Memo
1. On any event detail page, click "Export Memo"
2. Markdown file downloads
3. Open to see:
   - Disclaimers (not investment advice)
   - Confidence metrics
   - Topic summaries with citations
   - Methodology section

### 4. Audit Log
1. Navigate around the app
2. Go to `/audit`
3. See all your actions logged
4. Click "Export as JSON" to download

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000

# If needed, kill the process
kill -9 $(lsof -ti:8000)
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -ti:3000

# If needed, kill the process
kill -9 $(lsof -ti:3000)

# Or run on different port
npm run dev -- -p 3001
```

### "API connection failed"
- Ensure backend is running on port 8000
- Check `http://localhost:8000` in browser
- Verify CORS middleware in `api/main.py`

### Module not found errors
```bash
# Backend
cd api && pip install -r requirements.txt

# Frontend
cd web && npm install
```

## Next Steps

1. **Read the docs:**
   - Main README: `/README.md`
   - API README: `/api/README.md`
   - Frontend README: `/web/README.md`

2. **Explore the code:**
   - Backend endpoints: `api/routers/`
   - Frontend pages: `web/app/`
   - Components: `web/components/`

3. **Modify data:**
   - Edit `data/sample.json` directly, or
   - Run `python3 data/transform_boeing.py` to regenerate

4. **Customize:**
   - Add new tickers
   - Adjust confidence calculations
   - Modify UI styling

## Architecture Overview

```
User Browser (localhost:3000)
    ↓
Next.js Frontend
    ├── Pages: Dashboard, Ticker, Event, Audit
    ├── Client-Safe Mode (localStorage)
    └── Audit Logger (localStorage)
    ↓
    HTTP/JSON
    ↓
FastAPI Backend (localhost:8000)
    ├── Endpoints: /instruments, /ticker/*, /export
    ├── Data Loader (loads sample.json once)
    └── Confidence Calculations
    ↓
Static Data (data/sample.json)
    ├── Instruments
    ├── Events
    ├── Topics
    ├── Posts
    └── Price Series
```

## Key Files

| File | Purpose |
|------|---------|
| `api/main.py` | FastAPI entry point |
| `api/models.py` | Pydantic request/response models |
| `api/routers/ticker.py` | Main event detail endpoint |
| `web/app/page.tsx` | Dashboard |
| `web/app/ticker/[ticker]/event/[id]/page.tsx` | Event detail |
| `web/lib/api-client.ts` | Fetch wrapper for backend |
| `web/lib/audit-logger.ts` | localStorage audit trail |
| `data/sample.json` | All app data |

## Port Reference

- **3000**: Next.js frontend
- **8000**: FastAPI backend

## Support

Questions? Check:
1. API docs at `http://localhost:8000/docs`
2. README files in `/`, `/api`, `/web`
3. Code comments in source files

---

**You're all set! Enjoy exploring the platform.**
