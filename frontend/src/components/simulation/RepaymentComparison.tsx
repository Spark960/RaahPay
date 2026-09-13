import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine
} from "recharts"
import { useMemo } from "react"
import type { ScheduleComparison, StressTestResult } from "@/services/api"
import { formatCurrency } from "@/lib/utils"

interface Props {
  data: ScheduleComparison | null
  stressResult?: StressTestResult | null
  height?: number
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-xl text-xs font-body">
      <p className="text-slate-500 mb-2">Period {label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center gap-2 mb-1">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-600">{p.name}:</span>
          <span className="font-semibold" style={{ color: p.color }}>
            {formatCurrency(Number(p.value))}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function RepaymentComparison({ data, stressResult, height = 300 }: Props) {
  const chartData = useMemo(() => {
    if (!data) return []
    const len = Math.max(data.dynamic_schedule.length, data.fixed_schedule.length)

    return Array.from({ length: len }, (_, i) => {
      const dyn = data.dynamic_schedule[i]
      const fix = data.fixed_schedule[i]
      const missedFixed = stressResult?.summary.fixed_missed_periods.includes(i + 1)
      const stressedDyn = stressResult?.summary.dynamic_stressed_periods.includes(i + 1)

      return {
        period: i + 1,
        "RaahPay Dynamic": dyn?.dynamic_payment ?? null,
        "Traditional EMI": fix?.fixed_payment ?? null,
        missed: missedFixed,
        stressed: stressedDyn,
      }
    })
  }, [data, stressResult])

  if (!data) return (
    <div className="flex items-center justify-center h-32 text-ink-muted text-sm font-body">
      Loading schedule…
    </div>
  )

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis
            dataKey="period"
            tick={{ fill: "#64748B", fontSize: 10, fontFamily: "DM Sans" }}
            tickLine={false}
            label={{ value: "Month", fill: "#94A3B8", fontSize: 10, position: "insideBottom", offset: -2 }}
          />
          <YAxis
            tick={{ fill: "#64748B", fontSize: 10, fontFamily: "DM Sans" }}
            tickLine={false}
            tickFormatter={v => `₹${v}`}
            width={65}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "DM Sans", color: "#64748B" }} />

          {/* Traditional EMI flat line */}
          <Line
            type="monotone"
            dataKey="Traditional EMI"
            stroke="#94A3B8"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
          />

          {/* Dynamic payments as bars */}
          <Bar dataKey="RaahPay Dynamic" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  entry.missed ? "#EF4444"      // red = traditional would miss
                  : entry.stressed ? "#F59E0B"  // amber = dynamic adapts
                  : "#4F46E5"                   // indigo = normal (RaahPay primary)
                }
                fillOpacity={0.80}
              />
            ))}
          </Bar>

          {/* Base EMI reference */}
          {data.base_emi && (
            <ReferenceLine
              y={data.base_emi}
              stroke="#CBD5E1"
              strokeDasharray="4 2"
              label={{ value: "Base EMI", fill: "#94A3B8", fontSize: 9, fontFamily: "DM Sans" }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
