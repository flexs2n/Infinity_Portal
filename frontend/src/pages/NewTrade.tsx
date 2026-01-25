import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Plus, Rocket, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { tradingApi } from '@/services/api';

const popularStocks = [
  'NVDA',
  'AAPL',
  'MSFT',
  'GOOGL',
  'AMZN',
  'META',
  'TSLA',
  'AMD',
];

const strategyTypes = [
  { value: 'momentum', label: 'Momentum' },
  { value: 'value', label: 'Value Investing' },
  { value: 'growth', label: 'Growth' },
  { value: 'swing', label: 'Swing Trading' },
  { value: 'scalping', label: 'Scalping' },
];

export function NewTrade() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [stocks, setStocks] = useState<string[]>([]);
  const [stockInput, setStockInput] = useState('');
  const [task, setTask] = useState('');
  const [allocation, setAllocation] = useState('');
  const [riskLevel, setRiskLevel] = useState([5]);
  const [strategyType, setStrategyType] = useState('');

  const addStock = (stock: string) => {
    const upperStock = stock.toUpperCase().trim();
    if (upperStock && !stocks.includes(upperStock)) {
      setStocks([...stocks, upperStock]);
      setStockInput('');
    }
  };

  const removeStock = (stock: string) => {
    setStocks(stocks.filter((s) => s !== stock));
  };

  const handleStockInputKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addStock(stockInput);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (stocks.length === 0) {
      setError('Please add at least one stock');
      return;
    }
    if (task.length < 10) {
      setError('Task description must be at least 10 characters');
      return;
    }
    if (!allocation || parseFloat(allocation) <= 0) {
      setError('Please enter a valid allocation amount');
      return;
    }

    setIsLoading(true);

    try {
      const response = await tradingApi.createTrade({
        stocks,
        task,
        allocation: parseFloat(allocation),
        strategy_type: strategyType || undefined,
        risk_level: riskLevel[0],
      });

      navigate(`/trade/${response.id}`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to create trade. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Create New Trade Analysis
        </h1>
        <p className="text-muted-foreground">
          Configure your AI-powered trade analysis
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Trade Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Display */}
            {error && (
              <div className="rounded-md bg-danger/10 p-3 text-sm text-danger">
                {error}
              </div>
            )}

            {/* Stocks Selection */}
            <div className="space-y-2">
              <Label htmlFor="stocks">Select Stocks *</Label>
              <div className="flex gap-2">
                <Input
                  id="stocks"
                  placeholder="Enter stock symbol (e.g., NVDA)"
                  value={stockInput}
                  onChange={(e) => setStockInput(e.target.value)}
                  onKeyDown={handleStockInputKeyDown}
                />
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => addStock(stockInput)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              {/* Selected Stocks */}
              {stocks.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {stocks.map((stock) => (
                    <span
                      key={stock}
                      className="inline-flex items-center gap-1 rounded-md bg-primary/10 px-2.5 py-1 text-sm font-medium text-primary"
                    >
                      {stock}
                      <button
                        type="button"
                        onClick={() => removeStock(stock)}
                        className="hover:text-primary/70"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Popular Stocks */}
              <div className="mt-2">
                <p className="text-xs text-muted-foreground mb-2">
                  Popular stocks:
                </p>
                <div className="flex flex-wrap gap-1">
                  {popularStocks.map((stock) => (
                    <button
                      key={stock}
                      type="button"
                      onClick={() => addStock(stock)}
                      disabled={stocks.includes(stock)}
                      className="rounded bg-surface-light px-2 py-1 text-xs text-muted-foreground hover:bg-surface-light/80 hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {stock}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Trading Task */}
            <div className="space-y-2">
              <Label htmlFor="task">Trading Task *</Label>
              <Textarea
                id="task"
                placeholder="Describe your trading analysis task (e.g., Analyze NVIDIA for AI growth potential with $50,000 allocation)"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                className="min-h-[100px]"
              />
              <p className="text-xs text-muted-foreground">
                Minimum 10 characters. Be specific about your analysis goals.
              </p>
            </div>

            {/* Allocation Amount */}
            <div className="space-y-2">
              <Label htmlFor="allocation">Allocation Amount ($) *</Label>
              <Input
                id="allocation"
                type="number"
                placeholder="50000"
                value={allocation}
                onChange={(e) => setAllocation(e.target.value)}
                min="1"
                step="1000"
              />
            </div>

            {/* Risk Level */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Risk Level</Label>
                <span className="text-sm font-mono text-muted-foreground">
                  {riskLevel[0]}/10
                </span>
              </div>
              <Slider
                value={riskLevel}
                onValueChange={setRiskLevel}
                min={1}
                max={10}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Conservative</span>
                <span>Aggressive</span>
              </div>
            </div>

            {/* Strategy Type */}
            <div className="space-y-2">
              <Label htmlFor="strategy">Strategy Type (Optional)</Label>
              <Select value={strategyType} onValueChange={setStrategyType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategyTypes.map((strategy) => (
                    <SelectItem key={strategy.value} value={strategy.value}>
                      {strategy.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(-1)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
                className="flex-1 gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Rocket className="h-4 w-4" />
                    Run Analysis
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
