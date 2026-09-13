import { useEffect, useState } from "react"
import { useParams, Link } from "react-router-dom"
import { ArrowLeft, Activity, TrendingUp, Shield, Zap, AlertTriangle, ChevronRight, Briefcase, MapPin } from "lucide-react"
import {
  getBorrower, getForecast, getRisk, getScheduleComparison, getAlerts,
  type Borrower, type ForecastResult, type RiskResult, type ScheduleComparison, type AlertResult
} from "@/services/api"
import CashFlowChart from "@/components/borrower/CashFlowChart"
import RepaymentComparison from "@/components/simulation/RepaymentComparison"
import RiskExplanationCard from "@/components/risk/RiskExplanationCard"
import StressTestSlider from "@/components/simulation/StressTestSlider"
import { formatCurrency, personaLabel, riskBgClass, personaGradient, getInitials, cn } from "@/lib/utils"

type Tab = "cashflow" | "schedule" | "risk" | "stress"

// Removed unused SVG components

// ─── Tab button ──────────────────────────────────────────────────────────────
function TabButton({ label, icon: Icon, active, onClick }: {
  label: string; icon: any; active: boolean; onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-4 py-2.5 rounded-xl font-heading text-sm font-medium transition-all duration-200 cursor-pointer",
        active
          ? "bg-primary-600 text-white shadow-glow"
          : "text-ink-muted bg-white border border-border hover:border-primary-200 hover:text-primary-600 hover:bg-primary-50"
      )}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  )
}

// ─── Stat item ───────────────────────────────────────────────────────────────
function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <p className="text-ink-faint text-xs font-medium uppercase tracking-wide">{label}</p>
      <p className="font-heading font-semibold text-ink">{value}</p>
    </div>
  )
}

// ─── Risk tier badge ─────────────────────────────────────────────────────────
function RiskBadge({ tier }: { tier: string }) {
  const map: Record<string, string> = {
    low:      "bg-emerald-50 text-emerald-700 border-emerald-200",
    moderate: "bg-amber-50   text-amber-700   border-amber-200",
    high:     "bg-orange-50  text-orange-700  border-orange-200",
    critical: "bg-red-50     text-red-700     border-red-200",
  }
  return (
    <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-semibold border capitalize", map[tier] ?? "bg-slate-100 text-slate-600 border-slate-200")}>
      {tier} risk
    </span>
  )
}

// ─── Main page ───────────────────────────────────────────────────────────────
export default function BorrowerDetail() {
  const { id } = useParams<{ id: string }>()
  const borrowerId = Number(id)

  const [tab, setTab] = useState<Tab>("cashflow")
  const [borrower, setBorrower] = useState<Borrower | null>(null)
  const [forecast, setForecast] = useState<ForecastResult | null>(null)
  const [risk, setRisk] = useState<RiskResult | null>(null)
  const [schedule, setSchedule] = useState<ScheduleComparison | null>(null)
  const [alerts, setAlerts] = useState<AlertResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchBase = async () => {
      const b = await getBorrower(borrowerId)
      setBorrower(b)
      setLoading(false)

      const [fc, rk, al] = await Promise.all([
        getForecast(borrowerId),
        getRisk(borrowerId),
        getAlerts(borrowerId),
      ])
      setForecast(fc)
      setRisk(rk)
      setAlerts(al)

      if ((b as any).loan?.id) {
        const sc = await getScheduleComparison((b as any).loan.id)
        setSchedule(sc)
      }
    }
    fetchBase()
  }, [borrowerId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-primary-100 flex items-center justify-center">
            <Activity className="w-6 h-6 text-primary-600 animate-pulse" />
          </div>
          <p className="font-heading text-sm text-ink-muted">Loading borrower profile…</p>
        </div>
      </div>
    )
  }

  if (!borrower) return <div className="p-8 text-red-600 font-heading">Borrower not found</div>

  const loan = (borrower as any).loan

  return (
    <div className="min-h-screen p-6 lg:p-8 max-w-7xl mx-auto">

      {/* ── Back link ── */}
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-ink-muted hover:text-primary-600 text-sm font-medium mb-6 cursor-pointer transition-colors group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
        Back to Portfolio
      </Link>

      {/* ── Profile header card ── */}
      <div className="card-glass p-6 mb-6 relative overflow-hidden">
        <div className="absolute -right-8 -top-8 w-40 h-40 bg-primary-100 rounded-full opacity-40 blur-2xl pointer-events-none" />
        <div className="relative z-10 flex items-start gap-5">
          {/* Premium Monogram Avatar */}
          <div className={cn(
            "w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 shadow-md bg-gradient-to-br text-white font-heading text-xl font-bold tracking-wider",
            personaGradient(borrower.persona_type)
          )}>
            {getInitials(borrower.name)}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2.5 flex-wrap mb-1">
              <h1 className="font-heading text-2xl font-bold text-ink tracking-tight">{borrower.name}</h1>
              {risk?.risk_tier && <RiskBadge tier={risk.risk_tier} />}
              {alerts?.is_stressed && (
                <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-600 border border-red-200">
                  <AlertTriangle className="w-3 h-3" />
                  Stress Detected
                </span>
              )}
            </div>
            
            <div className="flex items-center gap-2 text-sm font-medium text-ink-muted mb-5">
              <span className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5 text-ink-faint" />
                {personaLabel(borrower.persona_type)}
              </span>
              <span className="text-border-strong">&bull;</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-ink-faint" />
                {borrower.location}
              </span>
            </div>

            {/* Stats row */}
            <div className="flex gap-6 flex-wrap">
              <StatItem label="Monthly Income" value={formatCurrency(borrower.base_monthly_income)} />
              {loan && <>
                <StatItem label="Loan Amount" value={formatCurrency(loan.principal)} />
                <StatItem label="Base EMI" value={`${formatCurrency(loan.base_emi)}/mo`} />
                <StatItem label="Interest Rate" value={`${(loan.annual_interest_rate * 100).toFixed(0)}% p.a.`} />
              </>}
            </div>
          </div>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <TabButton label="Cash Flow"          icon={TrendingUp} active={tab === "cashflow"}  onClick={() => setTab("cashflow")} />
        <TabButton label="Repayment Schedule" icon={Activity}   active={tab === "schedule"}  onClick={() => setTab("schedule")} />
        <TabButton label="Risk Analysis"      icon={Shield}     active={tab === "risk"}      onClick={() => setTab("risk")} />
        <TabButton label="Stress Test"        icon={Zap}        active={tab === "stress"}    onClick={() => setTab("stress")} />
      </div>

      {/* ── Tab content ── */}
      {tab === "cashflow" && (
        <div className="card p-6 animate-fade-in">
          <div className="mb-5">
            <h2 className="font-heading text-base font-semibold text-ink">Cash Flow + Forecast</h2>
            <p className="text-ink-muted text-xs mt-1">
              Historical daily net cash flow · P10 / P50 / P90 forecast bands
            </p>
          </div>
          {forecast ? (
            <CashFlowChart forecast={forecast} height={350} />
          ) : (
            <div className="flex items-center justify-center h-40 text-ink-faint gap-2">
              <Activity className="w-4 h-4 animate-spin" /> Loading forecast…
            </div>
          )}
        </div>
      )}

      {tab === "schedule" && (
        <div className="space-y-4 animate-fade-in">
          <div className="card p-6">
            <div className="mb-5">
              <h2 className="font-heading text-base font-semibold text-ink">Dynamic vs Fixed EMI Comparison</h2>
              <p className="text-ink-muted text-xs mt-1">
                RaahPay dynamic payments vs what a fixed EMI would charge every month
              </p>
            </div>
            {schedule ? (
              <>
                <RepaymentComparison data={schedule} height={300} />
                <div className="grid grid-cols-2 gap-4 mt-5">
                  <div className="bg-primary-50 border border-primary-100 rounded-xl p-4">
                    <p className="text-primary-600 text-xs font-medium mb-1">RaahPay Total</p>
                    <p className="font-heading font-bold text-primary-700 text-xl">{formatCurrency(schedule.summary.dynamic_total)}</p>
                  </div>
                  <div className="bg-slate-50 border border-border rounded-xl p-4">
                    <p className="text-ink-muted text-xs font-medium mb-1">Fixed EMI Total</p>
                    <p className="font-heading font-bold text-ink-muted text-xl">{formatCurrency(schedule.summary.fixed_total)}</p>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-40 text-ink-faint gap-2">
                <Activity className="w-4 h-4 animate-spin" /> Loading schedule…
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "risk" && (
        <div className="animate-fade-in">
          {risk ? (
            <RiskExplanationCard
              explanations={risk.shap_explanations}
              defaultProbability={risk.default_probability}
              affordabilityScore={risk.affordability_score}
              financialState={risk.financial_state}
              riskTier={risk.risk_tier}
            />
          ) : (
            <div className="flex items-center justify-center h-40 text-ink-faint gap-2">
              <Activity className="w-4 h-4 animate-spin" /> Running risk model…
            </div>
          )}
        </div>
      )}

      {tab === "stress" && (
        <div className="card p-6 animate-fade-in">
          <div className="mb-6">
            <h2 className="font-heading text-base font-semibold text-ink">Revenue Shock Simulator</h2>
            <p className="text-ink-muted text-xs mt-1">
              Simulate an income shock (rain, harvest failure, gig penalty) and see how RaahPay adapts vs a fixed EMI defaulting.
            </p>
          </div>
          <StressTestSlider
            borrowerId={borrowerId}
            loanId={loan?.id}
            baseEmi={loan?.base_emi}
          />
        </div>
      )}
    </div>
  )
}
