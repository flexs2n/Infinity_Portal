import { api } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { notFound } from "next/navigation"
import { formatDate, formatPercent } from "@/lib/utils"
import { ConfidenceMeter } from "@/components/event/confidence-meter"
import { TopicsTable } from "@/components/event/topics-table"
import { TransparencyPanel } from "@/components/event/transparency-panel"
import { ExportButton } from "@/components/event/export-button"
import { Badge } from "@/components/ui/badge"
import { EventDetailClient } from "@/components/event/event-detail-client"
import { NarrativePanel } from "@/components/event/narrative-panel"

interface EventDetailPageProps {
  params: {
    ticker: string
    id: string
  }
}

export default async function EventDetailPage({ params }: EventDetailPageProps) {
  const ticker = params.ticker.toUpperCase()
  const eventId = params.id

  try {
    const eventDetail = await api.getEventDetail(ticker, eventId)
    const { event, topics, posts, confidence } = eventDetail

    const isPositive = event.move_pct >= 0

    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Breadcrumb */}
        <div className="mb-6">
          <Link href="/">
            <Button variant="ghost" size="sm" className="mr-2">
              ← Dashboard
            </Button>
          </Link>
          <Link href={`/ticker/${ticker}`}>
            <Button variant="ghost" size="sm">
              {ticker}
            </Button>
          </Link>
        </div>

        {/* Event Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <h1 className="text-3xl font-bold">{ticker}</h1>
                <Badge variant={isPositive ? "default" : "destructive"} className="text-lg">
                  {formatPercent(event.move_pct)}
                </Badge>
              </div>
              <h2 className="text-xl text-muted-foreground mb-2">{event.headline}</h2>
              <p className="text-sm text-muted-foreground">
                {formatDate(event.window_start)} to {formatDate(event.window_end)} •{' '}
                Volatility Z-score: {event.vol_z.toFixed(1)}
              </p>
            </div>

            <ExportButton event={event} topics={topics} />
          </div>

          {/* Confidence Assessment */}
          <ConfidenceMeter confidence={confidence} />
        </div>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Topics Table (2 columns on large screens) */}
          <div className="lg:col-span-2">
            <h3 className="text-xl font-semibold mb-4">Evidence-Based Narratives</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Topics identified from social media discussions during the event window. Click on
              evidence counts to view supporting posts.
            </p>

            <EventDetailClient topics={topics} posts={posts} />
          </div>

          {/* Right: Narrative + Transparency */}
          <div className="lg:col-span-1 space-y-6">
            <NarrativePanel event={event} />
            <TransparencyPanel event={event} topics={topics} posts={posts} />
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error loading event detail:', error)
    notFound()
  }
}
