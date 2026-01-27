import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  BarChart2,
  MessageSquare,
  AlertTriangle,
  ClipboardList,
  Target,
  TrendingUp,
  TrendingDown,
  Brain,
  Sparkles,
  ChevronRight,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { LoadingSkeleton } from '@/components/ui/loading';
import {
  formatCurrency,
  formatDateTime
} from '@/utils/formatters';
import { cn } from '@/utils/cn';
import type { TradeStatus } from '@/types';

const statusConfig: Record<
  TradeStatus,
  { label: string; variant: 'pending' | 'executing' | 'completed' | 'failed' }
> = {
  pending: { label: 'Pending', variant: 'pending' },
  executing: { label: 'Analyzing...', variant: 'executing' },
  completed: { label: 'Complete', variant: 'completed' },
  failed: { label: 'Failed', variant: 'failed' },
};

const analysisIcons: Record<string, React.ElementType> = {
  trading_thesis: Brain,
  quantitative_analysis: BarChart2,
  sentiment_analysis: MessageSquare,
  risk_assessment: AlertTriangle,
  execution_order: ClipboardList,
  final_decision: Target,
};

const analysisLabels: Record<string, string> = {
  trading_thesis: '🎯 Trading Director Analysis',
  quantitative_analysis: '📊 Quantitative Analysis',
  sentiment_analysis: '💬 Market Sentiment',
  risk_assessment: '⚠️ Risk Assessment',
  execution_order: '📋 Trade Execution Plan',
  final_decision: '✅ Final Recommendation',
};

const analysisDescriptions: Record<string, string> = {
  trading_thesis: 'Comprehensive market thesis and trading strategy',
  quantitative_analysis: 'Technical indicators, price levels, and statistical analysis',
  sentiment_analysis: 'News and social media sentiment evaluation',
  risk_assessment: 'Position sizing, stop-loss, and risk management',
  execution_order: 'Specific trade parameters and execution strategy',
  final_decision: 'AI recommendation with confidence scoring',
};

// Format the AI response text for better readability
function formatAnalysisText(text: string): React.ReactNode {
  if (!text) return null;

  // Split by newlines and format
  const lines = text.split('\n');

  return (
    <div className="space-y-3">
      {lines.map((line, index) => {
        const trimmedLine = line.trim();
        if (!trimmedLine) return null;

        // Headers (lines with ** or ending with :)
        if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**')) {
          return (
            <h4 key={index} className="font-semibold text-foreground mt-4 first:mt-0">
              {trimmedLine.replace(/\*\*/g, '')}
            </h4>
          );
        }

        // Bold headers ending with colon
        if (trimmedLine.endsWith(':') && trimmedLine.length < 60) {
          return (
            <h4 key={index} className="font-medium text-foreground/90 mt-3 first:mt-0">
              {trimmedLine}
            </h4>
          );
        }

        // Numbered lists
        if (/^\d+\./.test(trimmedLine)) {
          return (
            <div key={index} className="flex gap-2 pl-2">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>{trimmedLine.replace(/^\d+\.\s*/, '')}</span>
            </div>
          );
        }

        // Bullet points
        if (trimmedLine.startsWith('-') || trimmedLine.startsWith('•') || trimmedLine.startsWith('*')) {
          return (
            <div key={index} className="flex gap-2 pl-2">
              <span className="text-primary">•</span>
              <span>{trimmedLine.replace(/^[-•*]\s*/, '')}</span>
            </div>
          );
        }

        // Key-value pairs (contains : in middle)
        if (trimmedLine.includes(':') && !trimmedLine.endsWith(':')) {
          const [key, ...valueParts] = trimmedLine.split(':');
          const value = valueParts.join(':').trim();
          if (key.length < 40 && value) {
            return (
              <div key={index} className="flex flex-wrap gap-x-2">
                <span className="font-medium text-foreground/80">{key}:</span>
                <span>{value}</span>
              </div>
            );
          }
        }

        // Regular paragraph
        return <p key={index}>{trimmedLine}</p>;
      })}
    </div>
  );
}

export function TradeDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentTrade, isLoading, fetchTrade } = useStore();
  const [expandedSections, setExpandedSections] = useState<string[]>([
    'trading_thesis',
    'final_decision',
  ]);

  useEffect(() => {
    if (id) {
      fetchTrade(id);
    }
  }, [id, fetchTrade]);

  // Poll for updates when trade is still executing
  useEffect(() => {
    if (!currentTrade || currentTrade.status !== 'executing') return;
    
    const interval = setInterval(() => {
      if (id) {
        fetchTrade(id);
      }
    }, 3000); // Poll every 3 seconds
    
    return () => clearInterval(interval);
  }, [currentTrade?.status, id, fetchTrade]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton className="h-10 w-48" />
        <LoadingSkeleton className="h-32 w-full" />
        <LoadingSkeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!currentTrade) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <p className="text-muted-foreground">Trade not found</p>
        <Button onClick={() => navigate('/trades')} className="mt-4">
          Back to Trades
        </Button>
      </div>
    );
  }

  // Show analysis in progress state
  if (currentTrade.status === 'executing') {
    return (
      <div className="space-y-6">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="gap-2 -ml-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>

        <Card className="bg-gradient-to-br from-surface to-surface-light border-primary/10">
          <CardContent className="py-12">
            <div className="flex flex-col items-center text-center space-y-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
                  <Brain className="h-12 w-12 text-primary animate-pulse" />
                </div>
                <div className="absolute -bottom-1 -right-1">
                  <Loader2 className="h-8 w-8 text-accent animate-spin" />
                </div>
              </div>
              
              <div>
                <h2 className="text-2xl font-bold text-foreground">Analysis in Progress</h2>
                <p className="text-muted-foreground mt-2">
                  Our AI agents are analyzing {currentTrade.task.stocks.join(', ')}
                </p>
              </div>

              <div className="flex gap-2">
                {currentTrade.task.stocks.map((stock) => (
                  <span
                    key={stock}
                    className="inline-flex items-center rounded-lg bg-primary/10 px-4 py-2 text-xl font-bold text-primary"
                  >
                    {stock}
                  </span>
                ))}
              </div>

              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>This page will automatically update when analysis is complete</span>
              </div>

              <p className="text-xs text-muted-foreground">
                Analysis typically takes 1-3 minutes. You can leave this page open or come back later.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const status = statusConfig[currentTrade.status];
  const result = currentTrade.result || {};
  const confidence = result.confidence_score || 0;
  const action = result.recommended_action || 'HOLD';

  // Parse analysis sections from result
  const analysisSections = Object.entries(result)
    .filter(([key]) => key in analysisLabels)
    .map(([key, value]) => ({
      key,
      label: analysisLabels[key],
      description: analysisDescriptions[key],
      icon: analysisIcons[key],
      content: typeof value === 'string' ? value : JSON.stringify(value, null, 2),
    }));

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button
        variant="ghost"
        onClick={() => navigate(-1)}
        className="gap-2 -ml-2"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </Button>

      {/* Header with Summary */}
      <Card className="bg-gradient-to-br from-surface to-surface-light border-primary/10">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex gap-2">
                {currentTrade.task.stocks.map((stock) => (
                  <span
                    key={stock}
                    className="inline-flex items-center rounded-lg bg-primary/10 px-4 py-2 text-xl font-bold text-primary"
                  >
                    {stock}
                  </span>
                ))}
              </div>
              <Badge variant={status.variant} className="text-sm">
                {status.label}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {formatDateTime(currentTrade.created_at)}
            </p>
          </div>

          {/* AI Decision Summary */}
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Decision */}
            <div className="p-4 rounded-xl bg-background/50">
              <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">AI Recommendation</p>
              <div
                className={cn(
                  'flex items-center gap-2 text-2xl font-bold',
                  action === 'BUY' && 'text-success',
                  action === 'SELL' && 'text-danger',
                  action === 'HOLD' && 'text-warning'
                )}
              >
                {action === 'BUY' && <TrendingUp className="h-6 w-6" />}
                {action === 'SELL' && <TrendingDown className="h-6 w-6" />}
                {action === 'HOLD' && <Target className="h-6 w-6" />}
                {action}
              </div>
            </div>

            {/* Confidence */}
            <div className="p-4 rounded-xl bg-background/50">
              <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Confidence Level</p>
              <div className="flex items-center gap-3">
                <div className="relative h-10 w-10">
                  <svg className="h-10 w-10 -rotate-90" viewBox="0 0 36 36">
                    <circle
                      cx="18"
                      cy="18"
                      r="16"
                      fill="none"
                      className="stroke-surface-light"
                      strokeWidth="3"
                    />
                    <circle
                      cx="18"
                      cy="18"
                      r="16"
                      fill="none"
                      className={cn(
                        "transition-all",
                        confidence >= 70 ? "stroke-success" : confidence >= 40 ? "stroke-warning" : "stroke-danger"
                      )}
                      strokeWidth="3"
                      strokeDasharray={`${confidence} 100`}
                      strokeLinecap="round"
                    />
                  </svg>
                </div>
                <span className="text-2xl font-bold">{confidence}%</span>
              </div>
            </div>

            {/* Allocation */}
            <div className="p-4 rounded-xl bg-background/50">
              <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Investment Amount</p>
              <p className="text-2xl font-bold font-mono">
                {formatCurrency(currentTrade.task.allocation)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Analysis Sections */}
      {analysisSections.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Sparkles className="h-5 w-5 text-primary" />
              AI Agent Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <Accordion
              type="multiple"
              value={expandedSections}
              onValueChange={setExpandedSections}
            >
              {analysisSections.map((section) => {
                const Icon = section.icon;
                return (
                  <AccordionItem key={section.key} value={section.key} className="border-border/50">
                    <AccordionTrigger className="hover:no-underline py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-accent/10">
                          <Icon className="h-5 w-5 text-primary" />
                        </div>
                        <div className="text-left">
                          <span className="font-medium">{section.label}</span>
                          <p className="text-xs text-muted-foreground font-normal">
                            {section.description}
                          </p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="pl-13 pr-4 pb-2 text-sm text-muted-foreground leading-relaxed">
                        {formatAnalysisText(section.content)}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics if available */}
      {(result.entry_price || result.stop_loss || result.take_profit) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">📈 Key Trading Levels</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {result.entry_price && (
                <div className="p-3 rounded-lg bg-surface-light">
                  <p className="text-xs text-muted-foreground">Entry Price</p>
                  <p className="font-mono font-bold text-lg">${result.entry_price}</p>
                </div>
              )}
              {result.stop_loss && (
                <div className="p-3 rounded-lg bg-danger/10">
                  <p className="text-xs text-muted-foreground">Stop Loss</p>
                  <p className="font-mono font-bold text-lg text-danger">${result.stop_loss}</p>
                </div>
              )}
              {result.take_profit && (
                <div className="p-3 rounded-lg bg-success/10">
                  <p className="text-xs text-muted-foreground">Take Profit</p>
                  <p className="font-mono font-bold text-lg text-success">${result.take_profit}</p>
                </div>
              )}
              {result.position_size && (
                <div className="p-3 rounded-lg bg-surface-light">
                  <p className="text-xs text-muted-foreground">Position Size</p>
                  <p className="font-mono font-bold text-lg">{result.position_size} shares</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Collapsible Raw Data - for advanced users */}
      <details className="group">
        <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2">
          <ChevronRight className="h-4 w-4 transition-transform group-open:rotate-90" />
          View Raw Response Data
        </summary>
        <Card className="mt-2">
          <CardContent className="pt-4">
            <pre className="overflow-auto rounded-lg bg-surface p-4 text-xs text-muted-foreground max-h-64">
              {JSON.stringify(currentTrade.result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </details>
    </div>
  );
}
