from pydantic import BaseModel, Field
from typing import Dict, Any


class HealthCheckResponse(BaseModel):
    status: str
    environment: str
    version: str = "1.0.0"
    database: str
    redis: str
    details: Dict[str, Any] = {}
