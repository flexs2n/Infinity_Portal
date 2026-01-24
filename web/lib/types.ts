/**
 * TypeScript types matching the FastAPI backend models
 */

export interface Instrument {
  ticker: string
  name: string
}

export interface PricePoint {
  ticker: string
  ts: string
  price: number
  volume: number
}

export interface Event {
  id: string
  ticker: string
  window_start: string
  window_end: string
  move_pct: number
  vol_z: number
  headline: string
}

export interface EventTopicSummary {
  event_id: string
  ticker: string
  window_start: string
  window_end: string
  topic_label: string
  share_of_posts: number
}

export interface TopicTrendPoint {
  week_start: string
  impressions: number
}

export interface TopicTrendSeries {
  topic_label: string
  points: TopicTrendPoint[]
}

export interface Topic {
  id: string
  ticker: string
  window_start: string
  window_end: string
  topic_label: string
  keywords: string[]
  share_of_posts: number
  sentiment_score: number
  evidence_post_ids: string[]
  counter_post_ids: string[]
}

export interface Post {
  id: string
  ts: string
  platform: string
  author_handle: string
  text: string
  url_placeholder: string
  engagement: number
}

export interface ConfidenceMetrics {
  coverage: number
  sentiment_coherence: number
  recency: number
  overall: number
}

export interface EventDetail {
  event: Event
  topics: Topic[]
  posts: Post[]
  confidence: ConfidenceMetrics
}

export interface ExportRequest {
  event_id: string
  ticker: string
  selected_topics?: string[]
  include_counter_narratives: boolean
}

export interface ExportResponse {
  markdown: string
  filename: string
}

// Frontend-specific types

export type AuditAction =
  | 'viewed_event'
  | 'opened_evidence'
  | 'toggled_client_safe'
  | 'weighted_by_engagement'
  | 'exported_memo'

export interface AuditEntry {
  id: string
  timestamp: string
  action: AuditAction
  ticker?: string
  event_id?: string
  details?: Record<string, any>
}
