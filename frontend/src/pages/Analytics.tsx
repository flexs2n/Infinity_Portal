import { useEffect, useState } from 'react';
import {
  TrendingUp,
  // TrendingDown,
  Activity,
  Target,
  DollarSign,
  BarChart3,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useStore } from '@/store/useStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PerformanceChart } from '@/components/PerformanceChart';
import { LoadingSkeleton } from '@/components/ui/loading';
import { formatCurrency, formatPercent } from '@/utils/formatters';
import { cn } from '@/utils/cn';

const timeRanges = [
  { label: '7D', days: 7 },
  { label: '30D', days: 30 },
  { label: '90D', days: 90 },
  { label: '1Y', days: 365 },
];

// Sample data for charts
const stockPerformanceData = [
  { name: 'NVDA', value: 28.5, trades: 12 },
  { name: 'AAPL', value: 15.2, trades: 8 },
  { name: 'MSFT', value: 12.8, trades: 6 },
  { name: 'GOOGL', value: -5.3, trades: 4 },
  { name: 'AMZN', value: 8.7, trades: 5 },
];

const tradeDistributionData = [
  { name: 'Completed', value: 85, color: '#10b981' },
  { name: 'Executing', value: 8, color: '#3b82f6' },
  { name: 'Pending', value: 5, color: '#f59e0b' },
  { name: 'Failed', value: 2, color: '#ef4444' },
];

export function Analytics() {
  const { analytics, isLoading, fetchAnalytics } = useStore();
  const [selectedRange, setSelectedRange] = useState(30);

  useEffect(() => {
    fetchAnalytics(selectedRange);
  }, [fetchAnalytics, selectedRange]);

  const metrics = [
    {
      title: 'Total Return',
      value: formatPercent(analytics?.average_return || 0),
      icon: TrendingUp,
      color:
        (analytics?.average_return || 0) >= 0
          ? 'text-success'
          : 'text-danger',
    },
    {
      title: 'Sharpe Ratio',
      value: (analytics?.risk_adjusted_return || 0).toFixed(2),
      icon: Activity,
      color: 'text-primary',
    },
    {
      title: 'Win Rate',
      value: `${(analytics?.success_rate || 0).toFixed(1)}%`,
      icon: Target,
      color: 'text-success',
    },
    {
      title: 'Total Volume',
      value: formatCurrency(analytics?.total_allocation || 0),
      icon: DollarSign,
      color: 'text-warning',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground">
            Historical performance analysis
          </p>
        </div>
        <Tabs
          value={selectedRange.toString()}
          onValueChange={(v) => setSelectedRange(parseInt(v))}
        >
          <TabsList>
            {timeRanges.map((range) => (
              <TabsTrigger key={range.days} value={range.days.toString()}>
                {range.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
          : metrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <Card key={metric.title}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          {metric.title}
                        </p>
                        <p
                          className={cn(
                            'text-2xl font-bold font-mono',
                            metric.color
                          )}
                        >
                          {metric.value}
                        </p>
                      </div>
                      <div
                        className={cn(
                          'flex h-10 w-10 items-center justify-center rounded-lg bg-surface-light',
                          metric.color
                        )}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
      </div>

      {/* Performance Chart */}
      <PerformanceChart />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stock Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Top Performing Stocks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={stockPerformanceData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#27272a"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    stroke="#6b7280"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="#6b7280"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#13131a',
                      border: '1px solid #27272a',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => [
                      `${value.toFixed(1)}%`,
                      'Return',
                    ]}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {stockPerformanceData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.value >= 0 ? '#10b981' : '#ef4444'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Trade Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Trade Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={tradeDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {tradeDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#13131a',
                      border: '1px solid #27272a',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => [`${value}%`, 'Percentage']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            {/* Legend */}
            <div className="flex flex-wrap justify-center gap-4 mt-4">
              {tradeDistributionData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-muted-foreground">
                    {item.name} ({item.value}%)
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Stocks Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Stock Performance Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border text-left text-sm text-muted-foreground">
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Trades</th>
                  <th className="pb-3 font-medium">Avg Return</th>
                  <th className="pb-3 font-medium">Win Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {stockPerformanceData.map((stock) => (
                  <tr key={stock.name}>
                    <td className="py-3">
                      <span className="font-medium text-foreground">
                        {stock.name}
                      </span>
                    </td>
                    <td className="py-3 text-muted-foreground">
                      {stock.trades}
                    </td>
                    <td className="py-3">
                      <span
                        className={cn(
                          'font-mono',
                          stock.value >= 0 ? 'text-success' : 'text-danger'
                        )}
                      >
                        {formatPercent(stock.value)}
                      </span>
                    </td>
                    <td className="py-3 text-muted-foreground">
                      {(50 + Math.random() * 40).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
