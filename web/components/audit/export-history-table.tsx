'use client'

import { formatDateTime } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

interface ExportHistoryEntry {
  timestamp: string
  ticker: string
  event_id: string
  filename: string
}

interface ExportHistoryTableProps {
  entries: ExportHistoryEntry[]
}

export function ExportHistoryTable({ entries }: ExportHistoryTableProps) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No memos exported yet. Export feature generates downloadable markdown files.
      </div>
    )
  }

  // Reverse to show most recent first
  const sortedEntries = [...entries].reverse()

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Exported At</th>
            <th className="px-4 py-3 text-left font-medium">Ticker</th>
            <th className="px-4 py-3 text-left font-medium">Event ID</th>
            <th className="px-4 py-3 text-left font-medium">Filename</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {sortedEntries.map((entry, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                {formatDateTime(entry.timestamp)}
              </td>
              <td className="px-4 py-3">
                <Badge>{entry.ticker}</Badge>
              </td>
              <td className="px-4 py-3 text-muted-foreground font-mono text-xs">
                {entry.event_id}
              </td>
              <td className="px-4 py-3 font-medium">
                {entry.filename}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
