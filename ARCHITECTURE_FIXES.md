# Architecture Fixes & Debugging Summary

This document outlines all the fixes made to align with the updated app architecture and resolve chart interaction issues.

## Issues Fixed

### 1. Price Chart Re-rendering Problem ✅

**Problem:** Chart was re-rendering on every click, causing performance issues and broken interactions.

**Root Causes:**
- ChartData was being recalculated on every render
- State changes triggered unnecessary re-renders
- No memoization of expensive calculations

**Solution:**
```typescript
// Added memoization
const chartData = useMemo(() => {
  return prices.map((p, index) => ({
    index,  // Critical: added for proper ReferenceArea coordinates
    date: new Date(p.ts).getTime(),
    dateStr: formatDate(p.ts),
    price: p.price,
    volume: p.volume / 1000000,
  }))
}, [prices])

// Added useCallback for event handlers
const handleChartClick = useCallback((state: any) => {
  // ... click logic
}, [rangeStartIndex, rangeEndIndex])
```

### 2. Interval Selection Not Working ✅

**Problem:** ReferenceArea components were using wrong coordinate system (timestamps vs indices).

**Root Cause:**
- Recharts ReferenceArea x1/x2 props expect dataKey values, not raw timestamps
- Original code was passing timestamps directly: `x1={start}` where start was a Date.getTime()

**Solution:**
```typescript
// Event windows - find data points by timestamp, use their index
{events.map((event) => {
  const start = new Date(event.window_start).getTime()
  const end = new Date(event.window_end).getTime()

  const startDataPoint = chartData.find(d => d.date >= start)
  const endDataPoint = chartData.findLast(d => d.date <= end)

  if (!startDataPoint || !endDataPoint) return null

  return (
    <ReferenceArea
      key={event.id}
      yAxisId="price"
      x1={startDataPoint.index}  // ✅ Use index
      x2={endDataPoint.index}    // ✅ Use index
      // ...
    />
  )
})}

// Selected range
{selectedRange && (
  <ReferenceArea
    yAxisId="price"
    x1={selectedRange.startIndex}  // ✅ Use index, not startLabel
    x2={selectedRange.endIndex}    // ✅ Use index, not endLabel
    fill="#3b82f6"
    fillOpacity={0.15}
  />
)}

// Current selection line
<ReferenceLine
  x={clampedIndex}  // ✅ Use index, not dateStr
  yAxisId="price"
  stroke="#1f2937"
  strokeWidth={2}
  strokeDasharray="4 4"
/>
```

### 3. Two-Point Interval Selection Logic ✅

**Problem:** Click handler wasn't properly tracking first/second clicks for range selection.

**Solution:**
```typescript
const handleChartClick = useCallback((state: any) => {
  if (!state?.activeTooltipIndex && state?.activeTooltipIndex !== 0) return
  const clickedIndex = state.activeTooltipIndex

  setSelectedIndex(clickedIndex)

  // Two-point selection logic
  if (rangeStartIndex === null || (rangeStartIndex !== null && rangeEndIndex !== null)) {
    // First click: start new range
    setRangeStartIndex(clickedIndex)
    setRangeEndIndex(null)
  } else {
    // Second click: complete range
    setRangeEndIndex(clickedIndex)
  }
}, [rangeStartIndex, rangeEndIndex])
```

**User Experience:**
1. **First Click:** Sets range start point, shows orange message "Click a second point to complete the range"
2. **Second Click:** Sets range end point, creates blue shaded area
3. **Third Click:** Resets and starts new range

### 4. Chart Animation Issues ✅

**Problem:** Animations were causing re-render loops and visual glitches.

**Solution:**
```typescript
<Line
  type="monotone"
  dataKey="price"
  stroke="#3b82f6"
  strokeWidth={2}
  dot={false}
  isAnimationActive={false}  // ✅ Disable animations
/>

<Bar
  yAxisId="volume"
  dataKey="volume"
  fill="#d1d5db"
  opacity={0.3}
  isAnimationActive={false}  // ✅ Disable animations
/>
```

### 5. Missing Backend Endpoints ✅

**Added Endpoints:**
- `GET /ticker/{ticker}/topic-map` - Returns top topic per event window
- `GET /ticker/{ticker}/topic-trends` - Returns weekly engagement trends

**Implementation:**
- Located in `/api/routers/ticker.py`
- Uses existing data_loader functions
- Aggregates engagement data into weekly time series
- Returns top 10 topics by total impressions

### 6. Created TopicTrends Component ✅

**Features:**
- Small multiple line charts showing weekly engagement per topic
- Color-coded topics (10-color palette)
- Responsive grid layout (1/2/3 columns)
- Total impressions display
- Methodology disclaimer
- Disabled animations for performance

## Architecture Alignment

### Data Flow

```
User clicks chart
    ↓
handleChartClick(state.activeTooltipIndex)
    ↓
setSelectedIndex(clickedIndex)
setRangeStartIndex / setRangeEndIndex
    ↓
useMemo recalculates:
  - selectedRange (start/end indices + dates)
  - activeRangeTopic (dominant topic in range)
    ↓
Timeline dot + range markers update
    ↓
Topic label displays
```

### Component Structure

```
PriceChart
├── Top Card
│   ├── ComposedChart
│   │   ├── Event ReferenceAreas (green/red)
│   │   ├── Selected Range ReferenceArea (blue)
│   │   ├── Current Line (black dashed)
│   │   ├── Volume Bars
│   │   └── Price Line
│   └── Clear Range Button
└── Bottom Card
    ├── Topic Timeline
    │   ├── Event windows (blue bars)
    │   ├── Current dot (blue)
    │   └── Range markers (green)
    ├── Current Point Info
    └── Selected Range Info

TopicTrends
└── Grid of mini charts
    └── LineChart per topic
```

### State Management

```typescript
// Selection state
const [selectedIndex, setSelectedIndex] = useState<number>(0)
const [rangeStartIndex, setRangeStartIndex] = useState<number | null>(null)
const [rangeEndIndex, setRangeEndIndex] = useState<number | null>(null)

// Derived state (memoized)
const selectedPoint = chartData[clampedIndex]
const activeEvent = useMemo(() => /* find event */, [events, selectedPoint])
const activeTopic = activeEvent ? topicByEventId.get(activeEvent.id) : null
const selectedRange = useMemo(() => /* calculate range */, [rangeStartIndex, rangeEndIndex])
const activeRangeTopic = useMemo(() => /* find dominant topic */, [selectedRange, topicMap])
```

## Visual Feedback

### Timeline Indicators

1. **Blue Bars:** Event windows with topics
2. **Blue Dot:** Current selected point (follows last click)
3. **Green Markers:** Range selection endpoints (only when range is active)

### Chart Overlays

1. **Event Windows:** Green (positive) / Red (negative) shaded areas
2. **Selected Range:** Blue shaded area between two click points
3. **Current Line:** Black dashed vertical line at selected point

### Status Messages

- **No selection:** "Click two points on the chart to select an analysis range"
- **First click:** "Click a second point to complete the range" (orange)
- **Range complete:** "Range selected: [date] to [date]" (blue)

## Testing Checklist

- [x] Click single point - moves timeline dot
- [x] Click second point - creates shaded range
- [x] Click third point - resets and starts new range
- [x] Clear Range button - removes selection
- [x] Chart renders without flickering
- [x] Event windows display correctly
- [x] Topic labels update based on selection
- [x] Timeline dots match chart selection
- [x] Range markers show at correct positions
- [x] Topic trends component loads
- [x] Weekly trend charts display
- [x] All API endpoints respond

## Files Modified

1. `/web/components/ticker/price-chart.tsx` - Complete rewrite with fixes
2. `/web/components/ticker/topic-trends.tsx` - New component
3. `/api/routers/ticker.py` - Added topic-map and topic-trends endpoints
4. `/api/models.py` - Added EventTopicSummary, TopicTrendPoint, TopicTrendSeries models
5. `/web/lib/api-client.ts` - Added getTopicMap() and getTopicTrends() methods
6. `/web/lib/types.ts` - Added EventTopicSummary, TopicTrendPoint, TopicTrendSeries types

## Performance Optimizations

1. **Memoization:** chartData, selectedRange, activeEvent, activeTopic, activeRangeTopic
2. **Callbacks:** handleChartClick, handleClearRange, getPercentForDate
3. **Disabled Animations:** All Recharts components set `isAnimationActive={false}`
4. **Conditional Rendering:** ReferenceAreas only render when data exists

## Known Limitations

1. **Range Selection:** Currently linear (start to end). Could enhance with drag-to-select.
2. **Topic Detection:** Uses max overlap + share_of_posts. Could use weighted algorithm.
3. **Timeline:** Fixed height. Could be responsive to number of events.
4. **Trends:** Only shows top 10 topics. Could add pagination or filtering.

## Future Enhancements

1. **Drag Selection:** Add mouse down/move/up handlers for range selection
2. **Time Callouts:** "Time A" / "Time B" labels on range markers
3. **Dashed Connector:** Visual line connecting chart range to timeline
4. **Zoom Controls:** Ability to zoom into specific date ranges
5. **Topic Filtering:** Filter chart by specific topic
6. **Export Range:** Export analysis for selected range only
7. **Comparison Mode:** Compare two different ranges side-by-side

---

**Status:** ✅ All critical bugs fixed and architecture aligned with specifications.
