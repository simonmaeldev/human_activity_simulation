from typing import Generator
import simpy
import logging
from .base_agent import BaseAgent
from cell import Cell

class FishAgent(BaseAgent):
    """
    Agent representing a fish population in a lake cell.
    Basic behaviors:
    - Population grows over time (3% daily)
    - Requires clean water to thrive
    - Dies quickly in polluted water
    """
    GROWTH_RATE = 1.03  # 3% daily growth
    MAX_DENSITY = 800  # maximum fish per lake cell
    POLLUTION_SENSITIVITY = 0.2  # Higher values mean more sensitive to pollution

    def __init__(self, cell: Cell, config, initial_size: int = None):
        self.cell = cell
        self.config = config
        self.size = initial_size or int(self.MAX_DENSITY * 0.4)  # Default to 40% of max
        self.active = True

    def run(self, env: simpy.Environment) -> Generator:
        """Main process loop using SimPy's generator pattern"""
        while self.active:
            try:
                # Population affected by water pollution
                pollution_impact = self.cell.current_pollution_level * self.POLLUTION_SENSITIVITY
                if pollution_impact > 50:  # High pollution causes population decline
                    self.size = int(self.size * 0.9)  # 10% death rate in polluted water
                elif self.cell.health_level > 70:  # Good conditions allow growth
                    self.size = min(
                        int(self.size * self.GROWTH_RATE),
                        self.MAX_DENSITY
                    )
                
                yield env.timeout(1)  # Wait for next day
                
            except Exception as e:
                logging.error(f"Error in FishAgent process: {str(e)}")
                self.active = False
                break
