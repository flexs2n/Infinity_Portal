import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useStore } from '@/store/useStore';

export function Onboarding() {
  const navigate = useNavigate();
  const { createUser, setApiKey, isLoading } = useStore();
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'login'>('create');

  // Form state
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fundName, setFundName] = useState('');
  const [fundDescription, setFundDescription] = useState('');
  const [apiKeyInput, setApiKeyInput] = useState('');

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!username || !email || !fundName) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      await createUser({
        username,
        email,
        fund_name: fundName,
        fund_description: fundDescription || undefined,
      });
      navigate('/dashboard');
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to create account. Please try again.'
      );
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!apiKeyInput.trim()) {
      setError('Please enter your API key');
      return;
    }

    setApiKey(apiKeyInput.trim());
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center">
          <div className="inline-flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
              <span className="text-2xl font-bold text-white">IP</span>
            </div>
            <span className="text-2xl font-bold text-foreground">
              Narrative Alpha
            </span>
          </div>
          <p className="text-muted-foreground">
            AI-Powered Trading Platform
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="flex rounded-lg bg-surface p-1">
          <button
            onClick={() => setMode('create')}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
              mode === 'create'
                ? 'bg-surface-light text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Create Account
          </button>
          <button
            onClick={() => setMode('login')}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
              mode === 'login'
                ? 'bg-surface-light text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Use API Key
          </button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>
              {mode === 'create' ? 'Create Your Fund' : 'Enter API Key'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Error Display */}
            {error && (
              <div className="mb-4 rounded-md bg-danger/10 p-3 text-sm text-danger">
                {error}
              </div>
            )}

            {mode === 'create' ? (
              <form onSubmit={handleCreateAccount} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username *</Label>
                  <Input
                    id="username"
                    placeholder="johndoe"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="john@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fundName">Fund Name *</Label>
                  <Input
                    id="fundName"
                    placeholder="My Trading Fund"
                    value={fundName}
                    onChange={(e) => setFundName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fundDescription">
                    Fund Description (Optional)
                  </Label>
                  <Textarea
                    id="fundDescription"
                    placeholder="A brief description of your trading strategy..."
                    value={fundDescription}
                    onChange={(e) => setFundDescription(e.target.value)}
                    className="min-h-[80px]"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full gap-2"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      Get Started
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="apiKey">API Key</Label>
                  <Input
                    id="apiKey"
                    type="password"
                    placeholder="Enter your API key"
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Your API key was provided when you created your account.
                  </p>
                </div>

                <Button type="submit" className="w-full gap-2">
                  Continue
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
