from pydantic import BaseModel, Field
from enum import Enum

class PopulationType(Enum):
    HUMANS = "humans"
    WILDLIFE = "wildlife"
    FISH = "fish"
    PESTS = "pests"
    TREES = "trees"

class Population(BaseModel):
    type: PopulationType = Field(description="Type of the population")
    size: int = Field(default=0, description="Size of the population")
    health_level: float = Field(default=100.0, description="Health level of the population (0-100)")
    resource_consumption_rate: float = Field(default=0.0, description="Rate at which the population consumes resources")
    pollution_generation_rate: float = Field(default=0.0, description="Rate at which the population generates pollution")

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
