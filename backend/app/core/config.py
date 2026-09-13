from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite:///./data/demo.db"
    sweep_alpha: float = 0.20          # % of net discretionary inflow to sweep
    min_payment_factor: float = 0.50   # floor = 50% of base EMI (interest-only approx)
    max_payment_factor: float = 1.50   # ceiling = 150% of base EMI
    cusum_threshold: float = 3.0       # CUSUM stress threshold (σ units)
    forecast_horizon_days: int = 90


settings = Settings()
