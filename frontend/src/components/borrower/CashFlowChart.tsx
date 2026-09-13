import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from "recharts"
import { useMemo } from "react"
import type { ForecastResult } from "@/services/api"

interface Props {
  forecast: ForecastResult
  height?: number
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-xl text-xs font-body">
      <p className="text-slate-500 mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-600">{p.name}:</span>
          <span className="font-semibold" style={{ color: p.color }}>
            ₹{Number(p.value).toFixed(0)}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function CashFlowChart({ forecast, height = 300 }: Props) {
  const data = useMemo(() => {
    // Historical portion
    const hist = forecast.historical_dates.map((d, i) => ({
      date: d.slice(5),  // MM-DD
      historical: forecast.historical[i],
      type: "historical",
    }))

    // Forecast portion — last 90 days only for clarity
    const fc = forecast.forecast_dates.slice(0, 90).map((d, i) => ({
      date: d.slice(5),
      p50: forecast.p50[i],
      p10: forecast.p10[i],
      p90: forecast.p90[i],
      type: "forecast",
    }))

    return [...hist.slice(-120), ...fc]  // last 120 hist days + 90 forecast
  }, [forecast])

  const splitIdx = data.findIndex(d => d.type === "forecast")

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="historicalGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="forecastBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.20} />
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#64748B", fontSize: 10, fontFamily: "DM Sans" }}
            tickLine={false}
            interval={29}
          />
          <YAxis
            tick={{ fill: "#64748B", fontSize: 10, fontFamily: "DM Sans" }}
            tickLine={false}
            tickFormatter={v => `₹${v}`}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: "11px", fontFamily: "DM Sans", color: "#64748B" }}
          />

          {/* Forecast boundary */}
          {splitIdx >= 0 && (
            <ReferenceLine
              x={data[splitIdx]?.date}
              stroke="#CBD5E1"
              strokeDasharray="4 4"
              label={{ value: "Today", fill: "#94A3B8", fontSize: 10, fontFamily: "DM Sans" }}
            />
          )}

          {/* Historical area */}
          <Area
            type="monotone"
            dataKey="historical"
            name="Historical"
            stroke="#3B82F6"
            strokeWidth={2}
            fill="url(#historicalGrad)"
            dot={false}
            activeDot={{ r: 4, fill: "#3B82F6" }}
          />

          {/* Confidence band — p90 */}
          <Area
            type="monotone"
            dataKey="p90"
            name="P90 Forecast"
            stroke="transparent"
            fill="url(#forecastBand)"
            dot={false}
          />

          {/* P50 forecast line */}
          <Line
            type="monotone"
            dataKey="p50"
            name="P50 Forecast"
            stroke="#F59E0B"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={false}
            activeDot={{ r: 4, fill: "#F59E0B" }}
          />

          {/* P10 floor */}
          <Line
            type="monotone"
            dataKey="p10"
            name="P10 (Pessimistic)"
            stroke="#EF4444"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
