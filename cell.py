from pydantic import BaseModel, Field
from typing import List, Tuple, TYPE_CHECKING
from enum import Enum

class CellType(Enum):
    CITY = "city"
    FOREST = "forest"
    LAKE = "lake"
    LAND = "land"

if TYPE_CHECKING:
    from population import Population
    position: Tuple[int, int] = Field(description="Position of the cell in the grid as (x, y)")
    cell_type: CellType = Field(description="Type of the cell")
    current_pollution_level: float = Field(default=0.0, description="Current pollution level in the cell")
    health_level: float = Field(default=100.0, description="Health level of the cell (0-100)")
    populations: List['Population'] = Field(default_factory=list, description="List of populations in the cell")
    resource_level: float = Field(default=0.0, description="Resource level in the cell")

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
