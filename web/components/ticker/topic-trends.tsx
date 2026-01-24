'use client'

import { TopicTrendSeries } from "@/lib/types"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface TopicTrendsProps {
  trends: TopicTrendSeries[]
}

export function TopicTrends({ trends }: TopicTrendsProps) {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/1f6bd708-b261-4564-82d5-7a5e8cafc675',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'topic-trends.tsx:13',message:'TopicTrends render',data:{trendCount:trends.length},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H2'})}).catch(()=>{});
  // #endregion
  if (trends.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Topic Trends</CardTitle>
        </CardHeader>
        <CardContent className="text-center py-8 text-muted-foreground">
          No topic trend data available
        </CardContent>
      </Card>
    )
  }

  // Color palette for different topics
  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Topic Trends (Weekly Impressions)</CardTitle>
        <p className="text-sm text-muted-foreground">
          Engagement momentum by topic over time. Impressions = total social media engagement.
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trends.map((series, index) => {
            const color = colors[index % colors.length]

            // Transform data for Recharts
            const chartData = series.points.map(point => ({
              week: new Date(point.week_start).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
              }),
              impressions: point.impressions,
            }))

            // Calculate total impressions for this topic
            const totalImpressions = series.points.reduce(
              (sum, p) => sum + p.impressions,
              0
            )
            // #region agent log
            if (index === 0) {
              fetch('http://127.0.0.1:7242/ingest/1f6bd708-b261-4564-82d5-7a5e8cafc675',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'topic-trends.tsx:56',message:'Topic series prepared',data:{label:series.topic_label,points:series.points.length,totalImpressions},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H1'})}).catch(()=>{});
            }
            // #endregion

            return (
              <div key={series.topic_label} className="space-y-2">
                <div className="flex items-baseline justify-between">
                  <h4 className="text-sm font-semibold truncate" title={series.topic_label}>
                    {series.topic_label}
                  </h4>
                  <span className="text-xs text-muted-foreground ml-2 flex-shrink-0">
                    {Math.round(totalImpressions).toLocaleString()}
                  </span>
                </div>

                <ResponsiveContainer width="100%" height={120}>
                  <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                      dataKey="week"
                      tick={{ fontSize: 10 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tick={{ fontSize: 10 }}
                      tickFormatter={(value) => {
                        if (value >= 1000) return `${(value / 1000).toFixed(1)}k`
                        return value.toString()
                      }}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (!active || !payload || payload.length === 0) return null
                        return (
                          <div className="bg-white p-2 border rounded shadow-lg text-xs">
                            <p className="font-medium">{payload[0].payload.week}</p>
                            <p style={{ color }}>
                              {Math.round(payload[0].value as number).toLocaleString()} impressions
                            </p>
                          </div>
                        )
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="impressions"
                      stroke={color}
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )
          })}
        </div>

        <div className="mt-6 text-xs text-muted-foreground p-3 bg-blue-50 border border-blue-200 rounded">
          <strong>Methodology:</strong> Topic trends show weekly engagement volume (likes + reposts + replies)
          for each discussion theme. Higher impressions indicate greater social media attention during that week.
          Evidence suggests these patterns may correlate with price movements, but correlation does not imply causation.
        </div>
      </CardContent>
    </Card>
  )
}
