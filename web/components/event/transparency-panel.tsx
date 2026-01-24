import { Event, Topic, Post } from "@/lib/types"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { formatDate } from "@/lib/utils"

interface TransparencyPanelProps {
  event: Event
  topics: Topic[]
  posts: Post[]
}

export function TransparencyPanel({ event, topics, posts }: TransparencyPanelProps) {
  return (
    <Card className="sticky top-4">
      <CardHeader>
        <CardTitle className="text-lg">Why am I seeing this?</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div>
          <h4 className="font-semibold mb-2">Data Sources</h4>
          <p className="text-muted-foreground">
            This analysis uses a static historical dataset of social media posts (Twitter/X). No
            live scraping or external API calls are made.
          </p>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Time Window Match</h4>
          <p className="text-muted-foreground mb-1">
            Event window: {formatDate(event.window_start)} to {formatDate(event.window_end)}
          </p>
          <p className="text-muted-foreground">
            All posts and topics are from this date range. The window was selected based on
            significant price movement ({event.move_pct >= 0 ? '+' : ''}{event.move_pct.toFixed(1)}%) and elevated discussion volume ({event.vol_z.toFixed(1)}σ above baseline).
          </p>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Topic Clustering</h4>
          <p className="text-muted-foreground">
            Topics were identified using NLP entity extraction and keyword clustering. Each cluster represents a distinct theme in the discussion.
          </p>
          <ul className="list-disc list-inside text-muted-foreground mt-2 space-y-1">
            <li>{topics.length} topics identified</li>
            <li>{posts.length} posts analyzed</li>
            <li>Coverage threshold: {(topics.reduce((sum, t) => sum + t.share_of_posts, 0) * 100).toFixed(0)}% of discussion</li>
          </ul>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Evidence vs Counter-Narratives</h4>
          <p className="text-muted-foreground">
            Evidence posts support or discuss the topic neutrally. Counter-narratives express
            opposing views or negative sentiment. Both are shown to provide balanced analysis.
          </p>
        </div>

        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
          <h4 className="font-semibold mb-2 text-xs">Important Limitations</h4>
          <ul className="list-disc list-inside text-xs text-muted-foreground space-y-1">
            <li>Correlation does not imply causation</li>
            <li>Social media ≠ institutional trading</li>
            <li>Sentiment analysis may contain errors</li>
            <li>This is NOT investment advice</li>
          </ul>
        </div>

        <div className="p-3 bg-blue-50 border border-blue-200 rounded">
          <h4 className="font-semibold mb-2 text-xs">For Compliance Teams</h4>
          <p className="text-xs text-muted-foreground">
            All user actions are logged in the audit trail. Client-safe mode available for
            presentations. Export feature generates markdown memos with disclaimers.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
