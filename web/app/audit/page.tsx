'use client'

import { useState, useEffect } from "react"
import { AuditLogTable } from "@/components/audit/audit-log-table"
import { ExportHistoryTable } from "@/components/audit/export-history-table"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { getAuditLog, exportAuditLog, clearAuditLog } from "@/lib/audit-logger"
import Link from "next/link"

export default function AuditPage() {
  const [auditLog, setAuditLog] = useState<any[]>([])
  const [exportHistory, setExportHistory] = useState<any[]>([])

  useEffect(() => {
    // Load audit log
    setAuditLog(getAuditLog())

    // Load export history
    const history = JSON.parse(localStorage.getItem('export_history') || '[]')
    setExportHistory(history)
  }, [])

  const handleExportAuditLog = () => {
    exportAuditLog()
  }

  const handleClearAuditLog = () => {
    if (confirm('Are you sure you want to clear the audit log? This cannot be undone.')) {
      clearAuditLog()
      setAuditLog([])
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <Link href="/">
          <Button variant="ghost" className="mb-4">
            ← Back to Dashboard
          </Button>
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Audit Log</h1>
            <p className="text-muted-foreground">
              Track all user actions for compliance and recordkeeping
            </p>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleExportAuditLog} variant="outline">
              Export as JSON
            </Button>
            <Button onClick={handleClearAuditLog} variant="destructive">
              Clear Log
            </Button>
          </div>
        </div>
      </div>

      <Tabs defaultValue="audit" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="audit">Audit Log ({auditLog.length})</TabsTrigger>
          <TabsTrigger value="exports">Export History ({exportHistory.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="audit" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>User Actions</CardTitle>
              <CardDescription>
                All actions are logged locally in your browser's localStorage for compliance
                tracking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AuditLogTable entries={auditLog} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="exports" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Memo Export History</CardTitle>
              <CardDescription>
                Track all exported markdown memos for client presentations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ExportHistoryTable entries={exportHistory} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">About the Audit Log</h2>
        <div className="text-sm text-muted-foreground space-y-2">
          <p>
            The audit log tracks all user interactions with the platform for compliance and
            recordkeeping purposes.
          </p>
          <p className="font-medium text-foreground">
            Logged actions include:
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>Viewed events and evidence panels</li>
            <li>Toggled client-safe mode</li>
            <li>Changed weighting preferences</li>
            <li>Exported memos for client presentations</li>
          </ul>
          <p className="mt-4">
            All data is stored locally in your browser. Export the audit log as JSON to preserve
            records or share with compliance teams.
          </p>
        </div>
      </div>
    </div>
  )
}
