
from dataclasses import dataclass
from typing import Dict, Any 
from proct_olis.core.source import Source
from proct_olis.core.destination import Destination
import yaml
from string import Template

@dataclass(frozen=True)
class Config:
    destination: Destination
    sources: dict[str, Source]
    operational_sources: dict[str, Source] = None
    datawarehouse_sources: dict[str, Source] = None
    datalake_sources: dict[str, Source] = None

    @classmethod
    def load_config(cls, path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        sources = {name: Source.from_data(src) for name, src in data.get('sources', {}).items()}
        operational_sources = {name: Source.from_data(src) for name, src in data.get('sources', {}).items() if src['type'] == 'postgres_operational'}
        datawarehouse_sources = {name: Source.from_data(src) for name, src in data.get('sources', {}).items() if src['type'] == 'postgres_datawarehouse'}
        datalake_sources = {name: Source.from_data(src) for name, src in data.get('sources', {}).items() if src['type'] == 's3'}
        destination = Destination.from_data(data['destination'])
        
        return cls(
            destination=destination,
            sources=sources,
            operational_sources=operational_sources,
            datawarehouse_sources=datawarehouse_sources,
            datalake_sources=datalake_sources
        )
    

    
class JsonTemplate(Template):
    delimiter = "{{"
    pattern = r"""
    \$\{(?:
    (?P<escaped>\$\{)|
    (?P<named>[_a-z][_a-z0-9]*)\}|
    (?P<braced>[_a-z][_a-z0-9]*)\}|
    (?P<invalid>)
    )
    """