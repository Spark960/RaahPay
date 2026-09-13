import React from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts"
import type { ShapExplanation } from "@/services/api"
import { cn, financialStateColor } from "@/lib/utils"

interface Props {
  explanations: ShapExplanation[]
  defaultProbability: number
  affordabilityScore: number
  financialState: string
  riskTier: string
}

// ─── Light-mode tooltip ──────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload as ShapExplanation & { shap_value: number }
  return (
    <div className="bg-white border border-border rounded-xl p-3 shadow-xl text-xs font-body max-w-60">
      <p className="font-semibold text-ink mb-1">{d?.label}</p>
      <p className="text-ink-muted mb-1">
        SHAP impact:{" "}
        <span className={d?.shap_value > 0 ? "text-red-600 font-semibold" : "text-emerald-700 font-semibold"}>
          {d?.shap_value > 0 ? "+" : ""}{d?.shap_value?.toFixed(3)}
        </span>
      </p>
      {d?.advice && <p className="text-primary-600 text-xs leading-relaxed">{d.advice}</p>}
    </div>
  )
}

// ─── DAS gauge (works on white bg) ──────────────────────────────────────────
function DasGauge({ score }: { score: number }) {
  const color = score >= 70 ? "#059669" : score >= 45 ? "#D97706" : "#DC2626"
  const angle = (score / 100) * 180 - 90
  const rad = (angle * Math.PI) / 180
  const x = 50 + 40 * Math.cos(rad)
  const y = 50 - 40 * Math.sin(rad)

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 100 60" className="w-36 h-20">
        {/* Track arc */}
        <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#E2E8F0" strokeWidth="10" strokeLinecap="round" />
        {/* Filled arc */}
        <path
          d={`M 10 50 A 40 40 0 0 1 ${x.toFixed(1)} ${y.toFixed(1)}`}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* Needle */}
        <line x1="50" y1="50" x2={x.toFixed(1)} y2={y.toFixed(1)} stroke={color} strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="50" cy="50" r="3.5" fill={color} />
      </svg>
      <span className="font-heading text-3xl font-bold mt-1" style={{ color }}>{score.toFixed(0)}</span>
      <span className="text-ink-faint text-xs font-body">DAS Score / 100</span>
    </div>
  )
}

// ─── Financial state icon (SVG-based, no emojis) ─────────────────────────────
function FinancialStateIcon({ state }: { state: string }): React.ReactElement {
  const iconMap: Record<string, React.ReactElement> = {
    thriving: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
        <polyline points="16 7 22 7 22 13"/>
      </svg>
    ),
    stable: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10Z"/>
        <path d="m9 12 2 2 4-4"/>
      </svg>
    ),
    recovering: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 12h18M3 12l4-4M3 12l4 4"/>
      </svg>
    ),
    stressed: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" x2="12" y1="9" y2="13"/>
        <line x1="12" x2="12.01" y1="17" y2="17"/>
      </svg>
    ),
    deteriorating: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/>
        <polyline points="16 17 22 17 22 11"/>
      </svg>
    ),
  }
  return iconMap[state] ?? iconMap["stable"]
}

// ─── Main card ───────────────────────────────────────────────────────────────
export default function RiskExplanationCard({ explanations, defaultProbability, affordabilityScore, financialState, riskTier }: Props) {
  const chartData = explanations.slice(0, 6).map(e => ({
    ...e,
    label_short: e.label.length > 22 ? e.label.slice(0, 20) + "…" : e.label,
    value: e.shap_value,
  }))

  const tierColors: Record<string, string> = {
    low: "#059669", moderate: "#D97706", high: "#EA580C", critical: "#DC2626"
  }
  const tierColor = tierColors[riskTier] ?? "#64748B"

  const stateLabels: Record<string, string> = {
    thriving: "Thriving", stable: "Stable", recovering: "Recovering",
    stressed: "Stressed", deteriorating: "Deteriorating"
  }

  return (
    <div className="space-y-4">
      {/* ── Top row: DAS · Default Prob · Financial State ── */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4 flex flex-col items-center justify-center">
          <p className="text-ink-faint text-xs font-medium uppercase tracking-wide mb-3">Affordability</p>
          <DasGauge score={affordabilityScore} />
        </div>

        <div className="card p-4 flex flex-col items-center justify-center text-center">
          <p className="text-ink-faint text-xs font-medium uppercase tracking-wide mb-2">Default Risk</p>
          <p className="font-heading text-4xl font-bold" style={{ color: tierColor }}>
            {(defaultProbability * 100).toFixed(1)}%
          </p>
          <span className={cn(
            "mt-2 px-2.5 py-0.5 rounded-full text-xs font-semibold border capitalize",
            riskTier === "low"      ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
            riskTier === "moderate" ? "bg-amber-50 text-amber-700 border-amber-200" :
            riskTier === "high"     ? "bg-orange-50 text-orange-700 border-orange-200" :
                                      "bg-red-50 text-red-700 border-red-200"
          )}>
            {riskTier}
          </span>
        </div>

        <div className="card p-4 flex flex-col items-center justify-center text-center">
          <p className="text-ink-faint text-xs font-medium uppercase tracking-wide mb-3">Financial State</p>
          <div className={cn(
            "w-12 h-12 rounded-2xl flex items-center justify-center mb-2",
            financialState === "thriving"     ? "bg-emerald-100 text-emerald-700" :
            financialState === "stable"       ? "bg-blue-100 text-blue-700" :
            financialState === "recovering"   ? "bg-sky-100 text-sky-700" :
            financialState === "stressed"     ? "bg-amber-100 text-amber-700" :
                                               "bg-red-100 text-red-700"
          )}>
            <FinancialStateIcon state={financialState} />
          </div>
          <p className={cn("font-heading text-sm font-semibold capitalize", financialStateColor(financialState))}>
            {stateLabels[financialState] ?? financialState}
          </p>
        </div>
      </div>

      {/* ── SHAP waterfall ── */}
      <div className="card p-5">
        <p className="font-heading text-sm font-semibold text-ink mb-0.5">Risk Factor Contributions (SHAP)</p>
        <p className="text-ink-muted text-xs mb-4">
          Positive = increases default risk · Negative = reduces risk
        </p>
        <div style={{ height: 220 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fill: "#64748B", fontSize: 10, fontFamily: "DM Sans" }}
                tickLine={false}
                tickFormatter={v => v.toFixed(2)}
              />
              <YAxis
                type="category"
                dataKey="label_short"
                tick={{ fill: "#64748B", fontSize: 10, fontFamily: "DM Sans" }}
                tickLine={false}
                width={150}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine x={0} stroke="#CBD5E1" />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.value > 0 ? "#EF4444" : "#10B981"} fillOpacity={0.75} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Reason codes */}
        <div className="mt-4 space-y-2 border-t border-border pt-4">
          {explanations.filter(e => e.shap_value > 0.01).slice(0, 3).map((e, i) => (
            <div key={i} className="flex items-start gap-2 text-xs">
              <span className="text-red-500 mt-0.5 flex-shrink-0 font-bold">▲</span>
              <div>
                <span className="text-ink font-semibold">{e.label}</span>
                {e.advice && <span className="text-ink-muted ml-1">— {e.advice}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
