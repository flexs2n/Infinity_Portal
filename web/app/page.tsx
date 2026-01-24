import { api } from "@/lib/api-client"
import { InstrumentCard } from "@/components/dashboard/instrument-card"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Suspense } from "react"

async function DashboardContent() {
  const instruments = await api.getInstruments()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Advisor Evidence Dashboard</h1>
        <p className="text-muted-foreground">
          A defensible narrative workflow for wealth advisors and compliance teams.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {instruments.map((instrument) => (
          <InstrumentCard key={instrument.ticker} instrument={instrument} />
        ))}
      </div>

      <div className="mt-12 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Client Dashboard</CardTitle>
              <CardDescription>Portfolio value, charted moves, and key events.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              Build a clean client-facing view while preserving the advisor-grade details in the
              evidence workflow.
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Narrative Workspace</CardTitle>
              <CardDescription>Time-windowed explanation tied to price moves.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              Hide the raw mess; surface a concise narrative with citations and confidence signals.
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Compliance-Ready Output</CardTitle>
              <CardDescription>Defensible record for advisor communications.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              Client-safe summaries, exportable memos, and an audit trail for oversight.
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Data Sources</CardTitle>
              <CardDescription>Multi-stream context for each price move.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <ul className="list-disc list-inside space-y-1">
                <li>Social stream signals (static dataset)</li>
                <li>News intelligence summaries</li>
                <li>Company fundamentals and earnings</li>
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Time Horizon Control</CardTitle>
              <CardDescription>Adjust story depth by zoom level.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>Switch between market, sector, and stock views.</p>
              <p>Short-term narratives emphasize signals; long-term narratives favor fundamentals.</p>
            </CardContent>
          </Card>
        </div>

        <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg text-sm text-muted-foreground">
          <p className="font-medium text-foreground mb-2">
            Important: This is NOT investment advice. Analysis shows correlation, not causation.
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>All data from static historical datasets (no live scraping)</li>
            <li>Evidence panels show supporting and counter-narratives</li>
            <li>Client-safe mode hides sensitive information for presentations</li>
            <li>All actions logged in audit trail for compliance</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {[1, 2].map((i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  )
}
