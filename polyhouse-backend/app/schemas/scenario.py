from uuid import UUID
from pydantic import BaseModel


class ApplyStrategyRequest(BaseModel):
    polyhouse_id: UUID
    strategy: str