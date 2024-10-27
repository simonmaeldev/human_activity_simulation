from typing import List
from .base_agent import BaseAgent
from cell import Cell, CellType
from constants import MAX_HUMAN_DENSITY

class HumanAgent(BaseAgent):
    """
    Agent class representing human decision-making behavior.
    Implements resource management, migration, and cell conversion logic.
    """
    def make_decisions(self) -> List[str]:
        decisions = []
        
        # Check if current cell is overcrowded
        if self.population.size > MAX_HUMAN_DENSITY:
            if self._try_expansion():
                decisions.append("expanded_to_new_cell")
                
        # Evaluate resource consumption strategy
        if self.cell.resource_level < 30:  # Resource stress
            if self._try_resource_optimization():
                decisions.append("optimized_resources")
                
        # Consider migration if conditions are poor
        if self.cell.health_level < 40 or self.cell.current_pollution_level > 70:
            if self._try_migration():
                decisions.append("migrated")
                
        return decisions
        
    def _try_expansion(self) -> bool:
        """Attempt to expand to neighboring land"""
        for neighbor in self.cell.neighbors:
            if (neighbor.cell_type == CellType.LAND and
                self.evaluate_cell_quality(neighbor) > 0.6):
                neighbor.cell_type = CellType.CITY
                return True
        return False
        
    def _try_resource_optimization(self) -> bool:
        """Optimize resource consumption and pollution generation"""
        if self.population.resource_consumption_rate > 0.5:
            self.population.resource_consumption_rate *= 0.9
            self.population.pollution_generation_rate *= 0.9
            return True
        return False
        
    def _try_migration(self) -> bool:
        """Attempt to migrate to better conditions"""
        best_neighbor = self.find_best_neighbor(self.cell.neighbors)
        if best_neighbor and self.evaluate_cell_quality(best_neighbor) > self.evaluate_cell_quality(self.cell):
            # Move 20% of population to new cell
            migration_size = int(self.population.size * 0.2)
            self.population.size -= migration_size
            # Add migrated population to target cell
            # This would need to be handled by the population manager
            return True
        return False
