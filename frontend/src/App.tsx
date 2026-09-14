import { useState, type ReactNode } from 'react'
import {
  Activity,
  BarChart3,
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

type Conversation = {
  id: number
  message: string
  intent: string
  confidence: number
  decision: string
  reply: string
}

type Page = 'inbox' | 'conversations' | 'evaluations' | 'human-review'

function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const [loginError, setLoginError] = useState('')

  const [page, setPage] = useState<Page>('inbox')
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<AgentResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [conversations, setConversations] = useState<Conversation[]>([])

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

      const data: AgentResult = await response.json()
      setResult(data)

      setConversations((previous) => [
        {
          id: Date.now(),
          message,
          intent: data.intent,
          confidence: data.confidence,
          decision: data.decision,
          reply: data.draft_reply,
        },
        ...previous,
      ])

      setPage('inbox')
    } catch (error) {
      console.error(error)
      alert('Could not connect to the support agent.')
    } finally {
      setLoading(false)
    }
  }

  const navigate = (nextPage: Page) => {
    setPage(nextPage)
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
            <SidebarItem
              icon={<Inbox className="h-4 w-4" />}
              label="Support Inbox"
              active={page === 'inbox'}
              onClick={() => navigate('inbox')}
            />

            <SidebarItem
              icon={<MessageSquare className="h-4 w-4" />}
              label="Conversations"
              active={page === 'conversations'}
              onClick={() => navigate('conversations')}
            />

            <SidebarItem
              icon={<ShieldCheck className="h-4 w-4" />}
              label="Evaluations"
              active={page === 'evaluations'}
              onClick={() => navigate('evaluations')}
            />
          </nav>

          <div className="mt-8 border-t border-slate-100 pt-5">
            <p className="px-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Workspace
            </p>

            <button
              onClick={() => navigate('human-review')}
              className={`mt-3 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm ${
                page === 'human-review'
                  ? 'bg-blue-50 font-medium text-blue-700'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Users className="h-4 w-4" />
              Human review
            </button>
          </div>
        </aside>

        <main className="flex-1 p-6 lg:p-8">
          <div className="mx-auto max-w-6xl">
            {page === 'inbox' && (
              <SupportInbox
                message={message}
                setMessage={setMessage}
                result={result}
                loading={loading}
                analyzeMessage={analyzeMessage}
              />
            )}

            {page === 'conversations' && (
              <ConversationsPage conversations={conversations} />
            )}

            {page === 'evaluations' && <EvaluationsPage />}

            {page === 'human-review' && (
              <HumanReviewPage conversations={conversations} />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

function SidebarItem({
  icon,
  label,
  active,
  onClick,
}: {
  icon: ReactNode
  label: string
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm ${
        active
          ? 'bg-blue-50 font-medium text-blue-700'
          : 'text-slate-600 hover:bg-slate-50'
      }`}
    >
      {icon}
      {label}
    </button>
  )
}

function SupportInbox({
  message,
  setMessage,
  result,
  loading,
  analyzeMessage,
}: {
  message: string
  setMessage: (value: string) => void
  result: AgentResult | null
  loading: boolean
  analyzeMessage: () => void
}) {
  return (
    <>
      <div className="mb-7">
        <h2 className="text-2xl font-semibold">Support Inbox</h2>

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
              <h3 className="font-semibold">New customer request</h3>

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

              {!loading && <ChevronRight className="h-4 w-4" />}
            </button>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-5 py-4">
            <h3 className="font-semibold">AI decision</h3>

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
                    Top {Math.min(3, result.historical_evidence.length)} matches
                  </span>
                </div>

                <div className="space-y-3">
                  {result.historical_evidence.slice(0, 3).map((item) => (
                    <div
                      key={item.rank}
                      className="rounded-lg border border-slate-200 p-3"
                    >
                      <div className="mb-2 flex items-center justify-between">
                        <span className="text-xs font-medium text-slate-500">
                          Match #{item.rank}
                        </span>

                        <span className="text-xs font-medium text-blue-600">
                          {(item.score * 100).toFixed(1)}% similarity
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
    </>
  )
}

function ConversationsPage({
  conversations,
}: {
  conversations: Conversation[]
}) {
  return (
    <>
      <PageHeader
        title="Conversations"
        subtitle="Previously analyzed customer support requests."
      />

      {conversations.length === 0 ? (
        <EmptyState
          icon={<MessageSquare className="h-6 w-6 text-slate-400" />}
          title="No conversations yet"
          description="Analyzed customer requests will appear here."
        />
      ) : (
        <div className="space-y-4">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className="rounded-xl border border-slate-200 bg-white p-5"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="text-xs font-medium text-slate-400">
                  Conversation #{conversation.id}
                </span>

                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                    conversation.decision === 'auto_handle'
                      ? 'bg-green-50 text-green-700'
                      : 'bg-amber-50 text-amber-700'
                  }`}
                >
                  {conversation.decision === 'auto_handle'
                    ? 'Auto-handled'
                    : 'Human review'}
                </span>
              </div>

              <p className="mt-4 text-sm leading-6 text-slate-700">
                {conversation.message}
              </p>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <InfoCard
                  label="Intent"
                  value={conversation.intent.replaceAll('_', ' ')}
                />

                <InfoCard
                  label="Confidence"
                  value={`${Math.round(
                    conversation.confidence * 100
                  )}%`}
                />
              </div>

              <div className="mt-4 rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-medium text-slate-400">
                  Suggested reply
                </p>

                <p className="mt-1 text-sm leading-6 text-slate-700">
                  {conversation.reply}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}

function EvaluationsPage() {
  return (
    <>
      <PageHeader
        title="Evaluations"
        subtitle="Final evaluation results on the 200-example golden set."
      />

      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Intent Accuracy"
          value="62.00%"
          description="AI Agent"
        />

        <MetricCard
          label="Intent Macro-F1"
          value="51.69%"
          description="AI Agent"
        />

        <MetricCard
          label="Escalation Accuracy"
          value="61.50%"
          description="200 evaluated cases"
        />

        <MetricCard
          label="Coverage"
          value="100%"
          description="200 / 200 successful"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600">
              <BarChart3 className="h-5 w-5" />
            </div>

            <div>
              <h3 className="font-semibold">
                Intent classification comparison
              </h3>

              <p className="text-xs text-slate-500">
                AI agent versus classification baselines
              </p>
            </div>
          </div>

          <EvaluationRow
            name="AI Agent"
            accuracy="62.00%"
            f1="51.69%"
          />

          <EvaluationRow
            name="TF-IDF + Logistic Regression"
            accuracy="66.00%"
            f1="49.19%"
          />

          <EvaluationRow
            name="Majority Baseline"
            accuracy="40.50%"
            f1="6.41%"
          />
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="font-semibold">LLM Judge</h3>

          <p className="mt-1 text-xs text-slate-500">
            Generated reply quality across the evaluated responses.
          </p>

          <div className="mt-5 space-y-4">
            <JudgeRow label="Relevance" value="3.63 / 5" />
            <JudgeRow label="Groundedness" value="4.41 / 5" />
            <JudgeRow label="Helpfulness" value="3.54 / 5" />
            <JudgeRow label="Overall quality" value="3.49 / 5" />
          </div>

          <div className="mt-6 rounded-lg bg-slate-50 p-4">
            <p className="text-xs font-medium text-slate-500">
              Judge-human validation
            </p>

            <p className="mt-1 text-xl font-semibold text-slate-900">
              92.5%
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Average exact agreement across four dimensions.
            </p>
          </div>
        </section>
      </div>

      <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="font-semibold">Evaluation coverage</h3>

        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-slate-500">
            Successful AI evaluations
          </span>

          <span className="font-semibold">200 / 200</span>
        </div>

        <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full w-full rounded-full bg-green-500" />
        </div>

        <p className="mt-3 text-xs text-slate-500">
          Final run completed with 0 API/run errors.
        </p>
      </div>
    </>
  )
}

function HumanReviewPage({
  conversations,
}: {
  conversations: Conversation[]
}) {
  const reviewCases = conversations.filter(
    (conversation) => conversation.decision !== 'auto_handle'
  )

  return (
    <>
      <PageHeader
        title="Human Review"
        subtitle="Customer requests that require additional human attention."
      />

      <div className="mb-6 grid gap-5 md:grid-cols-3">
        <StatCard
          icon={<Users className="h-5 w-5" />}
          label="Current review queue"
          value={String(reviewCases.length)}
        />

        <StatCard
          icon={<ShieldCheck className="h-5 w-5" />}
          label="Escalation threshold"
          value="75%"
        />

        <StatCard
          icon={<Search className="h-5 w-5" />}
          label="Evidence threshold"
          value="65%"
        />
      </div>

      {reviewCases.length === 0 ? (
        <EmptyState
          icon={<CheckCircle2 className="h-6 w-6 text-green-500" />}
          title="No active review cases"
          description="Cases requiring human review will appear here after analysis."
        />
      ) : (
        <div className="space-y-4">
          {reviewCases.map((conversation) => (
            <div
              key={conversation.id}
              className="rounded-xl border border-amber-200 bg-white p-5"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">
                  Conversation #{conversation.id}
                </span>

                <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
                  Escalated
                </span>
              </div>

              <p className="mt-4 text-sm leading-6 text-slate-700">
                {conversation.message}
              </p>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <InfoCard
                  label="Predicted intent"
                  value={conversation.intent.replaceAll('_', ' ')}
                />

                <InfoCard
                  label="Confidence"
                  value={`${Math.round(
                    conversation.confidence * 100
                  )}%`}
                />
              </div>

              <div className="mt-4 rounded-lg bg-amber-50 p-4">
                <p className="text-xs font-medium text-amber-700">
                  Reason for human review
                </p>

                <p className="mt-1 text-sm text-slate-700">
                  The agent determined that this request requires additional
                  human attention based on its confidence and evidence policy.
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}

function PageHeader({
  title,
  subtitle,
}: {
  title: string
  subtitle: string
}) {
  return (
    <div className="mb-7">
      <h2 className="text-2xl font-semibold">{title}</h2>

      <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
    </div>
  )
}

function EmptyState({
  icon,
  title,
  description,
}: {
  icon: ReactNode
  title: string
  description: string
}) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6 text-center">
      <div className="mb-3 rounded-full bg-slate-100 p-3">
        {icon}
      </div>

      <p className="text-sm font-medium text-slate-600">{title}</p>

      <p className="mt-1 max-w-sm text-xs text-slate-400">
        {description}
      </p>
    </div>
  )
}

function EvaluationRow({
  name,
  accuracy,
  f1,
}: {
  name: string
  accuracy: string
  f1: string
}) {
  return (
    <div className="border-b border-slate-100 py-4 last:border-0">
      <p className="text-sm font-medium text-slate-700">{name}</p>

      <div className="mt-2 flex gap-6 text-xs">
        <span className="text-slate-500">
          Accuracy <strong className="text-slate-800">{accuracy}</strong>
        </span>

        <span className="text-slate-500">
          Macro-F1 <strong className="text-slate-800">{f1}</strong>
        </span>
      </div>
    </div>
  )
}

function JudgeRow({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
      <span className="text-sm text-slate-600">{label}</span>

      <span className="text-sm font-semibold text-slate-900">
        {value}
      </span>
    </div>
  )
}

function MetricCard({
  label,
  value,
  description,
}: {
  label: string
  value: string
  description: string
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <p className="text-sm text-slate-500">{label}</p>

      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-400">{description}</p>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: ReactNode
  label: string
  value: string
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
        {icon}
      </div>

      <p className="text-sm text-slate-500">{label}</p>

      <p className="mt-1 text-2xl font-semibold">{value}</p>
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
      <p className="text-xs text-slate-400">{label}</p>

      <p className="mt-1 text-sm font-semibold capitalize">{value}</p>
    </div>
  )
}

export default App