from typing import Generator
import simpy
import logging
import random
from .base_agent import BaseAgent
from cell import Cell, CellType

class WildlifeAgent(BaseAgent):
    """
    Agent representing wildlife populations.
    Basic behaviors:
    - Prefers forest habitats
    - Migrates away from pollution
    - Population affected by resource availability
    """
    GROWTH_RATE = 1.02  # 2% daily growth
    MAX_DENSITY = 400  # maximum wildlife per cell
    MIGRATION_THRESHOLD = 60  # pollution level that triggers migration
    MIGRATION_CHANCE = 0.15  # 15% daily chance to migrate if conditions are poor

    def __init__(self, cell: Cell, config, initial_size: int = None):
        self.cell = cell
        self.config = config
        self.size = initial_size or int(self.MAX_DENSITY * 0.3)  # Default to 30% of max
        self.active = True

    def run(self, env: simpy.Environment) -> Generator:
        """Main process loop using SimPy's generator pattern"""
        while self.active:
            try:
                # Check if conditions are good for growth
                if (self.cell.health_level > 70 and 
                    self.cell.current_pollution_level < 30 and
                    self.cell.resource_level > 50):
                    
                    # Better growth in forest
                    base_growth = self.GROWTH_RATE
                    if self.cell.cell_type == CellType.FOREST:
                        base_growth *= 1.2  # 20% bonus in forest
                        
                    self.size = min(
                        int(self.size * base_growth),
                        self.MAX_DENSITY
                    )
                
                # Consider migration if conditions are poor
                if (self.cell.current_pollution_level > self.MIGRATION_THRESHOLD and
                    random.random() < self.MIGRATION_CHANCE):
                    self._try_migrate()
                
                yield env.timeout(1)  # Wait for next day
                
            except Exception as e:
                logging.error(f"Error in WildlifeAgent process: {str(e)}")
                self.active = False
                break

    def _try_migrate(self):
        """Attempt to migrate to a better cell"""
        best_cell = None
        best_score = float('inf')
        
        for neighbor in self.cell.neighbors:
            # Score based on pollution and habitat type
            score = neighbor.current_pollution_level
            if neighbor.cell_type == CellType.FOREST:
                score *= 0.5  # Prefer forest
            
            if score < best_score:
                best_score = score
                best_cell = neighbor
        
        if best_cell and best_score < self.cell.current_pollution_level:
            # Migrate to better cell
            migration_size = int(self.size * 0.8)  # 80% of population migrates
            self.size -= migration_size
            
            # Create new wildlife population in target cell
            new_wildlife = WildlifeAgent(best_cell, self.config, initial_size=migration_size)
            best_cell.agents.append(new_wildlife)
