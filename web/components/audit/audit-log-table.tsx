'use client'

import { AuditEntry } from "@/lib/types"
import { formatDateTime, getActionLabel } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

interface AuditLogTableProps {
  entries: AuditEntry[]
}

export function AuditLogTable({ entries }: AuditLogTableProps) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No audit log entries yet. Actions will be logged as you use the platform.
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
            <th className="px-4 py-3 text-left font-medium">Timestamp</th>
            <th className="px-4 py-3 text-left font-medium">Action</th>
            <th className="px-4 py-3 text-left font-medium">Ticker</th>
            <th className="px-4 py-3 text-left font-medium">Event ID</th>
            <th className="px-4 py-3 text-left font-medium">Details</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {sortedEntries.map((entry) => (
            <tr key={entry.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                {formatDateTime(entry.timestamp)}
              </td>
              <td className="px-4 py-3">
                <Badge variant="outline">{getActionLabel(entry.action)}</Badge>
              </td>
              <td className="px-4 py-3 font-medium">
                {entry.ticker || '-'}
              </td>
              <td className="px-4 py-3 text-muted-foreground font-mono text-xs">
                {entry.event_id ? entry.event_id.slice(0, 20) + '...' : '-'}
              </td>
              <td className="px-4 py-3 text-muted-foreground text-xs">
                {entry.details && Object.keys(entry.details).length > 0 ? (
                  <pre className="font-mono">
                    {JSON.stringify(entry.details, null, 2)}
                  </pre>
                ) : (
                  '-'
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
