app# Trust-First Wealth Management Evidence Platform

A web application for **wealth managers**, **financial advisors**, and **compliance teams** to analyze stock movements using static social media datasets. Built with evidence-first principles: every narrative links to sources and counter-narratives.

**Key Principle:** This platform shows *correlation*, not *causation*. It is NOT investment advice.

## Overview

This platform helps wealth management professionals:
- Understand social media discussion patterns during stock movements
- Present evidence-based narratives to clients
- Maintain compliance through audit logging
- Generate client-safe memos with disclaimers

## Features

### 🔍 Evidence-First Analysis
- Every topic linked to specific posts (by ID)
- Counter-narratives shown alongside supporting evidence
- Confidence metrics (coverage, sentiment coherence, recency)
- "Why am I seeing this?" transparency panel

### 🛡️ Trust & Compliance
- **Client-Safe Mode**: Hides handles and truncates text for presentations
- **Audit Log**: Tracks all user actions (viewed events, toggled settings, exports)
- **Export Memos**: Markdown files with disclaimers and methodology
- **Correlation Language**: Never says "caused" or gives buy/sell advice

### 📊 Rich Visualizations
- Price charts with event windows highlighted
- Topic ranking by share of discussion
- Engagement-weighted view
- Sentiment scoring (-1 to +1)

## Tech Stack

### Backend (Python)
- FastAPI
- Pydantic models
- Static JSON data (no database)
- CORS enabled for localhost frontend

### Frontend (TypeScript)
- Next.js 14 (App Router)
- Tailwind CSS
- shadcn/ui components
- Recharts for visualizations
- localStorage for audit + client-safe mode

### Data
- Boeing Twitter dataset (12,826 posts from 2019)
- Synthetic Apple data
- Pre-computed topic clusters
- Generated price series

## Quick Start

### 1. Generate Sample Data

```bash
cd data
python3 transform_boeing.py
```

This transforms `Boeing_clean.csv` into `sample.json` with:
- 2 instruments (BA, AAPL)
- 6 events (3 per ticker)
- ~33 topics
- ~270 posts
- ~522 price points

### 2. Start the Backend

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`.
View docs at `http://localhost:8000/docs`.

### 3. Start the Frontend

```bash
cd web
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`.

## Project Structure

```
/
├── Boeing_clean.csv         # Source data (12,826 Boeing tweets)
├── data/
│   ├── sample.json         # Transformed dataset
│   └── transform_boeing.py # Data transformation script
├── api/                    # FastAPI backend
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── instruments.py
│   │   ├── ticker.py
│   │   └── export.py
│   └── services/
│       ├── data_loader.py
│       └── calculations.py
└── web/                    # Next.js frontend
    ├── app/
    │   ├── page.tsx                      # Dashboard
    │   ├── ticker/[ticker]/page.tsx      # Ticker detail
    │   ├── ticker/[ticker]/event/[id]/page.tsx  # Event detail
    │   └── audit/page.tsx                # Audit log
    ├── components/
    │   ├── ui/             # shadcn/ui components
    │   ├── dashboard/
    │   ├── ticker/
    │   ├── event/
    │   └── audit/
    └── lib/
        ├── api-client.ts
        ├── audit-logger.ts
        ├── client-safe-context.tsx
        └── types.ts
```

## Key Endpoints

### Backend API

- `GET /instruments` - List all tickers
- `GET /ticker/{ticker}/series` - Price history
- `GET /ticker/{ticker}/events` - Movement events
- `GET /ticker/{ticker}/event/{id}` - Event detail with topics + posts + confidence
- `POST /export` - Generate markdown memo

### Frontend Routes

- `/` - Dashboard with instrument cards
- `/ticker/BA` - Boeing price chart + events
- `/ticker/BA/event/ba_737max_grounding` - Event detail with evidence
- `/audit` - Audit log + export history

## Data Model

### Event
A period with significant price movement and social media discussion.

```typescript
{
  id: "ba_737max_grounding",
  ticker: "BA",
  window_start: "2019-03-10T00:00:00Z",
  window_end: "2019-03-16T23:59:59Z",
  move_pct: -11.2,
  vol_z: 8.5,
  headline: "Discussion patterns associated with 737 MAX fleet grounding"
}
```

### Topic
A discussion theme identified via NLP clustering.

```typescript
{
  id: "ba_737max_grounding_737_max_faa_pilot",
  topic_label: "737 MAX Regulatory Issues",
  keywords: ["737 max", "faa", "pilot", "grounding"],
  share_of_posts: 0.35,
  sentiment_score: -0.62,
  evidence_post_ids: [...],
  counter_post_ids: [...]
}
```

### Post
A social media post (Twitter/X).

```typescript
{
  id: "ba_1234",
  ts: "2019-03-12T14:30:00Z",
  platform: "twitter",
  author_handle: "aviation_analyst",
  text: "FAA grounds 737 MAX fleet...",
  engagement: 1250
}
```

### Confidence Metrics
Transparent quality scoring.

```typescript
{
  coverage: 85.0,           // Post volume vs baseline
  sentiment_coherence: 72.0, // Agreement across topics
  recency: 90.0,            // Time decay from event
  overall: 82.3             // Weighted average
}
```

## Usage Flow

1. **Dashboard** → Browse tickers (BA, AAPL)
2. **Ticker Detail** → See price chart with event markers
3. **Event Detail** → View evidence-based narratives:
   - Topics ranked by share of discussion
   - Click evidence count to view posts
   - Toggle "Weight by Engagement" to rerank
   - See confidence metrics
   - Read transparency panel
4. **Evidence Panel** → View supporting and counter posts
   - Toggle client-safe mode to hide handles
   - Posts sorted by engagement
5. **Export Memo** → Download markdown file with:
   - Event summary
   - Confidence metrics
   - Topic narratives with citations
   - Disclaimers (correlation not causation, not investment advice)
6. **Audit Log** → Track all actions for compliance

## Client-Safe Mode

Toggle in header to hide sensitive information:

**Before (Normal Mode):**
```
@aviation_analyst • Mar 12, 2019 • twitter
FAA grounds 737 MAX fleet following Ethiopian Airlines crash. Boeing shares down 11% in early trading.
```

**After (Client-Safe Mode):**
```
@[hidden] • Mar 12, 2019
FAA grounds 737 MAX fleet following Ethiopian...
Post ID: ba_1234
```

## Copy Rules

The platform enforces trust-first language:

❌ **Avoid:**
- "The reason was..."
- "This caused the price to drop"
- "We recommend..."
- "Target price: $X"

✅ **Use:**
- "Evidence suggests..."
- "Most-discussed themes..."
- "Associated with..."
- "Correlation" not "causation"

## Audit Logging

All actions logged to localStorage:

| Action | Description |
|--------|-------------|
| `viewed_event` | User viewed event detail page |
| `opened_evidence` | User opened evidence panel |
| `toggled_client_safe` | Changed client-safe mode |
| `weighted_by_engagement` | Changed topic weighting |
| `exported_memo` | Downloaded markdown file |

Export audit log as JSON for compliance records.

## Export Memo Example

```markdown
# Stock Movement Analysis: BA - 2019-03-10 to 2019-03-16

**DISCLAIMER**: This memo presents evidence-based analysis of social media
discussion patterns associated with stock price movements. It does NOT
constitute investment advice, recommendations to buy/sell securities, or
price targets. All analysis is based on static historical datasets.

## Event Summary
- Price Movement: -11.2%
- Volatility Score: 8.5 standard deviations
- Headline: Discussion patterns associated with 737 MAX fleet grounding

## Confidence Assessment
- Coverage: 85.0/100
- Sentiment Coherence: 72.0/100
- Overall Confidence: 82.3/100

## Evidence-Based Narratives

### 1. 737 MAX Regulatory Issues
- Share of Discussion: 35.0%
- Sentiment Score: -0.62
- Keywords: 737 max, faa, pilot, grounding
- Supporting Evidence: 15 posts
- Counter-Narratives: 3 posts

...

## Methodology & Data Sources
- Static social media dataset (Twitter/X)
- No live scraping or external APIs
- Topic clustering via NLP entity extraction
- Correlation-based analysis only

**Important Limitations:**
- Social media discussion does NOT prove causation
- This is educational content, NOT investment advice
```

## Environment Variables

### Backend (Optional)
No environment variables required. Data loaded from `data/sample.json`.

### Frontend
Create `web/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

### Regenerate Data

```bash
cd data
python3 transform_boeing.py
```

This reads `Boeing_clean.csv` and generates new `sample.json`.

### Add New Ticker

1. Add instrument to `sample.json`:
   ```json
   {"ticker": "TSLA", "name": "Tesla Inc."}
   ```
2. Add events, topics, posts for that ticker
3. Add price series data

### Modify Confidence Calculation

Edit `api/services/calculations.py` → `calculate_confidence()`.

Current formula:
```python
overall = (coverage * 0.4) + (coherence * 0.3) + (recency * 0.3)
```

## Security & Compliance

- ✅ No live scraping (static datasets only)
- ✅ No external APIs
- ✅ Client-safe mode for presentations
- ✅ Audit logging for all actions
- ✅ Export memos include disclaimers
- ✅ Never provides buy/sell recommendations
- ✅ Strict correlation (not causation) language

## Limitations

1. **Correlation ≠ Causation**: Social media discussion patterns may correlate with price movements but do not prove causation.

2. **Incomplete Picture**: Social media represents retail sentiment, not institutional trading activity.

3. **Sentiment Analysis Errors**: Automated classification may misinterpret sarcasm, context, or nuance.

4. **Static Dataset**: Data is historical. No real-time updates.

5. **Not Investment Advice**: This tool is for research and education only.

## License

Proprietary - For wealth management professionals only.

## Support

For issues or questions:
1. Check API docs at `http://localhost:8000/docs`
2. Review `api/README.md` and `web/README.md`
3. Contact development team

---

**Built with trust-first principles for wealth management professionals.**
