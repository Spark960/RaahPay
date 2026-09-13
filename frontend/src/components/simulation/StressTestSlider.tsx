import { useState } from "react"
import { Zap, AlertTriangle, TrendingDown, CheckCircle } from "lucide-react"
import type { StressTestResult } from "@/services/api"
import { formatCurrency, cn } from "@/lib/utils"
import { runStressTest } from "@/services/api"
import RepaymentComparison from "./RepaymentComparison"

interface Props {
  borrowerId: number
  loanId?: number
  baseEmi?: number
}

export default function StressTestSlider({ borrowerId, loanId, baseEmi }: Props) {
  const [shockPct, setShockPct] = useState(30)
  const [durationDays, setDurationDays] = useState(30)
  const [result, setResult] = useState<StressTestResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    try {
      const r = await runStressTest({
        borrower_id: borrowerId,
        shock_pct: -(shockPct / 100),
        shock_duration_days: durationDays,
      })
      setResult(r)
    } finally {
      setLoading(false)
    }
  }

  // Build comparison-compatible object from stress result
  const comparisonData = result ? {
    loan_id: loanId ?? 0,
    base_emi: baseEmi ?? 0,
    dynamic_schedule: result.dynamic_schedule,
    fixed_schedule: result.fixed_schedule,
    summary: {
      dynamic_total: result.summary.dynamic_total_paid,
      fixed_total: result.summary.fixed_total_due,
      dynamic_periods: result.dynamic_schedule.length,
      fixed_periods: result.fixed_schedule.length,
    },
  } : null

  return (
    <div className="space-y-6">
      {/* ── Controls ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Revenue shock slider */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <label className="font-heading text-sm font-semibold text-ink">Revenue Shock</label>
            <span className="font-heading text-xl font-bold text-red-600">-{shockPct}%</span>
          </div>
          <input
            type="range" min={10} max={80} step={5}
            value={shockPct}
            onChange={e => setShockPct(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-red-500"
          />
          <p className="text-ink-muted text-xs font-body">
            Simulate an income drop (e.g. rain, harvest delay, gig penalty)
          </p>
        </div>

        {/* Duration slider */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <label className="font-heading text-sm font-semibold text-ink">Duration</label>
            <span className="font-heading text-xl font-bold text-amber-600">{durationDays} days</span>
          </div>
          <input
            type="range" min={7} max={90} step={7}
            value={durationDays}
            onChange={e => setDurationDays(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
          <p className="text-ink-muted text-xs font-body">
            Duration of the income shock
          </p>
        </div>
      </div>

      {/* ── Run button ── */}
      <button
        onClick={handleRun}
        disabled={loading}
        className="flex items-center gap-2 px-6 py-3 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white font-heading font-semibold rounded-xl transition-colors duration-200 cursor-pointer shadow-glow-amber"
      >
        <Zap className="w-4 h-4 fill-current" />
        {loading ? "Simulating…" : "Run Stress Test"}
      </button>

      {/* ── Results ── */}
      {result && (
        <div className="space-y-4 animate-fade-in mt-6 border-t border-border pt-6">
          {/* Summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="card p-4 border border-red-200 bg-red-50">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span className="text-red-700 text-xs font-medium uppercase tracking-wide">Fixed EMI</span>
              </div>
              <p className="font-heading text-3xl font-bold text-red-700">
                {result.summary.fixed_missed_payments}
              </p>
              <p className="text-red-600/80 text-xs mt-1 font-medium">missed payments</p>
            </div>

            <div className="card p-4 border border-emerald-200 bg-emerald-50">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span className="text-emerald-700 text-xs font-medium uppercase tracking-wide">RaahPay</span>
              </div>
              <p className="font-heading text-3xl font-bold text-emerald-700">
                {result.summary.dynamic_missed_payments}
              </p>
              <p className="text-emerald-600/80 text-xs mt-1 font-medium">zero missed payments</p>
            </div>

            <div className="card p-4 border border-primary-200 bg-primary-50">
              <div className="flex items-center gap-2 mb-2">
                <TrendingDown className="w-4 h-4 text-primary-600" />
                <span className="text-primary-700 text-xs font-medium uppercase tracking-wide">Savings</span>
              </div>
              <p className="font-heading text-2xl font-bold text-primary-700">
                {formatCurrency(result.summary.savings_from_dynamic)}
              </p>
              <p className="text-primary-600/80 text-xs mt-1 font-medium">vs fixed schedule</p>
            </div>
          </div>

          {/* Chart */}
          <div className="card p-5">
            <p className="font-heading text-sm font-semibold text-ink mb-1">Payment Schedule Under Shock</p>
            <p className="text-ink-muted text-xs font-body mb-5">
              <span className="text-primary-600 font-bold">■</span> RaahPay adapts &nbsp;&bull;&nbsp;
              <span className="text-amber-500 font-bold ml-2">■</span> Stressed (reduced) &nbsp;&bull;&nbsp;
              <span className="text-red-500 font-bold ml-2">■</span> Traditional EMI would default here
            </p>
            <RepaymentComparison data={comparisonData} stressResult={result} height={280} />
          </div>

          {/* Narrative */}
          <div className="card p-5 bg-emerald-50 border border-emerald-200">
            <p className="font-heading text-sm font-semibold text-emerald-800 mb-1.5">RaahPay Outcome</p>
            <p className="text-emerald-700 text-sm font-body leading-relaxed">
              With a <strong className="text-red-600">-{shockPct}% revenue shock</strong> for {durationDays} days,
              the traditional fixed EMI would trigger <strong className="text-red-600">
              {result.summary.fixed_missed_payments} default(s)</strong>. RaahPay's dynamic schedule
              <strong className="text-emerald-800"> reduces payments automatically during the shock</strong> and
              catches up during recovery, resulting in <strong className="text-emerald-800">zero missed payments</strong>.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
