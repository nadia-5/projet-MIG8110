import polars as pl
from proct_olis.core.config import Config
from proct_olis.core.session import Session
from proct_olis.settings import Settings
from abc import ABC, abstractmethod
from proct_olis.core.utilities import Utilities
from datetime import datetime
from typing import Optional


class WritterBase(ABC):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        self.process_name = process_name
        self.destination = config.destination
        self.settings = settings
        self.df = df
        self.execution_date = execution_date
        self.utilities = Utilities()
        
        if execution_date:
            self.current_datetime = datetime.strptime(execution_date, "%Y-%m-%d")
        else:
            self.current_datetime = datetime.now()

    @abstractmethod
    def write(self):
        raise NotImplementedError


class S3Writter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        super().__init__(process_name, config, settings, df, execution_date)
        self.fs = Session(settings, self.destination.destination_type).s3

    def write(self) -> None:
        if self.destination.file_name.startswith("common/"):
             path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"
        
        elif self.execution_date:
            path_save = f"s3://{self.destination.bucket_name}/daily_data/{self.execution_date}/{self.destination.file_name}"
        
        elif self.destination.date_bucket:
            date = pl.Date.strptime(self.destination.date_bucket, fmt="%Y-%m-%d").to_python_date()
            annee = str(date.year).zfill(4)
            mois = str(date.month).zfill(2)
            jour = str(date.day).zfill(2)
            path_save = f"s3://{self.destination.bucket_name}/{annee}/{mois}/{jour}/{self.destination.file_name}"
        
        else:
            path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"

        print(f"Writing S3: {path_save}")
        
        with self.fs.open(path_save, "wb") as f:
            self.df.write_parquet(f)


class tableWritter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        super().__init__(process_name, config, settings, df, execution_date)
        self.pg_conn = Session(self.settings, kind=self.destination.destination_type).pg_conn
    
    def append_table(self) -> None:
        query = f"SELECT * FROM {self.destination.schema}.{self.destination.table}"
        
        try:
            historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception:
            historical_df = pl.DataFrame(schema=self.df.schema)

        if self.destination.business_keys:
            business_keys = self.destination.business_keys
        else:
            excluded_columns = [self.destination.primary_key, "inserted_at", "updated_at"]
            if not historical_df.is_empty():
                business_keys = [col for col in historical_df.columns if col not in excluded_columns]
            else:
                business_keys = [col for col in self.df.columns if col not in excluded_columns]
    
        if not historical_df.is_empty():
            destination_table = self.utilities.calculate_hash_based_on_columns(historical_df, business_keys)
            current_df = self.utilities.calculate_hash_based_on_columns(self.df, business_keys)
            
            df_to_insert = current_df.join(destination_table, on="hash_key", how="anti")
        else:
            df_to_insert = self.df

        print(f"Number of new rows to insert: {df_to_insert.height}")

        if "inserted_at" not in df_to_insert.columns:
            df_to_insert = df_to_insert.with_columns(
                pl.lit(self.current_datetime).alias("inserted_at")
            )

        if not df_to_insert.is_empty():
            cols_to_drop = ["hash_key"] if "hash_key" in df_to_insert.columns else []
            
            df_to_insert.drop(cols_to_drop).write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append"
            )

    def write(self) -> None:
        if self.destination.kind == "append":
            self.append_table()


class Writter:
    def __init__(self, process_name: str, df: pl.DataFrame, config: Config, settings: Settings, execution_date: Optional[str] = None):
        self.process_name = process_name
        self.config = config
        self.settings = settings
        self.df = df
        self.execution_date = execution_date

    def write(self) -> None:
        if self.config.destination.destination_type == "s3":
            S3Writter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()
        elif self.config.destination.destination_type == "postgres_operational":
            tableWritter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()
        elif self.config.destination.destination_type == "postgres_datawarehouse":
            tableWritter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()

class SCD2Writter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        super().__init__(process_name, config, settings, df, execution_date)
        self.pg_conn = Session(self.settings, kind=self.destination.destination_type).pg_conn

    def write(self) -> None:
        print(f"🔄 Exécution du SCD Type 2 pour {self.destination.table}...")
        
        # 1. Lire la dimension actuelle (seulement les lignes actives)
        query = f"SELECT * FROM {self.destination.schema}.{self.destination.table} WHERE is_current = TRUE"
        try:
            current_dim_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except:
            current_dim_df = pl.DataFrame(schema=self.df.schema)

        # 2. Identifier les Business Keys (ex: customer_id)
        bk_cols = self.destination.business_keys
        
        # 3. Calculer les Hashes pour comparaison
        # Le hash doit inclure les colonnes qui déclenchent une nouvelle version (ex: ville, état)
        # On exclut les colonnes techniques (valid_from, valid_to, is_current, pk)
        tech_cols = ["valid_from", "valid_to", "is_current", self.destination.primary_key, "rowhash"]
        attr_cols = [c for c in self.df.columns if c not in tech_cols and c not in bk_cols]
        
        incoming_df = self.utilities.calculate_hash_based_on_columns(self.df, attr_cols)
        
        # Si la table cible est vide, tout est nouveau
        if current_dim_df.is_empty():
            self._insert_new_rows(self.df)
            return

        # 4. Comparaison (Source vs Target)
        # On joint sur les Business Keys
        joined = incoming_df.join(
            current_dim_df.select(bk_cols + ["rowhash"]).rename({"rowhash": "existing_hash"}),
            on=bk_cols,
            how="left"
        )

        # Nouveaux : Ceux qui n'ont pas de match dans le DW
        new_records = joined.filter(pl.col("existing_hash").is_null())
        
        # Modifiés : Ceux qui match mais ont un hash différent
        changed_records = joined.filter(
            (pl.col("existing_hash").is_not_null()) & 
            (pl.col("hash_key") != pl.col("existing_hash"))
        )

        # 5. Application des changements
        if not new_records.is_empty():
            print(f"➕ {new_records.height} nouvelles lignes.")
            self._insert_new_rows(new_records.select(self.df.columns))

        if not changed_records.is_empty():
            print(f"🔄 {changed_records.height} lignes modifiées (Historisation).")
            # A. Fermer les anciennes lignes (Update valid_to)
            self._close_old_records(changed_records, bk_cols)
            # B. Insérer les nouvelles versions
            self._insert_new_rows(changed_records.select(self.df.columns))

    def _insert_new_rows(self, df: pl.DataFrame):
        # Prépare les colonnes SCD2
        df_to_load = df.with_columns([
            pl.lit(self.current_datetime).alias("valid_from"),
            pl.lit(None, dtype=pl.Datetime).alias("valid_to"),
            pl.lit(True).alias("is_current"),
            # Calcul du hash final si pas déjà fait
            # ...
        ])
        # Insert...
        df_to_load.write_database(
            table_name=f"{self.destination.schema}.{self.destination.table}",
            connection=self.pg_conn,
            if_table_exists="append"
        )

    def _close_old_records(self, df_changed: pl.DataFrame, bk_cols):
        # Construit une liste d'ID à fermer
        # C'est ici qu'on fait l'UPDATE SQL
        # "UPDATE dim_xxx SET is_current = False, valid_to = NOW() WHERE business_key IN (...)"
        pass