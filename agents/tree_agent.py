from typing import List
import logging
from .base_agent import BaseAgent
from cell import Cell, CellType
from constants import MAX_TREE_DENSITY, FOREST_SPREAD_CHANCE
import random

class TreeAgent(BaseAgent):
    """
    Agent class representing tree/forest behavior.
    Implements natural spread and resource optimization.
    """
    def make_decisions(self) -> List[str]:
        decisions = []
        
        # Check forest health and density
        if self.population.size > MAX_TREE_DENSITY * 0.8:  # Near capacity
            if self._try_spread():
                decisions.append("spread_to_new_cell")
                
        # Optimize resource usage based on conditions
        if self.cell.resource_level < 40:
            if self._adjust_resource_consumption():
                decisions.append("reduced_consumption")
                
        # Respond to high pollution
        if self.cell.current_pollution_level > 60:
            if self._increase_co2_absorption():
                decisions.append("increased_absorption")
                
        return decisions
        
    def _try_spread(self) -> bool:
        """Attempt to spread to neighboring land"""
        for neighbor in self.cell.neighbors:
            if (neighbor.cell_type == CellType.LAND and
                random.random() < FOREST_SPREAD_CHANCE and
                self.evaluate_cell_quality(neighbor) > 0.5):
                neighbor.cell_type = CellType.FOREST
                logging.info(
                    f"Forest spread: Trees expanded from cell {self.cell.position} "
                    f"to new forest cell {neighbor.position}"
                )
                return True
        return False
        
    def _adjust_resource_consumption(self) -> bool:
        """Adjust resource consumption based on availability"""
        if self.population.resource_consumption_rate > 0.3:
            self.population.resource_consumption_rate *= 0.8
            return True
        return False
        
    def _increase_co2_absorption(self) -> bool:
        """Increase CO2 absorption rate to combat pollution"""
        if self.population.health_level > 60:
            # Trees can temporarily increase absorption at health cost
            self.population.health_level -= 5
            return True
        return False
