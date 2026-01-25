import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  BarChart2,
  MessageSquare,
  AlertTriangle,
  ClipboardList,
  Target,
  TrendingUp,
  TrendingDown,
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
  formatCurrencyDetailed,
  formatDateTime
} from '@/utils/formatters';
import { cn } from '@/utils/cn';
import type { TradeStatus } from '@/types';

const statusConfig: Record<
  TradeStatus,
  { label: string; variant: 'pending' | 'executing' | 'completed' | 'failed' }
> = {
  pending: { label: 'Pending', variant: 'pending' },
  executing: { label: 'Executing', variant: 'executing' },
  completed: { label: 'Completed', variant: 'completed' },
  failed: { label: 'Failed', variant: 'failed' },
};

const analysisIcons: Record<string, React.ElementType> = {
  trading_thesis: FileText,
  quantitative_analysis: BarChart2,
  sentiment_analysis: MessageSquare,
  risk_assessment: AlertTriangle,
  execution_order: ClipboardList,
  final_decision: Target,
};

const analysisLabels: Record<string, string> = {
  trading_thesis: 'Trading Director Thesis',
  quantitative_analysis: 'Quantitative Analysis',
  sentiment_analysis: 'Sentiment Analysis',
  risk_assessment: 'Risk Assessment',
  execution_order: 'Execution Order',
  final_decision: 'Final Decision',
};

export function TradeDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentTrade, isLoading, fetchTrade } = useStore();
  const [expandedSections, setExpandedSections] = useState<string[]>([
    'trading_thesis',
  ]);

  useEffect(() => {
    if (id) {
      fetchTrade(id);
    }
  }, [id, fetchTrade]);

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

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            {currentTrade.task.stocks.map((stock) => (
              <span
                key={stock}
                className="inline-flex items-center rounded-lg bg-primary/10 px-3 py-1.5 text-lg font-bold text-primary"
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

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Confidence Score */}
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground mb-2">
              Confidence Score
            </p>
            <div className="flex items-center gap-3">
              <div className="relative h-12 w-12">
                <svg className="h-12 w-12 -rotate-90" viewBox="0 0 36 36">
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
                    className="stroke-primary"
                    strokeWidth="3"
                    strokeDasharray={`${confidence} 100`}
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-xs font-bold">
                  {confidence}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Decision */}
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground mb-2">Decision</p>
            <div
              className={cn(
                'flex items-center gap-2 text-xl font-bold',
                action === 'BUY' && 'text-success',
                action === 'SELL' && 'text-danger',
                action === 'HOLD' && 'text-warning'
              )}
            >
              {action === 'BUY' && <TrendingUp className="h-5 w-5" />}
              {action === 'SELL' && <TrendingDown className="h-5 w-5" />}
              {action === 'HOLD' && <Target className="h-5 w-5" />}
              {action}
            </div>
          </CardContent>
        </Card>

        {/* Allocation */}
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground mb-2">Allocation</p>
            <p className="text-xl font-bold font-mono">
              {formatCurrency(currentTrade.task.allocation)}
            </p>
          </CardContent>
        </Card>

        {/* Risk Level */}
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground mb-2">Risk Level</p>
            <p className="text-xl font-bold">
              {currentTrade.task.risk_level || 5}/10
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Key Metrics */}
      {(result.entry_price || result.stop_loss || result.take_profit) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Key Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {result.entry_price && (
                <div>
                  <p className="text-sm text-muted-foreground">Entry Price</p>
                  <p className="font-mono font-medium">
                    {formatCurrencyDetailed(result.entry_price)}
                  </p>
                </div>
              )}
              {result.stop_loss && (
                <div>
                  <p className="text-sm text-muted-foreground">Stop Loss</p>
                  <p className="font-mono font-medium text-danger">
                    {formatCurrencyDetailed(result.stop_loss)}
                  </p>
                </div>
              )}
              {result.take_profit && (
                <div>
                  <p className="text-sm text-muted-foreground">Take Profit</p>
                  <p className="font-mono font-medium text-success">
                    {formatCurrencyDetailed(result.take_profit)}
                  </p>
                </div>
              )}
              {result.position_size && (
                <div>
                  <p className="text-sm text-muted-foreground">Position Size</p>
                  <p className="font-mono font-medium">
                    {result.position_size} shares
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Sections */}
      {analysisSections.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">AI Agent Analysis</CardTitle>
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
                  <AccordionItem key={section.key} value={section.key}>
                    <AccordionTrigger className="hover:no-underline">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-light">
                          <Icon className="h-4 w-4 text-primary" />
                        </div>
                        <span>{section.label}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="pl-11 pr-4 text-sm text-muted-foreground whitespace-pre-wrap">
                        {section.content}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          </CardContent>
        </Card>
      )}

      {/* Task Description */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Task Description</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{currentTrade.task.task}</p>
        </CardContent>
      </Card>

      {/* Raw Data */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Raw Response Data</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="overflow-auto rounded-lg bg-surface p-4 text-xs text-muted-foreground max-h-96">
            {JSON.stringify(currentTrade.result, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
