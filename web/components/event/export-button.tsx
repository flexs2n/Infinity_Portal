'use client'

import { useState } from "react"
import { Event, Topic } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { api, downloadMarkdown } from "@/lib/api-client"
import { logAuditAction } from "@/lib/audit-logger"
import { useClientSafe } from "@/lib/client-safe-context"

interface ExportButtonProps {
  event: Event
  topics: Topic[]
}

export function ExportButton({ event, topics }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  const { isClientSafe } = useClientSafe()

  const handleExport = async () => {
    setIsExporting(true)

    try {
      const response = await api.exportMemo({
        event_id: event.id,
        ticker: event.ticker,
        selected_topics: undefined, // Export all topics
        include_counter_narratives: true,
      })

      // Download the markdown file
      downloadMarkdown(response.markdown, response.filename)

      // Log to audit
      logAuditAction('exported_memo', {
        ticker: event.ticker,
        event_id: event.id,
        filename: response.filename,
        client_safe_mode: isClientSafe,
      })

      // Store export history in localStorage
      const history = JSON.parse(localStorage.getItem('export_history') || '[]')
      history.push({
        timestamp: new Date().toISOString(),
        ticker: event.ticker,
        event_id: event.id,
        filename: response.filename,
      })
      localStorage.setItem('export_history', JSON.stringify(history.slice(-50))) // Keep last 50
    } catch (error) {
      console.error('Export failed:', error)
      alert('Failed to export memo. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Button
      onClick={handleExport}
      disabled={isExporting}
      size="lg"
    >
      {isExporting ? 'Exporting...' : 'Export Memo'}
    </Button>
  )
}
