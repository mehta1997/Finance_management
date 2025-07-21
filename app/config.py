from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "FinanceFlow - Personal Wealth Manager"
    version: str = "2.1.0"
    debug: bool = False
    database_url: str = "sqlite:///./financeflow_db.db"
    secret_key: str = "financeflow_secure_jwt_secret_2024_nabhi_dev"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 45
    
    # Additional custom settings
    max_transaction_limit: float = 999999.99
    currency: str = "USD"
    timezone: str = "UTC"
    enable_analytics: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
