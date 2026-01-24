'use client'

import { Topic, Post } from "@/lib/types"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { useClientSafe } from "@/lib/client-safe-context"
import { formatDateTime, formatNumber } from "@/lib/utils"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface EvidencePanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  topic: Topic | null
  posts: Post[]
  showCounterNarratives: boolean
}

export function EvidencePanel({
  open,
  onOpenChange,
  topic,
  posts,
  showCounterNarratives,
}: EvidencePanelProps) {
  const { isClientSafe } = useClientSafe()

  if (!topic) return null

  // Filter posts by topic
  const evidencePosts = posts.filter((p) => topic.evidence_post_ids.includes(p.id))
  const counterPosts = posts.filter((p) => topic.counter_post_ids.includes(p.id))

  // Sort by engagement descending
  evidencePosts.sort((a, b) => b.engagement - a.engagement)
  counterPosts.sort((a, b) => b.engagement - a.engagement)

  const renderPost = (post: Post) => {
    const displayHandle = isClientSafe ? '[hidden]' : post.author_handle
    const displayText = isClientSafe
      ? post.text.slice(0, 50) + '...'
      : post.text

    return (
      <div key={post.id} className="p-4 border rounded-lg hover:bg-gray-50 transition">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>@{displayHandle}</span>
            <span>•</span>
            <span>{formatDateTime(post.ts)}</span>
            {!isClientSafe && (
              <>
                <span>•</span>
                <Badge variant="outline" className="text-xs">
                  {post.platform}
                </Badge>
              </>
            )}
          </div>

          <Badge variant="secondary" className="text-xs">
            {formatNumber(post.engagement)} engagement
          </Badge>
        </div>

        <p className="text-sm mb-2">{displayText}</p>

        {isClientSafe && (
          <div className="text-xs text-muted-foreground">
            Post ID: {post.id}
          </div>
        )}

        {!isClientSafe && (
          <div className="text-xs text-muted-foreground">
            <a
              href={post.url_placeholder}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              View original →
            </a>
          </div>
        )}
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{topic.topic_label}</DialogTitle>
          <DialogDescription>
            Social media posts associated with this topic
          </DialogDescription>
        </DialogHeader>

        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {topic.keywords.map((keyword) => (
              <Badge key={keyword} variant="outline">
                {keyword}
              </Badge>
            ))}
          </div>
        </div>

        <Tabs defaultValue={showCounterNarratives ? "counter" : "evidence"} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="evidence">
              Evidence ({evidencePosts.length})
            </TabsTrigger>
            <TabsTrigger value="counter">
              Counter-Narrative ({counterPosts.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="evidence" className="mt-4 space-y-3">
            {evidencePosts.length > 0 ? (
              evidencePosts.map(renderPost)
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No evidence posts available
              </div>
            )}

            {isClientSafe && evidencePosts.length > 0 && (
              <div className="text-xs text-muted-foreground p-3 bg-yellow-50 border border-yellow-200 rounded">
                <strong>Client-Safe Mode:</strong> Handles and full text hidden. Post IDs can be
                used to reference original sources.
              </div>
            )}
          </TabsContent>

          <TabsContent value="counter" className="mt-4 space-y-3">
            {counterPosts.length > 0 ? (
              counterPosts.map(renderPost)
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No counter-narrative posts available
              </div>
            )}

            <div className="text-xs text-muted-foreground p-3 bg-orange-50 border border-orange-200 rounded">
              <strong>Counter-Narratives:</strong> These posts express contrasting views or
              negative sentiment on the topic. Including counter-evidence demonstrates balanced
              analysis.
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
