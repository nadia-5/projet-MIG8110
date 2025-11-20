from dataclasses import dataclass, field
from typing import Dict, Any 

@dataclass(frozen=True)
class Source:
    filter_statement: str | None
    type: str
    database: str
    schema: str
    table: str
    watermark_column: str
    columns: dict[str, str] = field(default_factory=dict)
    bucket_name: str| None = field(default=None)
    file_name: str| None = field(default=None)
    file_extension: str| None = field(default=None)

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        return cls(
            filter_statement=data.get('filter_statement', None),
            type=data['type'],
            database=data.get('database', None),
            schema=data.get('schema', None),
            table=data.get('table', None),
            watermark_column=data.get('watermark_column', ''),
            columns=data.get('columns', None),
            bucket_name=data.get('bucket_name', None),
            file_name=data.get('file_name', None),
            file_extension=data.get('file_extension', None)
        )
    