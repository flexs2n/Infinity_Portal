'use client'

import { PricePoint, Event, EventTopicSummary } from "@/lib/types"
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"
import { useMemo, useState, useCallback } from "react"

interface PriceChartProps {
  prices: PricePoint[]
  events: Event[]
  topicMap: EventTopicSummary[]
}

export function PriceChart({ prices, events, topicMap }: PriceChartProps) {
  // State initialization BEFORE early return
  const [selectedIndex, setSelectedIndex] = useState(prices.length - 1)
  const [rangeStartIndex, setRangeStartIndex] = useState<number | null>(null)
  const [rangeEndIndex, setRangeEndIndex] = useState<number | null>(null)

  if (prices.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          No price data available
        </CardContent>
      </Card>
    )
  }

  // Transform data for Recharts with index for ReferenceArea
  const chartData = useMemo(() => {
    return prices.map((p, index) => ({
      index,  // ADD index for ReferenceArea x1/x2
      date: new Date(p.ts).getTime(),
      dateStr: formatDate(p.ts),
      price: p.price,
      volume: p.volume / 1000000, // Convert to millions
    }))
  }, [prices])

  const clampedIndex = Math.max(0, Math.min(selectedIndex, chartData.length - 1))
  const selectedPoint = chartData[clampedIndex]

  const minDate = Math.min(...chartData.map((point) => point.date))
  const maxDate = Math.max(...chartData.map((point) => point.date))
  const getPercentForDate = (date: number) => {
    if (maxDate === minDate) return 0
    return ((date - minDate) / (maxDate - minDate)) * 100
  }

  const activeEvent = useMemo(() => {
    if (!selectedPoint) return null
    return events.find((event) => {
      const start = new Date(event.window_start).getTime()
      const end = new Date(event.window_end).getTime()
      return selectedPoint.date >= start && selectedPoint.date <= end
    })
  }, [events, selectedPoint])

  const topicByEventId = useMemo(() => {
    return new Map(topicMap.map((topic) => [topic.event_id, topic]))
  }, [topicMap])

  const activeTopic = activeEvent ? topicByEventId.get(activeEvent.id) : null

  const selectedRange = useMemo(() => {
    if (rangeStartIndex === null || rangeEndIndex === null) return null
    const startIndex = Math.min(rangeStartIndex, rangeEndIndex)
    const endIndex = Math.max(rangeStartIndex, rangeEndIndex)
    const start = chartData[startIndex]
    const end = chartData[endIndex]
    return {
      startIndex,
      endIndex,
      startDate: start.date,
      endDate: end.date,
      startLabel: start.dateStr,
      endLabel: end.dateStr,
    }
  }, [rangeStartIndex, rangeEndIndex, chartData])

  const activeRangeTopic = useMemo(() => {
    if (!selectedRange) return null
    const rangeStart = selectedRange.startDate
    const rangeEnd = selectedRange.endDate
    let bestTopic: EventTopicSummary | null = null
    let bestOverlap = 0
    let bestShare = 0

    for (const topic of topicMap) {
      const start = new Date(topic.window_start).getTime()
      const end = new Date(topic.window_end).getTime()
      const overlap = Math.max(0, Math.min(rangeEnd, end) - Math.max(rangeStart, start))
      if (overlap <= 0) continue
      if (overlap > bestOverlap || (overlap === bestOverlap && topic.share_of_posts > bestShare)) {
        bestOverlap = overlap
        bestShare = topic.share_of_posts
        bestTopic = topic
      }
    }

    return bestTopic
  }, [selectedRange, topicMap])

  const percent =
    chartData.length > 1 ? (clampedIndex / (chartData.length - 1)) * 100 : 0

  // Calculate price range for Y-axis
  const priceValues = prices.map((p) => p.price)
  const minPrice = Math.min(...priceValues)
  const maxPrice = Math.max(...priceValues)
  const padding = (maxPrice - minPrice) * 0.1
  const yDomain = [minPrice - padding, maxPrice + padding]

  // Click handler using activeTooltipIndex
  const handleChartClick = useCallback((state: any) => {
    if (!state?.activeTooltipIndex && state?.activeTooltipIndex !== 0) return
    const clickedIndex = state.activeTooltipIndex

    setSelectedIndex(clickedIndex)

    if (rangeStartIndex === null || (rangeStartIndex !== null && rangeEndIndex !== null)) {
      setRangeStartIndex(clickedIndex)
      setRangeEndIndex(null)
    } else {
      setRangeEndIndex(clickedIndex)
    }
  }, [rangeStartIndex, rangeEndIndex])

  // Clear range button handler
  const handleClearRange = useCallback(() => {
    setRangeStartIndex(null)
    setRangeEndIndex(null)
  }, [])

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="pt-6">
          <div className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">
            Stock price over time
          </div>
          <ResponsiveContainer width="100%" height={360}>
            <ComposedChart
              data={chartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              onClick={handleChartClick}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />

            <XAxis
              dataKey="dateStr"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => {
                // Show every 10th date to avoid crowding
                return value
              }}
            />

            <YAxis
              yAxisId="price"
              orientation="left"
              domain={yDomain}
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />

            <YAxis
              yAxisId="volume"
              orientation="right"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${value.toFixed(0)}M`}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || payload.length === 0) return null

                return (
                  <div className="bg-white p-3 border rounded shadow-lg">
                    <p className="text-sm font-medium mb-2">{payload[0].payload.dateStr}</p>
                    <p className="text-sm text-blue-600">
                      Price: ${payload[0].payload.price.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Volume: {payload[0].payload.volume.toFixed(1)}M
                    </p>
                  </div>
                )
              }}
            />

              <Legend />

              {/* Event windows as shaded areas - FIXED to use index */}
              {events.map((event) => {
                const start = new Date(event.window_start).getTime()
                const end = new Date(event.window_end).getTime()

                // Find corresponding indices
                const startDataPoint = chartData.find(d => d.date >= start)
                const endDataPoint = chartData.findLast(d => d.date <= end)

                if (!startDataPoint || !endDataPoint) return null

                return (
                  <ReferenceArea
                    key={event.id}
                    yAxisId="price"
                    x1={startDataPoint.index}  // USE INDEX not timestamp
                    x2={endDataPoint.index}    // USE INDEX not timestamp
                    fill={event.move_pct >= 0 ? '#10b981' : '#ef4444'}
                    fillOpacity={0.1}
                    stroke={event.move_pct >= 0 ? '#10b981' : '#ef4444'}
                    strokeOpacity={0.5}
                    strokeDasharray="3 3"
                  />
                )
              })}

              {/* Selected range - FIXED to use index */}
              {selectedRange && (
                <ReferenceArea
                  yAxisId="price"
                  x1={selectedRange.startIndex}  // NOT startLabel
                  x2={selectedRange.endIndex}    // NOT endLabel
                  fill="#3b82f6"
                  fillOpacity={0.15}
                  stroke="#3b82f6"
                  strokeWidth={2}
                  strokeOpacity={0.6}
                />
              )}

              {/* ReferenceLine - FIXED to use index */}
              <ReferenceLine
                x={clampedIndex}  // USE INDEX not dateStr
                yAxisId="price"
                stroke="#1f2937"
                strokeWidth={2}
                strokeDasharray="4 4"
              />

              <Bar
                yAxisId="volume"
                dataKey="volume"
                fill="#d1d5db"
                opacity={0.3}
                name="Volume (M)"
                isAnimationActive={false}
              />

              <Line
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="Price ($)"
                isAnimationActive={false}  // Disable animations to prevent re-render issues
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">
            Social topic timeline
          </div>
          <div className="relative h-10">
            <div className="absolute left-0 right-0 top-1/2 h-px bg-muted" />
            {topicMap.map((topic) => {
              const start = new Date(topic.window_start).getTime()
              const end = new Date(topic.window_end).getTime()
              const left = getPercentForDate(start)
              const width = Math.max(1, getPercentForDate(end) - left)

              return (
                <div
                  key={topic.event_id}
                  className="absolute top-1/2 h-2 -translate-y-1/2 rounded-full bg-blue-200"
                  style={{ left: `${left}%`, width: `${width}%` }}
                />
              )
            })}
            {/* Visual feedback for range selection with green markers */}
            {selectedRange && (
              <>
                <div
                  className="absolute top-1/2 -translate-y-1/2 h-4 w-4 rounded-full bg-green-500 shadow-md border-2 border-white"
                  style={{ left: `calc(${(selectedRange.startIndex / (chartData.length - 1)) * 100}% - 8px)` }}
                />
                <div
                  className="absolute top-1/2 -translate-y-1/2 h-4 w-4 rounded-full bg-green-500 shadow-md border-2 border-white"
                  style={{ left: `calc(${(selectedRange.endIndex / (chartData.length - 1)) * 100}% - 8px)` }}
                />
              </>
            )}
            <div
              className="absolute top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-blue-600 shadow"
              style={{ left: `calc(${percent}% - 6px)` }}
            />
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Click two points on the price chart to set an analysis range.</span>
            {selectedRange && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearRange}
                className="h-7 text-xs"
              >
                Clear Range
              </Button>
            )}
          </div>
          <div className="flex items-center justify-between text-sm">
            <div className="text-muted-foreground">
              <span className="font-medium text-foreground">{selectedPoint.dateStr}</span>
            </div>
            <div className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              {activeTopic ? activeTopic.topic_label : "No topic"}
            </div>
          </div>
          {selectedRange ? (
            <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
              <div className="text-muted-foreground">
                Selected range:{" "}
                <span className="font-medium text-foreground">
                  {selectedRange.startLabel} to {selectedRange.endLabel}
                </span>
              </div>
              <div className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                {activeRangeTopic ? activeRangeTopic.topic_label : "No topic in range"}
              </div>
            </div>
          ) : null}
          {events.length > 0 && (
            <div className="text-xs text-muted-foreground">
              Bars represent event windows.{" "}
              <span className="text-blue-600">Active dot</span> follows the last clicked timestamp.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
