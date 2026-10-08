import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    bucket_name: str
    job_table_name: str
    region: str = "ap-southeast-1"
    expiry_seconds: int = 900
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        bucket = os.environ.get("BUCKET_NAME")
        job_table = os.environ.get("JOB_TABLE_NAME")

        missing_vars = []
        if not bucket:
            missing_vars.append("BUCKET_NAME")
        if not job_table:
            missing_vars.append("JOB_TABLE_NAME")

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        region = os.environ.get("AWS_REGION", "ap-southeast-1")
        raw_expiry = os.environ.get("EXPIRY_SECONDS", "900")
        log_level = os.environ.get("LOG_LEVEL", "INFO")

        try:
            expiry_minutes = int(raw_expiry)
        except ValueError:
            expiry_minutes = 15
        expiry_seconds = expiry_minutes * 60

        return cls(
            bucket_name=bucket,
            job_table_name=job_table,
            region=region,
            expiry_seconds=expiry_seconds,
            log_level=log_level
        )

config = AppConfig.from_env()
