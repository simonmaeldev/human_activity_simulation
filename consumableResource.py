from pydantic import BaseModel, Field

class Resource(BaseModel):
    """Represents a resource that can be consumed by agents"""
    name: str
    quantity: float
    quality: float = Field(default=1.0, ge=0.0, le=1.0)
    
    class Config:
        arbitrary_types_allowed = True
