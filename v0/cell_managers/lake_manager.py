from typing import List
from .base_manager import BaseCellManager
from cell import Cell, CellType
from population import Population, PopulationType

class LakeManager(BaseCellManager):
    """Manages lake cells and their specific behaviors"""
    
    def calculate_water_regeneration(self, cell: Cell) -> float:
        """Calculate water resource regeneration rate"""
        base_rate = self.config.resource_regeneration_rates["lake"]
        pollution_factor = 1 - (cell.current_pollution_level / 100)
        return base_rate * pollution_factor
    
    def calculate_pollution_dilution(self, cell: Cell) -> float:
        """Calculate pollution dilution effect"""
        base_dilution = 0.1  # 10% dilution per day
        health_factor = cell.health_level / 100
        return base_dilution * health_factor
    
    def calculate_fish_capacity(self, cell: Cell) -> int:
        """Calculate maximum fish population cell can support"""
        base_capacity = 1000  # Base fish capacity
        health_factor = cell.health_level / 100
        pollution_factor = 1 - (cell.current_pollution_level / 100)
        return int(base_capacity * health_factor * pollution_factor)
    
    def can_convert_to(self, cell: Cell, target_type: CellType) -> bool:
        """Lakes cannot be converted to other types"""
        return False
