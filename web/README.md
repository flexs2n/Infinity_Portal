# Wealth Management Evidence Platform - Frontend

Next.js 14 frontend for trust-first stock movement analysis using static social media datasets.

## Features

- **Evidence-First UI**: Every narrative links to sources and counter-narratives
- **Client-Safe Mode**: Hide sensitive information for client presentations
- **Audit Log**: Track all user actions for compliance
- **Export Memos**: Download markdown reports with disclaimers
- **Interactive Charts**: Recharts price series with event markers
- **Confidence Metrics**: Transparent data quality assessment

## Installation

```bash
cd web
npm install
```

## Running the App

```bash
# Development mode
npm run dev

# Production build
npm run build
npm start
```

The app will be available at `http://localhost:3000`.

**Important:** The backend API must be running on `http://localhost:8000` before starting the frontend.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui + Radix UI primitives
- **Charts**: Recharts
- **State**: React Context + localStorage
- **Data Fetching**: Native fetch API

## Routes

### `/` - Dashboard
- View all instruments
- See recent events
- Navigate to ticker detail

### `/ticker/[ticker]` - Ticker Detail
- Price chart with event windows highlighted
- List of all movement events
- Click event to view analysis

### `/ticker/[ticker]/event/[id]` - Event Detail
- Evidence-based narratives (topics)
- Confidence assessment
- Evidence and counter-narrative panels
- Client-safe mode toggle
- Export memo button
- Transparency panel ("Why am I seeing this?")

### `/audit` - Audit Log
- View all user actions
- Export history
- Download audit log as JSON

## Key Components

### Layout
- `app/layout.tsx` - Root layout with navigation
- `components/client-safe-toggle.tsx` - Global client-safe mode toggle

### Dashboard
- `components/dashboard/instrument-card.tsx` - Ticker summary cards

### Ticker
- `components/ticker/price-chart.tsx` - Recharts price/volume chart
- `components/ticker/event-card.tsx` - Event summary cards

### Event Detail
- `components/event/confidence-meter.tsx` - Visual confidence metrics
- `components/event/topics-table.tsx` - Ranked topics with evidence counts
- `components/event/evidence-panel.tsx` - Modal showing posts
- `components/event/transparency-panel.tsx` - Methodology explanation
- `components/event/export-button.tsx` - Download markdown memo

### Audit
- `components/audit/audit-log-table.tsx` - User action history
- `components/audit/export-history-table.tsx` - Memo export tracking

## Core Libraries

### API Client (`lib/api-client.ts`)
Fetch wrapper for all backend endpoints:
- `getInstruments()`
- `getPriceSeries(ticker, start?, end?)`
- `getEvents(ticker)`
- `getEventDetail(ticker, eventId)`
- `exportMemo(request)`

### Audit Logger (`lib/audit-logger.ts`)
localStorage-based audit trail:
- `logAuditAction(action, details)`
- `getAuditLog()`
- `exportAuditLog()`

### Client-Safe Context (`lib/client-safe-context.tsx`)
Global state for sensitive info visibility:
- `useClientSafe()` hook
- Persists to localStorage
- Controls: hide handles, truncate text

## Copy Rules

The UI strictly enforces trust-first language:

**Avoid:**
- "The reason was..."
- "This caused..."
- Buy/sell/hold recommendations
- Price targets

**Use:**
- "Evidence suggests..."
- "Most-discussed themes..."
- "Associated with..."
- "Correlation" not "causation"

## Client-Safe Mode

When enabled:
- Hides `@handles` → `@[hidden]`
- Truncates post text to 50 chars
- Shows post IDs for reference
- Persists across sessions

## Audit Logging

All actions logged to localStorage:
- `viewed_event` - User viewed event detail page
- `opened_evidence` - User opened evidence panel
- `toggled_client_safe` - Changed client-safe mode
- `weighted_by_engagement` - Changed topic weighting
- `exported_memo` - Downloaded markdown file

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
web/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard (/)
│   ├── ticker/[ticker]/
│   │   ├── page.tsx         # Ticker detail
│   │   └── event/[id]/
│   │       └── page.tsx     # Event detail
│   └── audit/
│       └── page.tsx         # Audit log
├── components/
│   ├── ui/                  # shadcn/ui components
│   ├── dashboard/
│   ├── ticker/
│   ├── event/
│   └── audit/
└── lib/
    ├── api-client.ts        # Backend API client
    ├── audit-logger.ts      # Audit logging
    ├── client-safe-context.tsx
    ├── types.ts             # TypeScript interfaces
    └── utils.ts             # Helper functions
```

## Development Notes

### Adding New Components

Use shadcn/ui CLI (if needed):
```bash
npx shadcn-ui@latest add [component]
```

Or manually create in `components/ui/` following shadcn patterns.

### Modifying API Types

1. Update `lib/types.ts` to match backend Pydantic models
2. Update `lib/api-client.ts` if endpoint signatures change

### Testing Client-Safe Mode

1. Toggle client-safe mode in header
2. Open evidence panel
3. Verify handles hidden and text truncated
4. Check localStorage persists setting

## Common Issues

### API Connection Failed
- Ensure backend running on port 8000
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify CORS enabled in FastAPI

### Hydration Errors
- Client-safe context prevents mismatch with `mounted` state
- localStorage only accessed after mount

### Chart Not Rendering
- Check Recharts ResponsiveContainer has explicit height
- Ensure data format matches expected shape

## License

Proprietary - For wealth management professionals only.
