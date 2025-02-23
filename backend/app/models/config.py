from pydantic import BaseModel
from typing import Dict, Any, List

class VariableConfig(BaseModel):
    name: str
    value: Any

class ConfigRequest(BaseModel):
    namespace_uri: str
    variables: Dict[str, Any]

class ConfigResponse(BaseModel):
    status: str
    config: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class NamespaceConfig(BaseModel):
    namespace: str
    variables: list[VariableConfig]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True