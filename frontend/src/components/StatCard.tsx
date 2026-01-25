import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { cn } from '@/utils/cn';

interface StatCardProps {
  title: string;
  value: string;
  change?: number;
  icon: LucideIcon;
  iconColor?: string;
}

export function StatCard({
  title,
  value,
  change,
  icon: Icon,
  iconColor = 'text-primary',
}: StatCardProps) {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold font-mono text-foreground">
              {value}
            </p>
            {change !== undefined && (
              <div
                className={cn(
                  'flex items-center gap-1 text-sm',
                  isPositive && 'text-success',
                  isNegative && 'text-danger',
                  !isPositive && !isNegative && 'text-muted-foreground'
                )}
              >
                {isPositive && <TrendingUp className="h-4 w-4" />}
                {isNegative && <TrendingDown className="h-4 w-4" />}
                <span>
                  {isPositive && '+'}
                  {change.toFixed(1)}%
                </span>
              </div>
            )}
          </div>
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-lg bg-surface-light',
              iconColor
            )}
          >
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
