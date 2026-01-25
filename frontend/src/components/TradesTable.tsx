import { Link } from 'react-router-dom';
import { Eye, Trash2 } from 'lucide-react';
import type { TradeResponse, TradeStatus } from '@/types';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  formatCurrency,
  formatDateTime,
  formatPercent,
} from '@/utils/formatters';
import { cn } from '@/utils/cn';

interface TradesTableProps {
  trades: TradeResponse[];
  onDelete?: (id: string) => void;
  compact?: boolean;
}

const statusConfig: Record<
  TradeStatus,
  { label: string; variant: 'pending' | 'executing' | 'completed' | 'failed' }
> = {
  pending: { label: 'Pending', variant: 'pending' },
  executing: { label: 'Executing', variant: 'executing' },
  completed: { label: 'Completed', variant: 'completed' },
  failed: { label: 'Failed', variant: 'failed' },
};

export function TradesTable({
  trades,
  onDelete,
  compact = false,
}: TradesTableProps) {
  if (trades.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground">No trades found</p>
        <Link to="/trade/new">
          <Button className="mt-4">Create your first trade</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border text-left text-sm text-muted-foreground">
            <th className="pb-3 font-medium">Stocks</th>
            <th className="pb-3 font-medium">Status</th>
            <th className="pb-3 font-medium">Allocation</th>
            {!compact && (
              <>
                <th className="pb-3 font-medium">Performance</th>
                <th className="pb-3 font-medium">Date</th>
              </>
            )}
            <th className="pb-3 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {trades.map((trade) => {
            const status = statusConfig[trade.status];
            const returnPct =
              trade.performance_metrics?.return_percentage;

            return (
              <tr
                key={trade.id}
                className="group hover:bg-surface-light/50 transition-colors"
              >
                <td className="py-4">
                  <div className="flex gap-1.5">
                    {trade.task.stocks.map((stock) => (
                      <span
                        key={stock}
                        className="inline-flex items-center rounded bg-surface-light px-2 py-1 text-sm font-medium text-foreground"
                      >
                        {stock}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="py-4">
                  <Badge variant={status.variant}>{status.label}</Badge>
                </td>
                <td className="py-4 font-mono text-sm">
                  {formatCurrency(trade.task.allocation)}
                </td>
                {!compact && (
                  <>
                    <td className="py-4">
                      {returnPct !== undefined ? (
                        <span
                          className={cn(
                            'font-mono text-sm',
                            returnPct >= 0
                              ? 'text-success'
                              : 'text-danger'
                          )}
                        >
                          {formatPercent(returnPct)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="py-4 text-sm text-muted-foreground">
                      {formatDateTime(trade.created_at)}
                    </td>
                  </>
                )}
                <td className="py-4">
                  <div className="flex items-center justify-end gap-2">
                    <Link to={`/trade/${trade.id}`}>
                      <Button variant="ghost" size="icon">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </Link>
                    {onDelete && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onDelete(trade.id)}
                        className="text-muted-foreground hover:text-danger"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
