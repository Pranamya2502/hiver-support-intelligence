import { useState } from 'react'
import {
  Activity,
  Bot,
  CheckCircle2,
  ChevronRight,
  Inbox,
  LogOut,
  MessageSquare,
  Search,
  ShieldCheck,
  Users,
} from 'lucide-react'

type AgentResult = {
  intent: string
  confidence: number
  decision: string
  escalation_reason: string
  draft_reply: string
  historical_evidence: {
    rank: number
    score: number
    customer_text: string
    agent_response: string
  }[]
}

function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const [loginError, setLoginError] = useState('')

  const [message, setMessage] = useState('')
  const [result, setResult] = useState<AgentResult | null>(null)
  const [loading, setLoading] = useState(false)

  const login = async () => {
    setLoginError('')

    if (!email.trim() || !password.trim()) {
      setLoginError('Please enter email and password.')
      return
    }

    setLoginLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (!response.ok) {
        throw new Error('Invalid credentials')
      }

      setLoggedIn(true)
    } catch {
      setLoginError('Invalid email or password.')
    } finally {
      setLoginLoading(false)
    }
  }

  const analyzeMessage = async () => {
    if (!message.trim()) return

    setLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/agent/respond', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_message: message,
        }),
      })

      if (!response.ok) {
        throw new Error('Agent request failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error(error)
      alert('Could not connect to the support agent.')
    } finally {
      setLoading(false)
    }
  }

  if (!loggedIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
        <div className="w-full max-w-md">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600">
              <Bot className="h-6 w-6 text-white" />
            </div>

            <h1 className="text-2xl font-semibold text-slate-900">
              Support Intelligence
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Sign in to your support workspace
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Email
                </label>

                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@hiver.com"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Password
                </label>

                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') login()
                  }}
                  placeholder="Enter your password"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              {loginError && (
                <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
                  {loginError}
                </p>
              )}

              <button
                onClick={login}
                disabled={loginLoading}
                className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
              >
                {loginLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>

            <p className="mt-5 text-center text-xs text-slate-400">
              Support Intelligence · Internal workspace
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="flex h-16 items-center justify-between px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
              <Bot className="h-5 w-5 text-white" />
            </div>

            <div>
              <h1 className="text-lg font-semibold">
                Support Intelligence
              </h1>
              <p className="text-xs text-slate-500">
                AmazonHelp AI Agent
              </p>
            </div>
          </div>

          <div className="flex items-center gap-5 text-sm text-slate-600">
            <span className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-green-600" />
              Agent online
            </span>

            <button
              onClick={() => setLoggedIn(false)}
              className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-slate-100"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>

            <div className="h-8 w-8 rounded-full bg-slate-200 text-center pt-1.5 font-medium">
              P
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        <aside className="hidden min-h-[calc(100vh-64px)] w-60 border-r border-slate-200 bg-white p-4 md:block">
          <nav className="space-y-1">
            <div className="flex items-center gap-3 rounded-lg bg-blue-50 px-3 py-2.5 text-sm font-medium text-blue-700">
              <Inbox className="h-4 w-4" />
              Support Inbox
            </div>

            <div className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-600">
              <MessageSquare className="h-4 w-4" />
              Conversations
            </div>

            <div className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-600">
              <ShieldCheck className="h-4 w-4" />
              Evaluations
            </div>
          </nav>

          <div className="mt-8 border-t border-slate-100 pt-5">
            <p className="px-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Workspace
            </p>

            <div className="mt-3 flex items-center gap-3 px-3 py-2 text-sm text-slate-600">
              <Users className="h-4 w-4" />
              Human review
            </div>
          </div>
        </aside>

        <main className="flex-1 p-6 lg:p-8">
          <div className="mx-auto max-w-6xl">
            <div className="mb-7">
              <h2 className="text-2xl font-semibold">
                Support Inbox
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Review customer requests and AI-assisted responses.
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-3">
              <StatCard
                icon={<Inbox className="h-5 w-5" />}
                label="Open conversations"
                value="24"
              />

              <StatCard
                icon={<Bot className="h-5 w-5" />}
                label="Auto-handled today"
                value="18"
              />

              <StatCard
                icon={<Users className="h-5 w-5" />}
                label="Needs human review"
                value="6"
              />
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
              <section className="rounded-xl border border-slate-200 bg-white">
                <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
                  <div>
                    <h3 className="font-semibold">
                      New customer request
                    </h3>

                    <p className="text-xs text-slate-500">
                      Analyze with the support agent
                    </p>
                  </div>

                  <Search className="h-4 w-4 text-slate-400" />
                </div>

                <div className="p-5">
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Customer message
                  </label>

                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Paste a customer support message..."
                    className="min-h-36 w-full resize-none rounded-lg border border-slate-300 p-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  />

                  <button
                    onClick={analyzeMessage}
                    disabled={loading}
                    className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
                  >
                    {loading ? 'Analyzing...' : 'Analyze request'}

                    {!loading && (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </section>

              <section className="rounded-xl border border-slate-200 bg-white">
                <div className="border-b border-slate-200 px-5 py-4">
                  <h3 className="font-semibold">
                    AI decision
                  </h3>

                  <p className="text-xs text-slate-500">
                    Classification, routing and suggested response
                  </p>
                </div>

                {!result ? (
                  <div className="flex min-h-80 flex-col items-center justify-center p-6 text-center">
                    <div className="mb-3 rounded-full bg-slate-100 p-3">
                      <Bot className="h-6 w-6 text-slate-400" />
                    </div>

                    <p className="text-sm font-medium text-slate-600">
                      No request analyzed yet
                    </p>

                    <p className="mt-1 max-w-xs text-xs text-slate-400">
                      Enter a customer message to see the AI decision.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-5 p-5">
                    <div className="grid grid-cols-2 gap-3">
                      <InfoCard
                        label="Intent"
                        value={result.intent.replaceAll('_', ' ')}
                      />

                      <InfoCard
                        label="Confidence"
                        value={`${Math.round(result.confidence * 100)}%`}
                      />
                    </div>

                    <div
                      className={`rounded-lg border p-4 ${
                        result.decision === 'auto_handle'
                          ? 'border-green-200 bg-green-50'
                          : 'border-amber-200 bg-amber-50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5" />

                        <span className="text-sm font-semibold">
                          {result.decision === 'auto_handle'
                            ? 'Auto-handle'
                            : 'Escalate to human'}
                        </span>
                      </div>

                      <p className="mt-2 text-xs leading-5 text-slate-600">
                        {result.escalation_reason}
                      </p>
                    </div>

                    <div>
                      <p className="mb-2 text-sm font-medium">
                        Suggested reply
                      </p>

                      <div className="rounded-lg bg-slate-50 p-4 text-sm leading-6 text-slate-700">
                        {result.draft_reply}
                      </div>
                    </div>

                    <div>
                      <div className="mb-3 flex items-center justify-between">
                        <p className="text-sm font-medium">
                          Historical evidence
                        </p>

                        <span className="text-xs text-slate-400">
                          Top{' '}
                          {Math.min(
                            3,
                            result.historical_evidence.length
                          )}{' '}
                          matches
                        </span>
                      </div>

                      <div className="space-y-3">
                        {result.historical_evidence
                          .slice(0, 3)
                          .map((item) => (
                            <div
                              key={item.rank}
                              className="rounded-lg border border-slate-200 p-3"
                            >
                              <div className="mb-2 flex items-center justify-between">
                                <span className="text-xs font-medium text-slate-500">
                                  Match #{item.rank}
                                </span>

                                <span className="text-xs font-medium text-blue-600">
                                  {(item.score * 100).toFixed(1)}%
                                  similarity
                                </span>
                              </div>

                              <p className="text-xs font-medium text-slate-400">
                                Historical customer
                              </p>

                              <p className="mt-1 text-sm leading-5 text-slate-700">
                                {item.customer_text}
                              </p>

                              <p className="mt-3 text-xs font-medium text-slate-400">
                                Historical AmazonHelp response
                              </p>

                              <p className="mt-1 text-sm leading-5 text-slate-700">
                                {item.agent_response}
                              </p>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                )}
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
        {icon}
      </div>

      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-2xl font-semibold">
        {value}
      </p>
    </div>
  )
}

function InfoCard({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="rounded-lg border border-slate-200 p-3">
      <p className="text-xs text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold capitalize">
        {value}
      </p>
    </div>
  )
}

export default App