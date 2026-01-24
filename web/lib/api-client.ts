/**
 * API client for communicating with FastAPI backend
 */

import {
  Instrument,
  PricePoint,
  Event,
  EventDetail,
  EventTopicSummary,
  TopicTrendSeries,
  ExportRequest,
  ExportResponse,
} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new APIError(response.status, errorText || `HTTP ${response.status}`)
  }

  return response.json()
}

export const api = {
  /**
   * Get all available instruments
   */
  getInstruments: async (): Promise<Instrument[]> => {
    return fetchAPI<Instrument[]>('/instruments')
  },

  /**
   * Get price series for a ticker
   */
  getPriceSeries: async (
    ticker: string,
    start?: string,
    end?: string
  ): Promise<PricePoint[]> => {
    const params = new URLSearchParams()
    if (start) params.append('start', start)
    if (end) params.append('end', end)

    const query = params.toString() ? `?${params.toString()}` : ''
    return fetchAPI<PricePoint[]>(`/ticker/${ticker}/series${query}`)
  },

  /**
   * Get all events for a ticker
   */
  getEvents: async (ticker: string): Promise<Event[]> => {
    return fetchAPI<Event[]>(`/ticker/${ticker}/events`)
  },

  /**
   * Get detailed information for a specific event
   */
  getEventDetail: async (ticker: string, eventId: string): Promise<EventDetail> => {
    return fetchAPI<EventDetail>(`/ticker/${ticker}/event/${eventId}`)
  },

  /**
   * Get top topic per event window for timeline labeling
   */
  getTopicMap: async (ticker: string): Promise<EventTopicSummary[]> => {
    return fetchAPI<EventTopicSummary[]>(`/ticker/${ticker}/topic-map`)
  },

  /**
   * Get weekly topic trend series for a ticker
   */
  getTopicTrends: async (ticker: string): Promise<TopicTrendSeries[]> => {
    return fetchAPI<TopicTrendSeries[]>(`/ticker/${ticker}/topic-trends`)
  },

  /**
   * Export event analysis as markdown memo
   */
  exportMemo: async (request: ExportRequest): Promise<ExportResponse> => {
    return fetchAPI<ExportResponse>('/export', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },
}

/**
 * Download markdown content as a file
 */
export function downloadMarkdown(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()

  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
