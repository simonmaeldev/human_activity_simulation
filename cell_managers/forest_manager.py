from typing import List
from .base_manager import BaseCellManager
from cell import Cell, CellType
from population import Population, PopulationType
from constants import (
    TREE_CO2_ABSORPTION_FACTOR, 
    FOREST_SPREAD_CHANCE,
    MAX_TREE_DENSITY
)

class ForestManager(BaseCellManager):
    """Manages forest cells and their specific behaviors"""
    
    def calculate_co2_absorption(self, cell: Cell) -> float:
        """Calculate CO2 absorption by trees"""
        tree_pop = next((p for p in cell.populations 
                        if p.type == PopulationType.TREES), None)
        if not tree_pop:
            return 0.0
            
        health_factor = tree_pop.health_level / 100
        density_factor = tree_pop.size / MAX_TREE_DENSITY
        return TREE_CO2_ABSORPTION_FACTOR * health_factor * density_factor
    
    def calculate_wildlife_capacity(self, cell: Cell) -> int:
        """Calculate maximum wildlife population cell can support"""
        base_capacity = MAX_TREE_DENSITY // 10  # 10% of max tree density
        health_factor = cell.health_level / 100
        resource_factor = cell.resource_level / 100
        return int(base_capacity * health_factor * resource_factor)
    
    def can_convert_to(self, cell: Cell, target_type: CellType) -> bool:
        """Check conversion possibilities"""
        if cell.cell_type == CellType.LAND and target_type == CellType.FOREST:
            return cell.health_level > self.config.health_thresholds["good"]
        elif cell.cell_type == CellType.FOREST and target_type == CellType.LAND:
            return True  # Deforestation is always possible
        return False
