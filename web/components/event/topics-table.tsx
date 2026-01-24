'use client'

import { Topic } from "@/lib/types"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

interface TopicsTableProps {
  topics: Topic[]
  isEngagementWeighted: boolean
  onToggleEngagementWeight: () => void
  onViewEvidence: (topic: Topic, showCounter?: boolean) => void
}

export function TopicsTable({
  topics,
  isEngagementWeighted,
  onToggleEngagementWeight,
  onViewEvidence,
}: TopicsTableProps) {
  const getSentimentColor = (score: number) => {
    if (score > 0.3) return "text-green-600"
    if (score < -0.3) return "text-red-600"
    return "text-gray-600"
  }

  const getSentimentLabel = (score: number) => {
    if (score > 0.3) return "Positive"
    if (score < -0.3) return "Negative"
    return "Neutral"
  }

  return (
    <div className="space-y-4">
      {/* Engagement Toggle */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="engagement-weight" className="text-sm font-medium cursor-pointer">
                Weight by Engagement
              </Label>
              <p className="text-xs text-muted-foreground mt-1">
                Reweight topics by total post engagement instead of post count
              </p>
            </div>
            <Switch
              id="engagement-weight"
              checked={isEngagementWeighted}
              onCheckedChange={onToggleEngagementWeight}
            />
          </div>
        </CardContent>
      </Card>

      {/* Topics List */}
      <div className="space-y-3">
        {topics.map((topic, index) => (
          <Card key={topic.id} className="hover:shadow-md transition">
            <CardContent className="py-4">
              <div className="flex items-start gap-4">
                {/* Rank Badge */}
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-sm">
                    {index + 1}
                  </div>
                </div>

                {/* Topic Content */}
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-lg mb-2">{topic.topic_label}</h4>

                  <div className="flex flex-wrap gap-1 mb-3">
                    {topic.keywords.map((keyword) => (
                      <Badge key={keyword} variant="outline" className="text-xs">
                        {keyword}
                      </Badge>
                    ))}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground text-xs">Share of Discussion</div>
                      <div className="font-semibold">
                        {(topic.share_of_posts * 100).toFixed(1)}%
                      </div>
                    </div>

                    <div>
                      <div className="text-muted-foreground text-xs">Sentiment</div>
                      <div className={`font-semibold ${getSentimentColor(topic.sentiment_score)}`}>
                        {getSentimentLabel(topic.sentiment_score)} ({topic.sentiment_score.toFixed(2)})
                      </div>
                    </div>

                    <div>
                      <div className="text-muted-foreground text-xs">Evidence</div>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 h-auto font-semibold"
                        onClick={() => onViewEvidence(topic, false)}
                      >
                        {topic.evidence_post_ids.length} posts
                      </Button>
                    </div>

                    <div>
                      <div className="text-muted-foreground text-xs">Counter-Narrative</div>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 h-auto font-semibold text-orange-600 hover:text-orange-700"
                        onClick={() => onViewEvidence(topic, true)}
                      >
                        {topic.counter_post_ids.length} posts
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {topics.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No topics identified for this event
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
