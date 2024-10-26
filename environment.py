import simpy
import random
from typing import List, Tuple
from cell import Cell, CellType
from config_model import ConfigModel
from population_processes import PopulationManager
from resource_manager import ResourceManager
from pollution_manager import PollutionManager

class Environment:
    def __init__(self, config: ConfigModel):
        self.env = simpy.Environment()
        self.grid = self._initialize_grid(config.grid_size)
        self.config = config
        self.population_manager = PopulationManager(self.env, config)
        self.resource_manager = ResourceManager(config)
        self.pollution_manager = PollutionManager(config)

    def _initialize_grid(self, grid_size: Tuple[int, int]) -> List[List[Cell]]:
        return [[Cell(position=(x, y), cell_type=random.choice(list(CellType))) 
                for y in range(grid_size[1])] 
                for x in range(grid_size[0])]

    def get_neighbors(self, x: int, y: int) -> List[Cell]:
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]):
                neighbors.append(self.grid[nx][ny])
        return neighbors

    def update_environment(self):
        """Update environment state for one time step"""
        # Handle pollution spread
        self.pollution_manager.spread_pollution(self.grid)
        
        # Regenerate resources
        for row in self.grid:
            for cell in row:
                self.resource_manager.regenerate_resources(cell)


    def track_global_statistics(self):
        total_pollution = sum(cell.current_pollution_level for row in self.grid for cell in row)
        total_health = sum(cell.health_level for row in self.grid for cell in row)
        return {
            "total_pollution": total_pollution,
            "average_health": total_health / (len(self.grid) * len(self.grid[0]))
        }
