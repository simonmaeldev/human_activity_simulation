from typing import List
from .base_manager import BaseCellManager
from cell import Cell, CellType
from population import Population, PopulationType
from constants import LAND_TO_FOREST_DAYS

class LandManager(BaseCellManager):
    """Manages land cells and their specific behaviors"""
    
    def calculate_food_production(self, cell: Cell) -> float:
        """Calculate food resource production"""
        base_rate = self.config.resource_regeneration_rates["land"]
        health_factor = cell.health_level / 100
        pollution_factor = 1 - (cell.current_pollution_level / 100)
        return base_rate * health_factor * pollution_factor
    
    def manage_pest_population(self, cell: Cell) -> None:
        """Manage pest population growth/decline"""
        pest_pop = next((p for p in cell.populations 
                        if p.type == PopulationType.PESTS), None)
        if not pest_pop:
            return
            
        # Pests thrive in polluted environments
        growth_factor = 1 + (cell.current_pollution_level / 200)  # Max 50% increase
        pest_pop.size = int(pest_pop.size * growth_factor)
    
    def can_convert_to(self, cell: Cell, target_type: CellType) -> bool:
        """Check if land can be converted to other types"""
        if cell.cell_type != CellType.LAND:
            return False
            
        if target_type == CellType.CITY:
            return (cell.health_level > self.config.health_thresholds["good"] and
                    cell.resource_level > self.config.cell_conversion_thresholds["land_to_city"])
        elif target_type == CellType.FOREST:
            return (cell.health_level > self.config.health_thresholds["good"] and
                    getattr(cell, 'days_unused', 0) >= LAND_TO_FOREST_DAYS)
        return False
