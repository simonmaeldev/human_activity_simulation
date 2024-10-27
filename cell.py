from pydantic import BaseModel, Field, field_validator
from typing import List, Tuple
from enum import Enum
from population import Population

class CellType(Enum):
    CITY = "city"
    FOREST = "forest"
    LAKE = "lake"
    LAND = "land"

class Cell(BaseModel):
    """Base class for all environment cells"""
    position: Tuple[int, int] = Field(..., description="Position of the cell in the grid as (x, y)")
    cell_type: CellType = Field(..., description="Type of the cell")
    air_pollution_level: float = Field(default=0.0, description="Current air pollution level in the cell")
    ground_pollution_level: float = Field(default=0.0, description="Current ground pollution level in the cell")
    health_level: float = Field(default=100.0, description="Health level of the cell (0-100)")
    populations: List[Population] = Field(default_factory=list, description="List of populations in the cell")
    resource_level: float = Field(default=100.0, description="Resource level in the cell")

    @property
    def current_pollution_level(self) -> float:
        """Calculate total pollution level"""
        return (self.air_pollution_level + self.ground_pollution_level) / 2

    @field_validator('health_level')
    def validate_health(cls, v):
        """Ensure health level stays between 0 and 100"""
        return max(0.0, min(100.0, v))

    @field_validator('air_pollution_level', 'ground_pollution_level')
    def validate_pollution(cls, v):
        """Ensure pollution levels are non-negative"""
        return max(0.0, v)

    @field_validator('resource_level')
    def validate_resources(cls, v):
        """Ensure resource level stays between 0 and 100"""
        return max(0.0, min(100.0, v))

class CityCell(Cell):
    """Specialized cell type for cities"""
    def __init__(self, **data):
        super().__init__(cell_type=CellType.CITY, **data)

class ForestCell(Cell):
    """Specialized cell type for forests"""
    def __init__(self, **data):
        super().__init__(cell_type=CellType.FOREST, **data)

class LakeCell(Cell):
    """Specialized cell type for lakes"""
    def __init__(self, **data):
        super().__init__(cell_type=CellType.LAKE, **data)

class LandCell(Cell):
    """Specialized cell type for land"""
    def __init__(self, **data):
        super().__init__(cell_type=CellType.LAND, **data)

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
