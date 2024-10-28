from typing import Generator
import simpy
import logging
import random
from .base_agent import BaseAgent
from cell import Cell

class PestAgent(BaseAgent):
    """
    Agent representing a pest population.
    Basic behaviors:
    - Thrives in polluted environments
    - Population grows faster in polluted areas
    - Can spread to adjacent cells
    """
    GROWTH_RATE = 1.04  # 4% daily growth
    MAX_DENSITY = 300  # maximum pests per cell
    SPREAD_CHANCE = 0.1  # 10% daily chance to spread

    def __init__(self, cell: Cell, config, initial_size: int = None):
        self.cell = cell
        self.config = config
        self.size = initial_size or int(self.MAX_DENSITY * 0.2)  # Default to 20% of max
        self.active = True

    def run(self, env: simpy.Environment) -> Generator:
        """Main process loop using SimPy's generator pattern"""
        while self.active:
            try:
                # Pests thrive in pollution
                pollution_bonus = 1 + (self.cell.current_pollution_level / 200)  # Up to 50% growth bonus
                growth_rate = self.GROWTH_RATE * pollution_bonus
                
                self.size = min(
                    int(self.size * growth_rate),
                    self.MAX_DENSITY
                )

                # Attempt to spread to adjacent cells
                if random.random() < self.SPREAD_CHANCE:
                    self._try_spread()
                
                yield env.timeout(1)  # Wait for next day
                
            except Exception as e:
                logging.error(f"Error in PestAgent process: {str(e)}")
                self.active = False
                break

    def _try_spread(self):
        """Attempt to spread to adjacent cells"""
        for neighbor in self.cell.neighbors:
            if not any(isinstance(agent, PestAgent) for agent in neighbor.agents):
                # Start new pest population in neighbor cell
                new_pest = PestAgent(neighbor, self.config, initial_size=int(self.size * 0.1))
                neighbor.agents.append(new_pest)
                break
