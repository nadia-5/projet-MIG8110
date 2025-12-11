from proct_olis.core import TransformationBase
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Dim Date Generation"

    def transformation(self):
        # Génération d'une plage de dates (ex: 2016 à 2020)
        # Note : Pour une prod, on ajuste les bornes dynamiquement ou on fixe large
        start_date = "2016-01-01"
        end_date = "2020-12-31"
        
        date_range = pl.date_range(
            start=pl.date(2016, 1, 1),
            end=pl.date(2020, 12, 31),
            interval="1d",
            eager=True
        ).alias("date_value")

        df = pl.DataFrame({"date_value": date_range})

        self.final_df = df.select([
            # date_sk au format YYYYMMDD (ex: 20160101)
            pl.col("date_value").dt.strftime("%Y%m%d").cast(pl.Int32).alias("date_sk"),
            pl.col("date_value"),
            pl.col("date_value").dt.year().alias("year"),
            pl.col("date_value").dt.quarter().alias("quarter"),
            pl.col("date_value").dt.month().alias("month"),
            pl.col("date_value").dt.day().alias("day"),
            pl.col("date_value").dt.week().alias("week_of_year"),
            pl.col("date_value").dt.weekday().alias("day_of_week"),
            # Est-ce un weekend ? (Samedi=6, Dimanche=7)
            (pl.col("date_value").dt.weekday() >= 6).alias("is_weekend"),
            pl.lit("hash_placeholder").alias("rowhash")
        ])