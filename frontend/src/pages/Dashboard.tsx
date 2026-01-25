import { useEffect } from 'react';
import {
  TrendingUp,
  Target,
  DollarSign,
  BarChart3,
} from 'lucide-react';
import { useStore } from '@/store/useStore';
import { StatCard } from '@/components/StatCard';
import { TradesTable } from '@/components/TradesTable';
import { PerformanceChart } from '@/components/PerformanceChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingSkeleton } from '@/components/ui/loading';
import { formatCurrency, formatPercent } from '@/utils/formatters';
import { tradingApi } from '@/services/api';

export function Dashboard() {
  const { trades, analytics, isLoading, fetchTrades, fetchAnalytics } =
    useStore();

  useEffect(() => {
    fetchTrades({ limit: 5 });
    fetchAnalytics(30);
  }, [fetchTrades, fetchAnalytics]);

  const handleDeleteTrade = async (id: string) => {
    if (confirm('Are you sure you want to delete this trade?')) {
      await tradingApi.deleteTrade(id);
      fetchTrades({ limit: 5 });
    }
  };

  const stats = [
    {
      title: 'Total Trades',
      value: analytics?.total_trades?.toString() || '0',
      change: 12.5,
      icon: BarChart3,
      iconColor: 'text-primary',
    },
    {
      title: 'Success Rate',
      value: analytics
        ? `${analytics.success_rate.toFixed(1)}%`
        : '0%',
      change: 5.2,
      icon: Target,
      iconColor: 'text-success',
    },
    {
      title: 'Total Allocation',
      value: formatCurrency(analytics?.total_allocation || 0),
      change: 8.3,
      icon: DollarSign,
      iconColor: 'text-warning',
    },
    {
      title: 'Avg Return',
      value: formatPercent(analytics?.average_return || 0),
      change: analytics?.average_return || 0,
      icon: TrendingUp,
      iconColor:
        (analytics?.average_return || 0) >= 0
          ? 'text-success'
          : 'text-danger',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your trading performance
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading
          ? Array(4)
              .fill(0)
              .map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <LoadingSkeleton className="h-20 w-full" />
                  </CardContent>
                </Card>
              ))
          : stats.map((stat) => <StatCard key={stat.title} {...stat} />)}
      </div>

      {/* Performance Chart */}
      <PerformanceChart />

      {/* Recent Trades */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">
            Recent Trades
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array(3)
                .fill(0)
                .map((_, i) => (
                  <LoadingSkeleton key={i} className="h-16 w-full" />
                ))}
            </div>
          ) : (
            <TradesTable
              trades={trades.slice(0, 5)}
              onDelete={handleDeleteTrade}
              compact
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
