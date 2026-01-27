import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Plus, Rocket, TrendingUp, TrendingDown, Target, Brain, Check, Loader2, Sparkles, ExternalLink, PartyPopper } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

// Stock groups - when user adds one, recommend related ones
const stockGroups: Record<string, { name: string; stocks: string[]; description: string }> = {
  'NVDA': { name: 'AI & Semiconductors', stocks: ['AMD', 'INTC', 'AVGO', 'QCOM', 'TSM', 'MRVL'], description: 'Companies in the AI chip race' },
  'AMD': { name: 'AI & Semiconductors', stocks: ['NVDA', 'INTC', 'AVGO', 'QCOM', 'TSM', 'MRVL'], description: 'Companies in the AI chip race' },
  'INTC': { name: 'Semiconductors', stocks: ['NVDA', 'AMD', 'AVGO', 'QCOM', 'TSM'], description: 'Chip manufacturers' },
  'AAPL': { name: 'Big Tech', stocks: ['MSFT', 'GOOGL', 'AMZN', 'META'], description: 'Tech giants dominating the market' },
  'MSFT': { name: 'Big Tech', stocks: ['AAPL', 'GOOGL', 'AMZN', 'META'], description: 'Tech giants dominating the market' },
  'GOOGL': { name: 'Big Tech', stocks: ['AAPL', 'MSFT', 'AMZN', 'META'], description: 'Tech giants dominating the market' },
  'AMZN': { name: 'Big Tech & E-Commerce', stocks: ['AAPL', 'MSFT', 'GOOGL', 'META', 'SHOP'], description: 'Tech and retail giants' },
  'META': { name: 'Social Media & Tech', stocks: ['AAPL', 'MSFT', 'GOOGL', 'SNAP', 'PINS'], description: 'Social platforms and tech' },
  'TSLA': { name: 'EV & Clean Energy', stocks: ['RIVN', 'LCID', 'NIO', 'F', 'GM'], description: 'Electric vehicle companies' },
  'RIVN': { name: 'EV & Clean Energy', stocks: ['TSLA', 'LCID', 'NIO', 'F', 'GM'], description: 'Electric vehicle market' },
  'JPM': { name: 'Banking & Finance', stocks: ['BAC', 'WFC', 'GS', 'MS', 'C'], description: 'Major financial institutions' },
  'BAC': { name: 'Banking & Finance', stocks: ['JPM', 'WFC', 'GS', 'MS', 'C'], description: 'Major financial institutions' },
  'V': { name: 'Payments & Fintech', stocks: ['MA', 'PYPL', 'SQ', 'COIN'], description: 'Payment processing companies' },
  'MA': { name: 'Payments & Fintech', stocks: ['V', 'PYPL', 'SQ', 'COIN'], description: 'Payment processing companies' },
  'JNJ': { name: 'Healthcare', stocks: ['PFE', 'UNH', 'ABBV', 'MRK', 'LLY'], description: 'Pharmaceutical and healthcare' },
  'PFE': { name: 'Pharma', stocks: ['JNJ', 'MRNA', 'ABBV', 'MRK', 'LLY'], description: 'Pharmaceutical companies' },
  'XOM': { name: 'Energy & Oil', stocks: ['CVX', 'COP', 'SLB', 'OXY', 'BP'], description: 'Oil and energy sector' },
  'CVX': { name: 'Energy & Oil', stocks: ['XOM', 'COP', 'SLB', 'OXY', 'BP'], description: 'Oil and energy sector' },
  'LMT': { name: 'Defense & Aerospace', stocks: ['RTX', 'NOC', 'BA', 'GD', 'LHX'], description: 'Defense contractors' },
  'RTX': { name: 'Defense & Aerospace', stocks: ['LMT', 'NOC', 'BA', 'GD', 'LHX'], description: 'Defense contractors' },
  'BA': { name: 'Aerospace', stocks: ['LMT', 'RTX', 'NOC', 'GE', 'HON'], description: 'Aerospace and defense' },
  'DIS': { name: 'Entertainment', stocks: ['NFLX', 'WBD', 'PARA', 'CMCSA'], description: 'Media and entertainment' },
  'NFLX': { name: 'Streaming', stocks: ['DIS', 'WBD', 'PARA', 'ROKU'], description: 'Streaming services' },
  'WMT': { name: 'Retail', stocks: ['COST', 'TGT', 'HD', 'LOW'], description: 'Retail giants' },
  'COST': { name: 'Retail', stocks: ['WMT', 'TGT', 'HD', 'LOW'], description: 'Retail and wholesale' },
};

// Quick presets
const quickPresets = [
  { name: 'Magnificent 7', stocks: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'], emoji: '🌟' },
  { name: 'AI Leaders', stocks: ['NVDA', 'AMD', 'MSFT', 'GOOGL'], emoji: '🤖' },
  { name: 'Safe Bets', stocks: ['AAPL', 'JNJ', 'JPM', 'V', 'PG'], emoji: '🛡️' },
  { name: 'Growth Stocks', stocks: ['TSLA', 'NVDA', 'AMD', 'SHOP'], emoji: '📈' },
];

// Preset allocation amounts
const allocationPresets = [
  { label: '$10K', value: 10000 },
  { label: '$25K', value: 25000 },
  { label: '$50K', value: 50000 },
  { label: '$100K', value: 100000 },
];

interface TradeSummary {
  action: string;
  confidence: number;
  stocks: string[];
  entry_price?: string;
}

interface StreamMessage {
  type: 'status' | 'reasoning' | 'complete' | 'error';
  message: string;
  agent?: string;
  progress?: number;
  trade_id?: string;
  summary?: TradeSummary;
}

export function NewTrade() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const streamRef = useRef<HTMLDivElement>(null);

  // Form state
  const [stocks, setStocks] = useState<string[]>([]);
  const [stockInput, setStockInput] = useState('');
  const [allocation, setAllocation] = useState<number>(50000);

  // Streaming state
  const [streamMessages, setStreamMessages] = useState<StreamMessage[]>([]);
  const [progress, setProgress] = useState(0);
  const [currentAgent, setCurrentAgent] = useState('');
  
  // Completion state
  const [isComplete, setIsComplete] = useState(false);
  const [completedTradeId, setCompletedTradeId] = useState<string | null>(null);
  const [tradeSummary, setTradeSummary] = useState<TradeSummary | null>(null);

  // Recommended stocks based on selection
  const [recommendations, setRecommendations] = useState<{ name: string; stocks: string[]; description: string } | null>(null);

  // Update recommendations when stocks change
  useEffect(() => {
    if (stocks.length > 0) {
      const lastStock = stocks[stocks.length - 1];
      const group = stockGroups[lastStock];
      if (group) {
        setRecommendations({
          name: group.name,
          stocks: group.stocks.filter(s => !stocks.includes(s)),
          description: group.description,
        });
      } else {
        setRecommendations(null);
      }
    } else {
      setRecommendations(null);
    }
  }, [stocks]);

  // Auto-scroll stream messages
  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [streamMessages]);

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

  const handleStockInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addStock(stockInput);
    }
  };

  const applyPreset = (preset: { stocks: string[] }) => {
    setStocks(preset.stocks);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (stocks.length === 0) {
      setError('Please add at least one stock');
      return;
    }

    setIsLoading(true);
    setStreamMessages([]);
    setProgress(0);

    const apiKey = localStorage.getItem('api_key');
    if (!apiKey) {
      setError('Not authenticated');
      setIsLoading(false);
      return;
    }

    const stockList = stocks.join(', ');
    const autoTask = `Perform comprehensive AI-powered analysis on ${stockList} with a $${allocation.toLocaleString()} allocation. Analyze market trends, technical indicators, sentiment, and provide actionable trading recommendations.`;

    try {
      const response = await fetch('/api/trades/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({
          stocks,
          task: autoTask,
          allocation,
          risk_level: 5,
          strategy_type: 'momentum',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Stream not available');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamMessage = JSON.parse(line.slice(6));

              setStreamMessages(prev => [...prev, data]);

              if (data.progress) {
                setProgress(data.progress);
              }

                              if (data.agent) {
                                setCurrentAgent(data.agent);
                              }
                              
                              // Capture trade_id from any message (enables "Skip to Report")
                              if (data.trade_id && !completedTradeId) {
                                setCompletedTradeId(data.trade_id);
                              }

                              if (data.type === 'complete' && data.trade_id) {
                                setCompletedTradeId(data.trade_id);
                                setIsComplete(true);
                                if (data.summary) {
                                  setTradeSummary(data.summary);
                                }
                              }

              if (data.type === 'error') {
                setError(data.message);
                setIsLoading(false);
              }
            } catch {
              // Ignore parse errors
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setIsLoading(false);
    }
  };

  // Loading screen with streaming updates
  if (isLoading) {
    // Completion screen - "Tada!"
    if (isComplete && tradeSummary && completedTradeId) {
      const actionColors = {
        BUY: 'text-success',
        SELL: 'text-danger',
        HOLD: 'text-warning',
      };
      const ActionIcon = tradeSummary.action === 'BUY' ? TrendingUp : tradeSummary.action === 'SELL' ? TrendingDown : Target;
      
      return (
        <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto mb-4">
                <div className="relative">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-success/20 to-accent/20 flex items-center justify-center animate-pulse">
                    <PartyPopper className="h-12 w-12 text-success" />
                  </div>
                  <Sparkles className="absolute -top-2 -right-2 h-8 w-8 text-accent animate-bounce" />
                </div>
              </div>
              <CardTitle className="text-2xl">Tada! Analysis Complete</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Our AI has finished analyzing your portfolio
              </p>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Summary Card */}
              <div className="p-6 rounded-xl bg-gradient-to-br from-surface to-surface-light border border-primary/20">
                <div className="text-center space-y-4">
                  <p className="text-sm text-muted-foreground uppercase tracking-wide">AI Recommendation</p>
                  
                  <div className={`flex items-center justify-center gap-3 text-4xl font-bold ${actionColors[tradeSummary.action as keyof typeof actionColors] || 'text-foreground'}`}>
                    <ActionIcon className="h-10 w-10" />
                    <span>{tradeSummary.action}</span>
                  </div>
                  
                  <div className="flex items-center justify-center gap-2 text-xl">
                    {tradeSummary.stocks.map((stock) => (
                      <span
                        key={stock}
                        className="inline-flex items-center rounded-lg bg-primary/10 px-4 py-2 font-bold text-primary"
                      >
                        {stock}
                      </span>
                    ))}
                  </div>
                  
                  {tradeSummary.entry_price && (
                    <p className="text-lg">
                      Entry Price: <span className="font-mono font-bold text-foreground">${tradeSummary.entry_price}</span>
                    </p>
                  )}
                  
                  <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                    <span>Confidence:</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-24 bg-surface-light rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${tradeSummary.confidence >= 70 ? 'bg-success' : tradeSummary.confidence >= 40 ? 'bg-warning' : 'bg-danger'}`}
                          style={{ width: `${tradeSummary.confidence}%` }}
                        />
                      </div>
                      <span className="font-mono font-bold">{tradeSummary.confidence}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-3">
                <Button
                  size="lg"
                  className="w-full gap-2 h-14 text-lg"
                  onClick={() => navigate(`/narrative/${completedTradeId}`)}
                >
                  <ExternalLink className="h-5 w-5" />
                  View Full Narrative & Analysis
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setIsLoading(false);
                    setIsComplete(false);
                    setCompletedTradeId(null);
                    setTradeSummary(null);
                    setStreamMessages([]);
                    setProgress(0);
                  }}
                  className="w-full"
                >
                  Analyze Another Stock
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }
    
    // In-progress loading screen
    return (
      <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto mb-4">
              <div className="relative">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
                  <Brain className="h-10 w-10 text-primary animate-pulse" />
                </div>
                <Sparkles className="absolute -top-1 -right-1 h-6 w-6 text-accent animate-bounce" />
              </div>
            </div>
            <CardTitle className="text-xl">AI Analysis in Progress</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Analyzing {stocks.join(', ')} with ${allocation.toLocaleString()} allocation
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Progress bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{currentAgent || 'Initializing...'}</span>
                <span className="font-mono text-primary">{progress}%</span>
              </div>
              <div className="h-2 bg-surface-light rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Streaming messages */}
            <div
              ref={streamRef}
              className="h-64 overflow-y-auto rounded-lg bg-surface p-4 space-y-3"
            >
              {streamMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex gap-3 text-sm animate-fadeIn ${msg.type === 'reasoning' ? 'pl-4 border-l-2 border-accent/50' : ''
                    }`}
                >
                  {msg.type === 'status' && (
                    <div className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
                      {progress === 100 ? (
                        <Check className="h-3 w-3 text-success" />
                      ) : (
                        <Loader2 className="h-3 w-3 text-primary animate-spin" />
                      )}
                    </div>
                  )}
                  <div className="flex-1">
                    {msg.agent && (
                      <span className="font-medium text-accent">{msg.agent}: </span>
                    )}
                    <span className={msg.type === 'reasoning' ? 'text-muted-foreground italic' : 'text-foreground'}>
                      {msg.message}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Proceed to Narrative button */}
            {completedTradeId && (
              <Button
                variant="outline"
                className="w-full gap-2"
                onClick={() => navigate(`/narrative/${completedTradeId}`)}
              >
                <ExternalLink className="h-4 w-4" />
                Proceed to Narrative
              </Button>
            )}

            <p className="text-xs text-center text-muted-foreground">
              Our AI agents are working together to provide you with comprehensive analysis.
              This typically takes 1-3 minutes.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Page Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 mb-4">
          <TrendingUp className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold text-foreground">AI Trade Analysis</h1>
        <p className="text-muted-foreground mt-2">
          Pick stocks, set your budget — AI does the rest
        </p>
      </div>

      {/* Quick Presets */}
      <div className="flex flex-wrap justify-center gap-2">
        {quickPresets.map((preset) => (
          <Button
            key={preset.name}
            type="button"
            variant="outline"
            size="sm"
            onClick={() => applyPreset(preset)}
            className="gap-2"
          >
            <span>{preset.emoji}</span>
            {preset.name}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">What would you like to analyze?</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="rounded-md bg-danger/10 p-3 text-sm text-danger">
                {error}
              </div>
            )}

            {/* Stock Input */}
            <div className="space-y-3">
              <Label>Enter a stock symbol</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="e.g., AAPL, NVDA, TSLA..."
                  value={stockInput}
                  onChange={(e) => setStockInput(e.target.value.toUpperCase())}
                  onKeyDown={handleStockInputKeyDown}
                  className="text-lg font-mono"
                />
                <Button type="button" variant="secondary" onClick={() => addStock(stockInput)}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                💡 Tip: Enter any stock symbol from the US market (NYSE, NASDAQ)
              </p>
            </div>

            {/* Selected Stocks */}
            {stocks.length > 0 && (
              <div className="p-4 rounded-xl bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/10">
                <p className="text-sm font-medium text-foreground mb-3">
                  📊 Your portfolio ({stocks.length} stock{stocks.length > 1 ? 's' : ''}):
                </p>
                <div className="flex flex-wrap gap-2">
                  {stocks.map((stock) => (
                    <span
                      key={stock}
                      className="inline-flex items-center gap-2 rounded-lg bg-primary/10 px-4 py-2 text-base font-bold text-primary"
                    >
                      {stock}
                      <button
                        type="button"
                        onClick={() => removeStock(stock)}
                        className="hover:text-primary/70 transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Smart Recommendations */}
            {recommendations && recommendations.stocks.length > 0 && (
              <div className="p-4 rounded-xl bg-surface-light border border-border/50">
                <p className="text-sm font-medium text-foreground mb-1">
                  💡 Related stocks: <span className="text-primary">{recommendations.name}</span>
                </p>
                <p className="text-xs text-muted-foreground mb-3">{recommendations.description}</p>
                <div className="flex flex-wrap gap-2">
                  {recommendations.stocks.slice(0, 6).map((stock) => (
                    <button
                      key={stock}
                      type="button"
                      onClick={() => addStock(stock)}
                      className="rounded-lg px-3 py-1.5 text-sm bg-background hover:bg-primary/10 hover:text-primary transition-all border border-border/50"
                    >
                      + {stock}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Allocation */}
            <div className="space-y-3">
              <Label>How much would you like to invest?</Label>
              <div className="grid grid-cols-4 gap-2">
                {allocationPresets.map((preset) => (
                  <button
                    key={preset.value}
                    type="button"
                    onClick={() => setAllocation(preset.value)}
                    className={`py-3 px-4 rounded-lg text-sm font-medium transition-all ${allocation === preset.value
                        ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25'
                        : 'bg-surface-light text-muted-foreground hover:bg-surface-light/80 hover:text-foreground'
                      }`}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground text-sm">Custom amount:</span>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                  <Input
                    type="number"
                    value={allocation}
                    onChange={(e) => setAllocation(parseFloat(e.target.value) || 0)}
                    min="1000"
                    step="1000"
                    className="w-32 pl-7 text-right font-mono"
                  />
                </div>
              </div>
            </div>

            {/* Submit */}
            <Button
              type="submit"
              disabled={stocks.length === 0}
              className="w-full gap-2 h-14 text-lg"
              size="lg"
            >
              <Rocket className="h-5 w-5" />
              Analyze with AI
            </Button>

            <Button type="button" variant="ghost" onClick={() => navigate(-1)} className="w-full">
              Cancel
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
