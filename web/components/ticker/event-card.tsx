import { Event } from "@/lib/types"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { formatDate, formatPercent } from "@/lib/utils"

interface EventCardProps {
  event: Event
}

export function EventCard({ event }: EventCardProps) {
  const isPositive = event.move_pct >= 0

  return (
    <Card className="hover:shadow-md transition">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant={isPositive ? "default" : "destructive"}>
                {formatPercent(event.move_pct)}
              </Badge>
              <Badge variant="outline">
                Z-score: {event.vol_z.toFixed(1)}
              </Badge>
            </div>
            <CardTitle className="text-lg">{event.headline}</CardTitle>
            <CardDescription>
              {formatDate(event.window_start)} to {formatDate(event.window_end)}
            </CardDescription>
          </div>

          <Link href={`/ticker/${event.ticker}/event/${event.id}`}>
            <Button>View Evidence</Button>
          </Link>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Price Movement</div>
            <div className={`font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(event.move_pct, 2)}
            </div>
          </div>

          <div>
            <div className="text-muted-foreground">Volatility</div>
            <div className="font-semibold">
              {event.vol_z.toFixed(1)}σ
            </div>
          </div>

          <div>
            <div className="text-muted-foreground">Duration</div>
            <div className="font-semibold">
              {Math.ceil(
                (new Date(event.window_end).getTime() - new Date(event.window_start).getTime()) /
                  (1000 * 60 * 60 * 24)
              )}{' '}
              days
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
