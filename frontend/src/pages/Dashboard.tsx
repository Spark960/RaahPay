import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import {
  TrendingUp, AlertTriangle, Users, IndianRupee, Activity,
  ArrowRight, ShieldCheck, Sparkles, ChevronRight, Briefcase, MapPin
} from "lucide-react"
import { getBorrowers, type Borrower } from "@/services/api"
import { cn, formatCurrency, personaLabel, riskBgClass, riskColor, personaGradient, getInitials } from "@/lib/utils"

// ─── KPI card ───────────────────────────────────────────────────────────────
function MetricCard({
  label, value, icon: Icon, iconBg, sub, trend
}: {
  label: string; value: string; icon: any
  iconBg?: string; sub?: string; trend?: "up" | "down" | "neutral"
}) {
  const trendEl = trend === "up"
    ? <span className="inline-flex items-center gap-0.5 text-xs text-emerald-600 font-medium bg-emerald-50 px-1.5 py-0.5 rounded-full">▲ Good</span>
    : trend === "down"
    ? <span className="inline-flex items-center gap-0.5 text-xs text-red-500 font-medium bg-red-50 px-1.5 py-0.5 rounded-full">▼ Alert</span>
    : null

  return (
    <div className="card p-5 flex items-start gap-4 hover:shadow-card-hover transition-all duration-200 group">
      <div className={cn("p-3 rounded-xl flex-shrink-0", iconBg ?? "bg-primary-100 text-primary-600")}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-ink-faint text-xs font-medium uppercase tracking-wide mb-0.5">{label}</p>
        <p className="font-heading text-2xl font-bold text-ink">{value}</p>
        <div className="mt-1.5 flex items-center gap-2">
          {sub && <p className="text-ink-muted text-xs">{sub}</p>}
          {trendEl}
        </div>
      </div>
    </div>
  )
}

// ─── Risk badge ─────────────────────────────────────────────────────────────
function RiskBadge({ tier }: { tier: string }) {
  const map: Record<string, string> = {
    low:      "bg-emerald-50 text-emerald-700 border-emerald-200",
    moderate: "bg-amber-50   text-amber-700   border-amber-200",
    high:     "bg-orange-50  text-orange-700  border-orange-200",
    critical: "bg-red-50     text-red-700     border-red-200",
  }
  return (
    <span className={cn("px-2 py-0.5 rounded-full text-xs font-semibold border capitalize", map[tier] ?? "bg-slate-100 text-slate-600 border-slate-200")}>
      {tier}
    </span>
  )
}

// ─── Persona tag ─────────────────────────────────────────────────────────────
function PersonaTag({ type }: { type: string }) {
  const colors: Record<string, string> = {
    vendor:     "bg-violet-50 text-violet-700 border-violet-200",
    farmer:     "bg-emerald-50 text-emerald-700 border-emerald-200",
    gig_worker: "bg-sky-50 text-sky-700 border-sky-200",
  }
  return (
    <span className={cn("px-2 py-0.5 rounded text-xs font-medium border", colors[type] ?? "bg-slate-100 text-slate-600 border-slate-200")}>
      {personaLabel(type)}
    </span>
  )
}

// ─── DAS score bar ──────────────────────────────────────────────────────────
function ScoreBar({ score, tier }: { score: number | null | undefined; tier: string }) {
  const s = score ?? 0
  const barColor =
    tier === "low"      ? "bg-emerald-500" :
    tier === "moderate" ? "bg-amber-400" :
    tier === "high"     ? "bg-orange-500" : "bg-red-500"
  return (
    <div className="w-20">
      <div className="flex items-center justify-between mb-1">
        <span className={cn("font-heading text-sm font-bold", riskColor(tier))}>{s.toFixed(0)}</span>
        <span className="text-ink-faint text-xs">/100</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={cn("h-full rounded-full transition-all", barColor)} style={{ width: `${s}%` }} />
      </div>
    </div>
  )
}

// ─── Main dashboard ──────────────────────────────────────────────────────────
export default function Dashboard() {
  const [borrowers, setBorrowers] = useState<Borrower[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getBorrowers().then(data => {
      setBorrowers(data)
      setLoading(false)
    })
  }, [])

  const atRisk = borrowers.filter(b => b.risk_tier === "high" || b.risk_tier === "critical").length
  const totalPrincipal = borrowers.reduce((s, b) => s + (b.loan_principal ?? 0), 0)
  const avgDas = borrowers.length
    ? Math.round(borrowers.reduce((s, b) => s + (b.affordability_score ?? 0), 0) / borrowers.length)
    : 0

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-primary-100 flex items-center justify-center">
            <Activity className="w-6 h-6 text-primary-600 animate-pulse" />
          </div>
          <p className="font-heading text-sm text-ink-muted">Loading portfolio…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-6 lg:p-8 max-w-7xl mx-auto">

      {/* ── Top nav bar ── */}
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Logo mark */}
          <img src="/assets/raahpay.png" alt="RaahPay Logo" className="w-10 h-10 object-contain rounded-xl shadow-sm" />
          <div>
            <h1 className="font-heading text-xl font-bold text-ink leading-none">RaahPay</h1>
            <p className="text-ink-faint text-xs font-medium mt-0.5">Lender Dashboard</p>
          </div>
        </div>

        {/* Right: badge */}
        <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary-50 border border-primary-100 text-primary-700 text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          SDG 8 &bull; Financial Inclusion
        </span>
      </header>

      {/* ── KPI row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Active Borrowers"
          value={String(borrowers.length)}
          icon={Users}
          iconBg="bg-primary-100 text-primary-600"
          sub="In portfolio"
          trend="neutral"
        />
        <MetricCard
          label="At Risk"
          value={String(atRisk)}
          icon={AlertTriangle}
          iconBg="bg-red-100 text-red-500"
          sub={atRisk > 0 ? "Needs attention" : "Portfolio healthy"}
          trend={atRisk > 0 ? "down" : "up"}
        />
        <MetricCard
          label="Total Portfolio"
          value={formatCurrency(totalPrincipal)}
          icon={IndianRupee}
          iconBg="bg-emerald-100 text-emerald-600"
          sub="Outstanding principal"
          trend="up"
        />
        <MetricCard
          label="Avg. DAS Score"
          value={`${avgDas}`}
          icon={Activity}
          iconBg="bg-violet-100 text-violet-600"
          sub="Dynamic Affordability"
          trend={avgDas >= 60 ? "up" : "down"}
        />
      </div>

      {/* ── Borrower list ── */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-heading text-base font-semibold text-ink">Borrower Portfolio</h2>
        <span className="text-ink-faint text-sm">{borrowers.length} borrowers</span>
      </div>

      <div className="grid gap-3">
        {borrowers.map(b => (
          <Link
            key={b.id}
            to={`/borrower/${b.id}`}
            className="card p-4 sm:p-5 flex items-center gap-4 hover:shadow-card-hover hover:border-primary-200 cursor-pointer transition-all duration-200 group"
          >
            {/* Premium Monogram Avatar */}
            <div className={cn(
              "w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-105 shadow-sm bg-gradient-to-br text-white font-heading font-bold tracking-wider",
              personaGradient(b.persona_type)
            )}>
              {getInitials(b.name)}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="font-heading text-[15px] font-bold text-ink tracking-tight">{b.name}</span>
                {b.risk_tier && <RiskBadge tier={b.risk_tier} />}
              </div>
              <div className="flex items-center gap-1.5 text-xs font-medium text-ink-muted flex-wrap">
                <span className="flex items-center gap-1">
                  <Briefcase className="w-3 h-3 text-ink-faint" />
                  {personaLabel(b.persona_type)}
                </span>
                <span className="text-border-strong">&bull;</span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-ink-faint" />
                  {b.location}
                </span>
              </div>
            </div>

            {/* Desktop metrics */}
            <div className="hidden md:flex items-center gap-8 flex-shrink-0">
              <div className="text-right">
                <p className="text-ink-faint text-[11px] font-bold tracking-wider uppercase mb-0.5">Monthly Income</p>
                <p className="font-heading text-sm font-semibold text-ink">{formatCurrency(b.base_monthly_income)}</p>
              </div>
              <div className="text-right">
                <p className="text-ink-faint text-[11px] font-bold tracking-wider uppercase mb-0.5">Loan</p>
                <p className="font-heading text-sm font-semibold text-ink">{formatCurrency(b.loan_principal ?? 0)}</p>
              </div>
              <div className="text-right">
                <p className="text-ink-faint text-[11px] font-bold tracking-wider uppercase mb-1">DAS Score</p>
                <ScoreBar score={b.affordability_score} tier={b.risk_tier ?? "moderate"} />
              </div>
              <div className="text-right">
                <p className="text-ink-faint text-[11px] font-bold tracking-wider uppercase mb-0.5">Default Prob.</p>
                <p className={cn("font-heading text-sm font-bold", riskColor(b.risk_tier ?? "moderate"))}>
                  {b.default_probability !== undefined ? `${(b.default_probability * 100).toFixed(1)}%` : "—"}
                </p>
              </div>
            </div>

            <ChevronRight className="w-4 h-4 text-ink-faint group-hover:text-primary-500 transition-colors flex-shrink-0 ml-2" />
          </Link>
        ))}
      </div>

      {/* ── Footer note ── */}
      <p className="mt-8 text-center text-ink-faint text-xs">
        RaahPay · Adaptive Microloan Platform · SDG 8 Financial Inclusion
      </p>
    </div>
  )
}
