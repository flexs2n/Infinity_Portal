'use client'

import { useState, useEffect } from "react"
import { Topic, Post } from "@/lib/types"
import { TopicsTable } from "./topics-table"
import { EvidencePanel } from "./evidence-panel"
import { logAuditAction } from "@/lib/audit-logger"

interface EventDetailClientProps {
  topics: Topic[]
  posts: Post[]
}

export function EventDetailClient({ topics: initialTopics, posts }: EventDetailClientProps) {
  const [topics, setTopics] = useState(initialTopics)
  const [isEngagementWeighted, setIsEngagementWeighted] = useState(false)
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null)
  const [evidencePanelOpen, setEvidencePanelOpen] = useState(false)
  const [showCounterNarratives, setShowCounterNarratives] = useState(false)

  // Recalculate topic shares when engagement weighting changes
  useEffect(() => {
    if (isEngagementWeighted) {
      // Build post engagement map
      const postEngagement = posts.reduce((map, post) => {
        map[post.id] = post.engagement
        return map
      }, {} as Record<string, number>)

      // Calculate engagement-weighted shares
      const topicsWithEngagement = initialTopics.map((topic) => {
        const allPostIds = [...topic.evidence_post_ids, ...topic.counter_post_ids]
        const totalEngagement = allPostIds.reduce(
          (sum, id) => sum + (postEngagement[id] || 0),
          0
        )
        return { topic, engagement: totalEngagement }
      })

      const totalEngagement = topicsWithEngagement.reduce(
        (sum, t) => sum + t.engagement,
        0
      )

      const reweighted = topicsWithEngagement.map(({ topic, engagement }) => ({
        ...topic,
        share_of_posts: totalEngagement > 0 ? engagement / totalEngagement : topic.share_of_posts,
      }))

      // Re-sort by share
      reweighted.sort((a, b) => b.share_of_posts - a.share_of_posts)

      setTopics(reweighted)
    } else {
      setTopics(initialTopics)
    }
  }, [isEngagementWeighted, initialTopics, posts])

  const handleViewEvidence = (topic: Topic, showCounter: boolean = false) => {
    setSelectedTopic(topic)
    setShowCounterNarratives(showCounter)
    setEvidencePanelOpen(true)
    logAuditAction('opened_evidence', {
      ticker: topic.ticker,
      topic_id: topic.id,
      counter_narratives: showCounter,
    })
  }

  return (
    <>
      <TopicsTable
        topics={topics}
        isEngagementWeighted={isEngagementWeighted}
        onToggleEngagementWeight={() => {
          const newValue = !isEngagementWeighted
          setIsEngagementWeighted(newValue)
          logAuditAction('weighted_by_engagement', { enabled: newValue })
        }}
        onViewEvidence={handleViewEvidence}
      />

      <EvidencePanel
        open={evidencePanelOpen}
        onOpenChange={setEvidencePanelOpen}
        topic={selectedTopic}
        posts={posts}
        showCounterNarratives={showCounterNarratives}
      />
    </>
  )
}
