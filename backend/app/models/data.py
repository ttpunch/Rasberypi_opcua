from pydantic import BaseModel
from typing import Dict, Any

class DataUpdate(BaseModel):
    variable: str
    value: Any

class DataResponse(BaseModel):
    status: str
    data: Dict[str, Any]

class UpdateResponse(BaseModel):
    status: str
    message: str

    class Config:
        arbitrary_types_allowed = True