from dataclasses import dataclass
from datetime import datetime
import polars as pl

from proct_olis.core.session import Session
from proct_olis.settings import Settings

@dataclass
class Watermark:
    settings: Settings
    
    def __post_init__(self):
        self.connection_string = Session(self.settings, kind="postgres_datawarehouse").pg_conn

    def get_watermark(self, source_name: str, destination_name: str, watermark_column: str) -> datetime | None:
        """
        Retrieves the last watermark value for a given source and destination.
        Returns None if no watermark exists.
        """
        query = f"""
            SELECT last_value 
            FROM watermark 
            WHERE source_name = '{source_name}' 
              AND destination_name = '{destination_name}' 
              AND watermark_column = '{watermark_column}'
        """
        try:
            df = pl.read_database_uri(query=query, uri=self.connection_string)
            
            if df.is_empty():
                return None
                
            value = df["last_value"][0]
            return value
        except Exception as e:
            print(f"Error reading watermark: {e}")
            return None

    def set_watermark(self, source_name: str, destination_name: str, watermark_column: str, last_value: datetime):
        """
        Updates or inserts the watermark value for a given source and destination using Polars.
        Since Polars write_database doesn't support generic UPSERT, we use a Read-Modify-Replace strategy.
        """
        try:
            # 1. Read the full table
            # We need to read everything to preserve other watermarks when replacing
            query = "SELECT * FROM watermark"
            try:
                current_df = pl.read_database_uri(query=query, uri=self.connection_string)
            except Exception:
                # Table might not exist yet or be empty/error, assume empty schema
                current_df = pl.DataFrame(schema={
                    "source_name": pl.Utf8,
                    "destination_name": pl.Utf8,
                    "watermark_column": pl.Utf8,
                    "last_value": pl.Datetime
                })

            # 2. Create the new record DataFrame
            new_record = pl.DataFrame({
                "source_name": [source_name],
                "destination_name": [destination_name],
                "watermark_column": [watermark_column],
                "last_value": [last_value]
            }) # Ensure types match if necessary, mainly last_value as datetime

            # 3. Filter out the old record for this source/dest if it exists
            if not current_df.is_empty():
                updated_df = current_df.filter(
                    ~((pl.col("source_name") == source_name) & (pl.col("destination_name") == destination_name))
                )
                # Append the new record
                final_df = pl.concat([updated_df, new_record], how="vertical")
            else:
                final_df = new_record

            # 4. Write back to the database replacing the table
            # distinct() ensures we don't introduce duplicates if logic above failed somehow
            final_df.unique(subset=["source_name", "destination_name"]).write_database(
                table_name="watermark",
                connection=self.connection_string,
                if_table_exists="replace"
            )
            
        except Exception as e:
            print(f"Error setting watermark: {e}")
            raise e
