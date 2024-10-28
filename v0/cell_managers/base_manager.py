from typing import Optional, List
from cell import Cell, CellType
from config_model import ConfigModel
from population import Population

class BaseCellManager:
    """Base class for specialized cell managers"""
    
    def __init__(self, config: ConfigModel):
        self.config = config
    
    def can_convert_to(self, cell: Cell, target_type: CellType) -> bool:
        """Check if cell can be converted to target type"""
        return False
    
    def convert_cell(self, cell: Cell, target_type: CellType) -> bool:
        """Convert cell to new type if possible"""
        if self.can_convert_to(cell, target_type):
            cell.cell_type = target_type
            return True
        return False
    
    def calculate_health_impact(self, cell: Cell) -> float:
        """Calculate health impact based on cell conditions"""
        pollution_impact = -(cell.air_pollution_level + cell.ground_pollution_level) / 100
        resource_factor = cell.resource_level / 100
        return pollution_impact + resource_factor
