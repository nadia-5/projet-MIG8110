import s3fs 
import polars as pl
from dataclasses import dataclass

from proct_olis.settings import Settings

@dataclass
class Session:
    settings: Settings
    kind: str
    s3: s3fs.S3FileSystem | None = None
    pg_conn: str | None = None

    def __post_init__(self):
        if self.kind == "s3":
            self._init_s3(self.settings.get("minio"))
        elif self.kind == "postgres_operational":
            self._init_postgres(self.settings.get("postgres_operational"))
        elif self.kind == "postgres_datawarehouse":
            self._init_postgres(self.settings.get("postgres_datawarehouse"))

    def _init_postgres(self, config):
        self.pg_conn = f"postgresql://{config.get('user')}:{config.get('password')}@{config.get('host')}:{config.get('port')}/{config.get('database')}"

    def _init_s3(self, config):
        self.s3 = s3fs.S3FileSystem(
            key=config.get("access_key"),
            secret=config.get("secret_key"),
            client_kwargs={"endpoint_url": config.get("endpoint")}
        )