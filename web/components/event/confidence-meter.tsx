import { ConfidenceMetrics } from "@/lib/types"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

interface ConfidenceMeterProps {
  confidence: ConfidenceMetrics
}

export function ConfidenceMeter({ confidence }: ConfidenceMeterProps) {
  const getBarColor = (value: number) => {
    if (value >= 70) return "bg-green-500"
    if (value >= 40) return "bg-yellow-500"
    return "bg-red-500"
  }

  const metrics = [
    {
      label: "Coverage",
      value: confidence.coverage,
      description: "Post volume vs baseline activity",
    },
    {
      label: "Sentiment Coherence",
      value: confidence.sentiment_coherence,
      description: "Agreement across topics",
    },
    {
      label: "Recency",
      value: confidence.recency,
      description: "Time decay from event date",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Confidence Assessment</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {metrics.map((metric) => (
            <div key={metric.label}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{metric.label}</span>
                <span className="text-sm font-semibold">{metric.value.toFixed(0)}/100</span>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                <div
                  className={`h-2 rounded-full transition-all ${getBarColor(metric.value)}`}
                  style={{ width: `${metric.value}%` }}
                />
              </div>

              <div className="text-xs text-muted-foreground">{metric.description}</div>
            </div>
          ))}

          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <span className="font-semibold">Overall Confidence</span>
              <span className="text-xl font-bold">{confidence.overall.toFixed(0)}/100</span>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-3 mt-2">
              <div
                className={`h-3 rounded-full transition-all ${getBarColor(confidence.overall)}`}
                style={{ width: `${confidence.overall}%` }}
              />
            </div>
          </div>

          <div className="text-xs text-muted-foreground mt-4 p-3 bg-blue-50 rounded border border-blue-200">
            <strong>Note:</strong> Confidence metrics assess data quality and reliability, not
            investment merit. High confidence indicates robust discussion data, not positive
            investment outlook.
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
