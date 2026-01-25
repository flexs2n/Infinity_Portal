import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Filter } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { TradesTable } from '@/components/TradesTable';
import { LoadingSkeleton } from '@/components/ui/loading';
import { tradingApi } from '@/services/api';
import type { TradeStatus } from '@/types';

const PAGE_SIZE = 10;

export function TradesList() {
  const { trades, isLoading, fetchTrades } = useStore();
  const [statusFilter, setStatusFilter] = useState<TradeStatus | 'all'>('all');
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    const params: { skip: number; limit: number; status?: TradeStatus } = {
      skip: currentPage * PAGE_SIZE,
      limit: PAGE_SIZE,
    };

    if (statusFilter !== 'all') {
      params.status = statusFilter;
    }

    fetchTrades(params);
  }, [fetchTrades, statusFilter, currentPage]);

  const handleDeleteTrade = async (id: string) => {
    if (confirm('Are you sure you want to delete this trade?')) {
      await tradingApi.deleteTrade(id);
      fetchTrades({
        skip: currentPage * PAGE_SIZE,
        limit: PAGE_SIZE,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      });
    }
  };

  const handleStatusChange = (value: string) => {
    setStatusFilter(value as TradeStatus | 'all');
    setCurrentPage(0);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Trades</h1>
          <p className="text-muted-foreground">
            View and manage all your trade analyses
          </p>
        </div>
        <Link to="/trade/new">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Trade
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Filter:</span>
            </div>
            <Select value={statusFilter} onValueChange={handleStatusChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="executing">Executing</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Trades Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {statusFilter === 'all'
              ? 'All Trades'
              : `${statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)} Trades`}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array(5)
                .fill(0)
                .map((_, i) => (
                  <LoadingSkeleton key={i} className="h-16 w-full" />
                ))}
            </div>
          ) : (
            <TradesTable trades={trades} onDelete={handleDeleteTrade} />
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {!isLoading && trades.length > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {currentPage * PAGE_SIZE + 1} -{' '}
            {currentPage * PAGE_SIZE + trades.length} trades
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => p + 1)}
              disabled={trades.length < PAGE_SIZE}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
