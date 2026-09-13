import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(val: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(val)
}

export function formatPercent(val: number, decimals = 1) {
  return `${(val * 100).toFixed(decimals)}%`
}

/** Light-mode–safe text colors for risk tiers */
export function riskColor(tier: string) {
  const map: Record<string, string> = {
    low:      "text-emerald-700",
    moderate: "text-amber-600",
    high:     "text-orange-600",
    critical: "text-red-600",
  }
  return map[tier] ?? "text-slate-500"
}

/** Light-mode badge classes (defined in index.css) */
export function riskBgClass(tier: string) {
  const map: Record<string, string> = {
    low:      "badge-low",
    moderate: "badge-moderate",
    high:     "badge-high",
    critical: "badge-critical",
  }
  return map[tier] ?? "bg-slate-100 text-slate-600 border border-slate-200"
}

export function personaLabel(type: string) {
  const map: Record<string, string> = {
    vendor:     "Retail Merchant",
    farmer:     "Agri-Business",
    gig_worker: "Platform Worker",
  }
  return map[type] ?? type
}

/** Premium gradient backgrounds for avatars */
export function personaGradient(type: string) {
  const map: Record<string, string> = {
    vendor:     "from-violet-500 to-purple-700",
    farmer:     "from-emerald-500 to-teal-700",
    gig_worker: "from-sky-500 to-indigo-700",
  }
  return map[type] ?? "from-slate-500 to-slate-700"
}

/** Get initials for avatar */
export function getInitials(name: string) {
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

/** Light-mode–safe text colors for financial state */
export function financialStateColor(state: string) {
  const map: Record<string, string> = {
    thriving:     "text-emerald-700",
    stable:       "text-blue-700",
    recovering:   "text-sky-700",
    stressed:     "text-amber-700",
    deteriorating: "text-red-600",
  }
  return map[state] ?? "text-slate-500"
}
