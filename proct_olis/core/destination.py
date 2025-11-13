from dataclasses import dataclass
from typing import Dict, Any 

@dataclass(frozen=True)
class Destination:
    table: str 
    schema: str 
    database: str
    destination_type: str
    primary_key: str | None
    business_keys: list[str] | None = None
    kind: str | None = None
    bucket_name: str | None = None
    file_name: str | None = None
    date_bucket: str | None = None

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        return cls(
            table=data.get('table', None),
            schema=data.get('schema', None),
            database=data.get('database', None),
            destination_type=data.get('destination_type', None),
            primary_key=data.get('primary_key', None),
            business_keys=data.get('business_keys', None),
            kind=data.get('kind', None),
            bucket_name=data.get('bucket_name', None),
            file_name=data.get('file_name', None),
            date_bucket=data.get('date_bucket', None)
        )