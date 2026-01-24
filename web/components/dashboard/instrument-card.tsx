import { Instrument } from "@/lib/types"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { api } from "@/lib/api-client"
import { formatPercent } from "@/lib/utils"

interface InstrumentCardProps {
  instrument: Instrument
}

export async function InstrumentCard({ instrument }: InstrumentCardProps) {
  // Fetch events for this ticker
  const events = await api.getEvents(instrument.ticker)
  const recentEvent = events[0]

  // Fetch recent price
  const prices = await api.getPriceSeries(instrument.ticker)
  const latestPrice = prices[prices.length - 1]

  return (
    <Card className="hover:shadow-lg transition">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-2xl">{instrument.ticker}</CardTitle>
            <CardDescription>{instrument.name}</CardDescription>
          </div>
          {latestPrice && (
            <div className="text-right">
              <div className="text-2xl font-bold">
                ${latestPrice.price.toFixed(2)}
              </div>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {recentEvent && (
            <div className="p-3 bg-gray-50 rounded border">
              <div className="text-xs text-muted-foreground mb-1">Most Recent Event</div>
              <div className="text-sm font-medium mb-2">{recentEvent.headline}</div>
              <div className="flex items-center gap-4 text-sm">
                <span className={recentEvent.move_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                  {formatPercent(recentEvent.move_pct)}
                </span>
                <span className="text-muted-foreground">
                  {new Date(recentEvent.window_start).toLocaleDateString()}
                </span>
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <Link href={`/ticker/${instrument.ticker}`} className="flex-1">
              <Button className="w-full" variant="default">
                View Analysis
              </Button>
            </Link>
          </div>

          <div className="text-xs text-muted-foreground">
            {events.length} event{events.length !== 1 ? 's' : ''} available
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
