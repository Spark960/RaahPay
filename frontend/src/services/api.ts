import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Borrower {
  id: number
  name: string
  persona_type: 'vendor' | 'farmer' | 'gig_worker'
  base_monthly_income: number
  location: string
  registered_at: string
  status: string
  loan_id?: number
  loan_principal?: number
  base_emi?: number
  risk_tier?: 'low' | 'moderate' | 'high' | 'critical'
  affordability_score?: number
  default_probability?: number
  financial_state?: string
}

export interface ShapExplanation {
  feature: string
  label: string
  shap_value: number
  feature_value: number
  direction: 'risk_increasing' | 'risk_reducing'
  advice: string
}

export interface RiskResult {
  borrower_id: number
  default_probability: number
  risk_tier: string
  affordability_score: number
  financial_state: string
  shap_explanations: ShapExplanation[]
  features: Record<string, number>
}

export interface ForecastResult {
  historical_dates: string[]
  historical: number[]
  forecast_dates: string[]
  p50: number[]
  p10: number[]
  p90: number[]
}

export interface DecompositionResult {
  dates: string[]
  observed: number[]
  trend: number[]
  seasonal: number[]
  residual: number[]
}

export interface RepaymentPeriod {
  period: number
  due_date: string
  dynamic_payment: number
  base_emi: number
  interest_component: number
  principal_component: number
  remaining_balance: number
  adjustment_reason: string
  monthly_forecast_inflow: number
  affordability_ratio: number
}

export interface FixedPeriod {
  period: number
  due_date: string
  fixed_payment: number
  interest_component: number
  principal_component: number
  remaining_balance: number
}

export interface ScheduleComparison {
  loan_id: number
  base_emi: number
  dynamic_schedule: RepaymentPeriod[]
  fixed_schedule: FixedPeriod[]
  summary: {
    dynamic_total: number
    fixed_total: number
    dynamic_periods: number
    fixed_periods: number
  }
}

export interface StressTestResult {
  shock: { pct: number; duration_days: number }
  dynamic_schedule: RepaymentPeriod[]
  fixed_schedule: FixedPeriod[]
  summary: {
    dynamic_total_paid: number
    fixed_total_due: number
    fixed_missed_payments: number
    fixed_missed_periods: number[]
    dynamic_stressed_periods: number[]
    dynamic_missed_payments: number
    savings_from_dynamic: number
  }
  monthly_inflows: number[]
}

export interface AlertResult {
  is_stressed: boolean
  current_cusum: number
  threshold: number
  alerts: Array<{
    type: string
    date: string
    severity: string
    cusum_value: number
    message: string
  }>
  cusum_series: Array<{ date: string; value: number }>
}

// ─── API calls ────────────────────────────────────────────────────────────────

export const getBorrowers = () => api.get<Borrower[]>('/borrowers/').then(r => r.data)
export const getBorrower = (id: number) => api.get<Borrower>(`/borrowers/${id}`).then(r => r.data)
export const getCashFlow = (id: number) => api.get(`/borrowers/${id}/cashflow`).then(r => r.data)
export const getDecomposition = (id: number) => api.get<DecompositionResult>(`/borrowers/${id}/cashflow/decomposition`).then(r => r.data)
export const getForecast = (id: number, horizon = 90) => api.get<ForecastResult>(`/borrowers/${id}/cashflow/forecast?horizon=${horizon}`).then(r => r.data)
export const getRisk = (id: number) => api.get<RiskResult>(`/borrowers/${id}/risk`).then(r => r.data)
export const getAlerts = (id: number) => api.get<AlertResult>(`/borrowers/${id}/alerts`).then(r => r.data)
export const getScheduleComparison = (loanId: number) => api.get<ScheduleComparison>(`/loans/${loanId}/schedule/comparison`).then(r => r.data)
export const runStressTest = (body: { borrower_id: number; shock_pct: number; shock_duration_days: number }) =>
  api.post<StressTestResult>('/simulate/stress-test', body).then(r => r.data)
