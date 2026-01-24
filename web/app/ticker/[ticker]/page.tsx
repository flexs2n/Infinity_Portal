import { api } from "@/lib/api-client"
import { PriceChart } from "@/components/ticker/price-chart"
import { TopicTrends } from "@/components/ticker/topic-trends"
import { EventCard } from "@/components/ticker/event-card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { notFound } from "next/navigation"

interface TickerPageProps {
  params: {
    ticker: string
  }
}

export default async function TickerPage({ params }: TickerPageProps) {
  const ticker = params.ticker.toUpperCase()

  try {
    // Fetch ticker data
    const [instruments, prices, events, topicMap, topicTrends] = await Promise.all([
      api.getInstruments(),
      api.getPriceSeries(ticker),
      api.getEvents(ticker),
      api.getTopicMap(ticker),
      api.getTopicTrends(ticker),
    ])

    const instrument = instruments.find((i) => i.ticker === ticker)
    if (!instrument) {
      notFound()
    }

    return (
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              ← Back to Dashboard
            </Button>
          </Link>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">{ticker}</h1>
              <p className="text-xl text-muted-foreground">{instrument.name}</p>
            </div>

            {prices.length > 0 && (
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Current Price</div>
                <div className="text-3xl font-bold">
                  ${prices[prices.length - 1].price.toFixed(2)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Price Chart */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Price History</h2>
          <PriceChart prices={prices} events={events} topicMap={topicMap} />
        </div>

        <div className="mb-12">
          <TopicTrends trends={topicTrends} />
        </div>

        {/* Events Timeline */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Movement Events</h2>
          <p className="text-muted-foreground mb-6">
            Events represent periods with significant price movements and social media discussion
          </p>

          <div className="space-y-4">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>

          {events.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              No events found for this ticker
            </div>
          )}
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error loading ticker page:', error)
    notFound()
  }
}
