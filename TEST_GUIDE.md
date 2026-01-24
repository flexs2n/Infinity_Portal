# Testing Guide - Chart Fixes Verification

Follow these steps to verify all fixes are working correctly.

## Prerequisites

1. **Start Backend:**
   ```bash
   cd api
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd web
   npm run dev
   ```

3. **Open Browser:** `http://localhost:3000`

## Test Cases

### 1. Chart Rendering (No Re-render Issues)

**Test:** Navigate to any ticker page (e.g., `/ticker/BA`)

**Expected:**
- ✅ Chart renders smoothly without flickering
- ✅ No console errors
- ✅ Price line and volume bars display correctly
- ✅ Event windows (green/red shaded areas) appear
- ✅ Timeline below chart shows blue bars

**Fail Conditions:**
- ❌ Chart constantly re-renders
- ❌ Console shows React errors
- ❌ Chart is blank or broken

---

### 2. Single Point Selection

**Test:** Click once anywhere on the price chart

**Expected:**
- ✅ Black dashed vertical line appears at clicked point
- ✅ Blue dot on timeline moves to corresponding position
- ✅ Date label updates below timeline
- ✅ Topic label updates (if point is within event window)
- ✅ Orange message appears: "Click a second point to complete the range"

**Fail Conditions:**
- ❌ Nothing happens on click
- ❌ Line doesn't appear
- ❌ Timeline dot doesn't move
- ❌ Chart re-renders constantly

---

### 3. Two-Point Range Selection

**Test:** Click two different points on the chart

**Expected:**
- ✅ After first click: Orange message "Click a second point..."
- ✅ After second click:
  - Blue shaded area appears between the two points
  - Two green circular markers appear on timeline at range endpoints
  - "Clear Range" button appears in top-right
  - Blue info box shows: "Selected Range: [date] to [date]"
  - Green badge shows dominant topic for range
  - Message changes to "Range selected: ..."

**Fail Conditions:**
- ❌ Blue shaded area doesn't appear
- ❌ Range calculation is wrong
- ❌ Green markers don't show on timeline
- ❌ Topic detection fails

---

### 4. Range Reset

**Test:** After creating a range, click "Clear Range" button

**Expected:**
- ✅ Blue shaded area disappears
- ✅ Green timeline markers disappear
- ✅ "Clear Range" button disappears
- ✅ Blue info box disappears
- ✅ Message returns to "Click two points..."

**Fail Conditions:**
- ❌ Range doesn't clear
- ❌ Button doesn't work
- ❌ Visual elements remain

---

### 5. Third Click (New Range)

**Test:** After creating a range, click a third point WITHOUT clicking "Clear Range"

**Expected:**
- ✅ Previous range clears
- ✅ New range starts at third click point
- ✅ Orange message appears: "Click a second point..."
- ✅ Timeline dot moves to new position

**Fail Conditions:**
- ❌ Range doesn't reset
- ❌ Multiple ranges appear
- ❌ State becomes corrupted

---

### 6. Event Window Highlighting

**Test:** Observe the chart with event data loaded

**Expected:**
- ✅ Green shaded areas for positive events (move_pct > 0)
- ✅ Red shaded areas for negative events (move_pct < 0)
- ✅ Dashed borders on event windows
- ✅ Event windows don't interfere with range selection

**Fail Conditions:**
- ❌ Event windows missing
- ❌ Wrong colors
- ❌ Windows cover entire chart

---

### 7. Topic Detection

**Test:** Click points within and outside event windows

**Expected:**
- ✅ When point is IN event window: Topic label shows (e.g., "CEO Leadership Changes")
- ✅ When point is OUTSIDE event window: Shows "No topic"
- ✅ Range selection shows dominant topic with highest overlap

**Fail Conditions:**
- ❌ Topic always shows "No topic"
- ❌ Topic doesn't change with selection
- ❌ Topic detection crashes

---

### 8. Timeline Synchronization

**Test:** Click various points and observe timeline

**Expected:**
- ✅ Blue dot position matches chart vertical line
- ✅ Dot smoothly transitions (no jumping)
- ✅ Percentage calculation is accurate
- ✅ Blue bars (event windows) align with chart shaded areas

**Fail Conditions:**
- ❌ Dot doesn't move
- ❌ Dot position is wrong
- ❌ Timeline bars don't match chart

---

### 9. Topic Trends Component

**Test:** Scroll down on ticker page to "Topic Trends" section

**Expected:**
- ✅ Grid of small line charts appears
- ✅ Each chart shows weekly engagement trend
- ✅ Topic labels appear above each chart
- ✅ Total impressions number displayed
- ✅ Tooltips work on hover
- ✅ No animations/flickering

**Fail Conditions:**
- ❌ Component doesn't render
- ❌ Charts are blank
- ❌ API errors in console
- ❌ Crashes on load

---

### 10. API Endpoints

**Test:** Check backend API responses

```bash
# Test topic map
curl http://localhost:8000/ticker/BA/topic-map

# Test topic trends
curl http://localhost:8000/ticker/BA/topic-trends
```

**Expected:**
- ✅ topic-map returns array of EventTopicSummary objects
- ✅ topic-trends returns array of TopicTrendSeries with points
- ✅ No 404 errors
- ✅ JSON is valid

**Fail Conditions:**
- ❌ 404 Not Found
- ❌ 500 Server Error
- ❌ Empty arrays
- ❌ Invalid JSON

---

### 11. Performance (No Re-render Loops)

**Test:** Open browser DevTools, watch for excessive re-renders

**Steps:**
1. Open React DevTools Profiler
2. Click chart multiple times
3. Create/clear ranges
4. Observe render count

**Expected:**
- ✅ Each click triggers 1-2 renders (acceptable)
- ✅ No render loops (constant re-rendering)
- ✅ Smooth 60fps interactions
- ✅ No memory leaks

**Fail Conditions:**
- ❌ Chart re-renders 10+ times per click
- ❌ Browser becomes slow/laggy
- ❌ Memory usage grows continuously
- ❌ DevTools shows warnings

---

### 12. Visual Regression

**Test:** Compare with expected UI

**Expected Layout:**

```
┌─────────────────────────────────────────────┐
│ Stock price over time     [Clear Range]    │
│                                             │
│  $400 ┤                                     │
│       │     ╱╲                              │
│  $350 ┤    ╱  ╲   ╱╲                        │
│       │   ╱    ╲ ╱  ╲                       │
│  $300 ┤  ╱      ╲    ╲                      │
│       └─────────────────────────            │
│        Jan  Feb  Mar  Apr  May              │
│                                             │
│ [Event windows = green/red shaded]         │
│ [Selected range = blue shaded]             │
│ [Current line = black dashed]              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Social topic timeline                       │
│                                             │
│ ─────●━━━━━━━━●─────●───────●──────         │
│      ↑        ↑     ↑       ↑              │
│   Events   Range  Range   Event            │
│            Start   End                      │
│                                             │
│ Jan 15, 2019              CEO Leadership   │
│                                             │
│ Selected Range: Jan 10 to Jan 20           │
│          [Dominant Topic: 737 MAX Issues]  │
└─────────────────────────────────────────────┘
```

**Fail Conditions:**
- ❌ Layout is broken
- ❌ Elements overlap
- ❌ Colors are wrong
- ❌ Text is unreadable

---

## Browser Console Checklist

Open DevTools Console and verify:

- [ ] No React errors
- [ ] No "Warning: Each child should have unique key"
- [ ] No "Warning: Cannot update component while rendering"
- [ ] No "useEffect has missing dependencies"
- [ ] No 404 API errors
- [ ] No CORS errors

---

## Quick Smoke Test

**1-Minute Verification:**

1. Go to `http://localhost:3000`
2. Click "Boeing" or "Apple" card
3. Click chart once → See vertical line + timeline dot
4. Click chart again → See blue shaded area
5. Click "Clear Range" → Range disappears
6. Scroll down → See topic trends charts
7. No errors in console

**If all above work:** ✅ All critical bugs are fixed!

---

## Debugging Tips

### Chart Doesn't Render
- Check browser console for errors
- Verify API is running on port 8000
- Check `chartData` array has data with `index` property

### Clicks Don't Work
- Verify `handleChartClick` receives `state.activeTooltipIndex`
- Check state updates in React DevTools
- Ensure `useCallback` dependencies are correct

### ReferenceArea Wrong Position
- Verify using `index` not `timestamp` for x1/x2
- Check `chartData` includes `index` field
- Ensure `find()` and `findLast()` return valid points

### Timeline Dot Wrong Position
- Check `timelinePercent` calculation
- Verify `clampedIndex` is within bounds
- Ensure `chartData.length > 1` before division

### Topic Detection Fails
- Verify backend returns valid `topicMap` data
- Check timestamp comparisons use same timezone
- Ensure `topicByEventId` Map is populated

---

## Success Criteria

✅ **All systems operational when:**

1. Chart renders without flicker
2. Single clicks move timeline dot
3. Two clicks create blue range
4. Clear button removes range
5. Third click starts new range
6. Event windows display correctly
7. Topics update based on selection
8. Timeline markers sync with chart
9. Topic trends load and display
10. No console errors
11. Performance is smooth (60fps)
12. All API endpoints respond

---

**Last Updated:** 2026-01-24
**Status:** All fixes verified and operational ✅
