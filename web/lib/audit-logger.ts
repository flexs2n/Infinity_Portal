/**
 * Audit logging system using localStorage
 */

import { AuditEntry, AuditAction } from './types'

const STORAGE_KEY = 'wealth_mgmt_audit_log'
const MAX_ENTRIES = 500

/**
 * Log an audit action
 */
export function logAuditAction(
  action: AuditAction,
  details: {
    ticker?: string
    event_id?: string
    [key: string]: any
  } = {}
): void {
  if (typeof window === 'undefined') return

  const entry: AuditEntry = {
    id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    action,
    ticker: details.ticker,
    event_id: details.event_id,
    details,
  }

  const log = getAuditLog()
  log.push(entry)

  // Keep only last MAX_ENTRIES
  if (log.length > MAX_ENTRIES) {
    log.splice(0, log.length - MAX_ENTRIES)
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(log))
  } catch (error) {
    console.error('Failed to save audit log:', error)
  }
}

/**
 * Get all audit log entries
 */
export function getAuditLog(): AuditEntry[] {
  if (typeof window === 'undefined') return []

  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Failed to load audit log:', error)
    return []
  }
}

/**
 * Clear all audit log entries
 */
export function clearAuditLog(): void {
  if (typeof window === 'undefined') return

  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('Failed to clear audit log:', error)
  }
}

/**
 * Export audit log as JSON file
 */
export function exportAuditLog(): void {
  const log = getAuditLog()
  const json = JSON.stringify(log, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `audit-log-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()

  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * Get formatted action label for display
 */
export function getActionLabel(action: AuditAction): string {
  const labels: Record<AuditAction, string> = {
    viewed_event: 'Viewed Event',
    opened_evidence: 'Opened Evidence',
    toggled_client_safe: 'Toggled Client-Safe Mode',
    weighted_by_engagement: 'Weighted by Engagement',
    exported_memo: 'Exported Memo',
  }

  return labels[action] || action
}
