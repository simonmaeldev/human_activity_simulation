from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_agent import BaseAgent

class Resource(BaseModel):
    """Represents a resource that can be consumed by agents"""
    name: str
    quantity: float
    quality: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional["BaseAgent"] = None
    
    class Config:
        arbitrary_types_allowed = True
