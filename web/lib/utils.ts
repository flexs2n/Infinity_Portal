import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { AuditAction } from "./types"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

export function formatPercent(value: number, decimals: number = 1): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value)
}

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
