from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    data_path: str = "./data/ncr_ride_bookings.csv"
    artifact_dir: str = "./artifacts"
    seed: int = 42
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
