"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatDate, formatPercent } from "@/lib/utils"
import type { Event } from "@/lib/types"

interface NarrativePanelProps {
  event: Event
}

const horizons = [
  {
    value: "short",
    label: "Short term",
    title: "Stock-level narrative",
    detail:
      "Emphasize the immediate catalysts and social/news chatter tied to the event window.",
    focus: "Stock"
  },
  {
    value: "medium",
    label: "Medium term",
    title: "Sector-level narrative",
    detail:
      "Bridge the event to sector rotation and competitive signals while keeping the timeline tight.",
    focus: "Sector"
  },
  {
    value: "long",
    label: "Long term",
    title: "Market-level narrative",
    detail:
      "Prioritize fundamentals and earnings context; social signals become supporting evidence.",
    focus: "Market"
  }
]

export function NarrativePanel({ event }: NarrativePanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Advisory Narrative</CardTitle>
        <CardDescription>
          Client-safe summary with evidence links and a defensible record.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm text-muted-foreground">
        <div className="rounded-md border bg-muted/40 p-3 text-foreground">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Event summary</div>
          <div className="mt-1 text-sm font-medium">
            {event.ticker} moved {formatPercent(event.move_pct)} from{" "}
            {formatDate(event.window_start)} to {formatDate(event.window_end)}.
          </div>
          <div className="mt-1 text-sm">{event.headline}</div>
        </div>

        <Tabs defaultValue="short">
          <TabsList className="w-full justify-between">
            {horizons.map((horizon) => (
              <TabsTrigger key={horizon.value} value={horizon.value} className="flex-1">
                {horizon.label}
              </TabsTrigger>
            ))}
          </TabsList>
          {horizons.map((horizon) => (
            <TabsContent key={horizon.value} value={horizon.value} className="space-y-2">
              <div className="text-sm font-semibold text-foreground">{horizon.title}</div>
              <div>{horizon.detail}</div>
              <div className="text-xs uppercase tracking-wide text-muted-foreground">
                Narrative focus: {horizon.focus}
              </div>
            </TabsContent>
          ))}
        </Tabs>

        <div className="space-y-2">
          <div className="text-sm font-semibold text-foreground">Evidence sources</div>
          <ul className="list-disc list-inside space-y-1">
            <li>Social stream signals (static dataset)</li>
            <li>News intelligence summaries</li>
            <li>Company fundamentals and earnings</li>
          </ul>
        </div>

        <div className="rounded-md border border-dashed p-3 text-xs text-muted-foreground">
          Delivery-ready: client portal summaries, voice-ready briefing, and RAG-backed citations.
        </div>
      </CardContent>
    </Card>
  )
}
