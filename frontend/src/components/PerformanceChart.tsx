import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsList, TabsTrigger } from './ui/tabs';
import { useState } from 'react';

interface DataPoint {
  date: string;
  portfolio: number;
  benchmark: number;
}

// Generate sample data for demo purposes
const generateSampleData = (days: number): DataPoint[] => {
  const data: DataPoint[] = [];
  let portfolioValue = 100;
  let benchmarkValue = 100;

  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);

    // Random daily returns
    portfolioValue *= 1 + (Math.random() - 0.48) * 0.03;
    benchmarkValue *= 1 + (Math.random() - 0.49) * 0.02;

    data.push({
      date: date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      portfolio: parseFloat(portfolioValue.toFixed(2)),
      benchmark: parseFloat(benchmarkValue.toFixed(2)),
    });
  }

  return data;
};

const timeRanges = [
  { label: '7D', days: 7 },
  { label: '30D', days: 30 },
  { label: '90D', days: 90 },
  { label: '1Y', days: 365 },
];

export function PerformanceChart() {
  const [selectedRange, setSelectedRange] = useState(30);
  const data = generateSampleData(selectedRange);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base font-medium">
          Performance Overview
        </CardTitle>
        <Tabs
          value={selectedRange.toString()}
          onValueChange={(v) => setSelectedRange(parseInt(v))}
        >
          <TabsList className="h-8">
            {timeRanges.map((range) => (
              <TabsTrigger
                key={range.days}
                value={range.days.toString()}
                className="text-xs px-2"
              >
                {range.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 5, right: 5, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#27272a"
                vertical={false}
              />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#13131a',
                  border: '1px solid #27272a',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
                labelStyle={{ color: '#9ca3af' }}
                itemStyle={{ color: '#f9fafb' }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                formatter={(value) => (
                  <span style={{ color: '#9ca3af', fontSize: '12px' }}>
                    {value}
                  </span>
                )}
              />
              <Line
                type="monotone"
                dataKey="portfolio"
                name="Portfolio"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#3b82f6' }}
              />
              <Line
                type="monotone"
                dataKey="benchmark"
                name="S&P 500"
                stroke="#6b7280"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                activeDot={{ r: 4, fill: '#6b7280' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
