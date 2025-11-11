import polars as pl
import s3fs

class Transformation:
    def __init__(self):
        self.fs = s3fs.S3FileSystem(
            key="minio",
            secret="minio123",
            client_kwargs={"endpoint_url": "http://minio:9000"}
        )

    def save_file_path(self, bucket_name: str, base_file: pl.DataFrame, date: str = None) -> str:
        if date is None:
            path_save = f"s3://raw-data/{bucket_name}.parquet"
        else:
            annee = str(date.year).zfill(4)
            mois = str(date.month).zfill(2)
            jour = str(date.day).zfill(2)

            path_save = f"s3://raw-data/{annee}/{mois}/{jour}/{bucket_name}.parquet"

        # Écriture directe dans MinIO
        with self.fs.open(path_save, "wb") as f:
            base_file.write_parquet(f)
            self.fs.close()

    def read_file_path(self, bucket_name: str, file_name: str) -> str:
        path_read = f"s3://{bucket_name}/{file_name}.csv"

        with self.fs.open(path_read, "rb") as f:
            df = pl.read_csv(f)
            self.fs.close()

        return df
    
    def read(self):
        pass

    def transform(self):
        pass

    def write(self):
        pass
    
    def process(self):
        try:
            self.read()
            self.transform()
            self.write()
        except Exception as e:
            print(f"Error processing data: {e}")
