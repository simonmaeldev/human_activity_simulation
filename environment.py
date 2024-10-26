import simpy
import random
from typing import List, Tuple
from cell import Cell, CellType
from config_model import ConfigModel
from population_processes import PopulationManager

class Environment:
    def __init__(self, config: ConfigModel):
        self.env = simpy.Environment()
        self.grid = self._initialize_grid(config.grid_size)
        self.global_co2_level = config.initial_co2_level
        self.config = config
        self.population_manager = PopulationManager(self.env, config)

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

    def calculate_pollution_spread(self):
        # Create temporary grids for new pollution levels
        new_air_pollution = [[0.0 for _ in range(len(self.grid[0]))] for _ in range(len(self.grid))]
        new_ground_pollution = [[0.0 for _ in range(len(self.grid[0]))] for _ in range(len(self.grid))]
        
        AIR_SPREAD_RATE = 0.4  # Air pollution spreads faster
        GROUND_SPREAD_RATE = 0.1  # Ground pollution spreads slower
        AIR_TO_GROUND_RATE = 0.2  # Rate at which air pollution settles into ground
        
        # Calculate pollution diffusion for each cell
        for x, row in enumerate(self.grid):
            for y, cell in enumerate(row):
                neighbors = self.get_neighbors(x, y)
                if not neighbors:
                    continue
                    
                # Air pollution spread
                air_outflow = cell.air_pollution_level * AIR_SPREAD_RATE
                air_per_neighbor = air_outflow / len(neighbors)
                new_air_pollution[x][y] = cell.air_pollution_level - air_outflow
                
                # Ground pollution spread
                ground_outflow = cell.ground_pollution_level * GROUND_SPREAD_RATE
                ground_per_neighbor = ground_outflow / len(neighbors)
                new_ground_pollution[x][y] = cell.ground_pollution_level - ground_outflow
                
                # Distribute to neighbors
                for neighbor in neighbors:
                    nx, ny = neighbor.position
                    new_air_pollution[nx][ny] += air_per_neighbor
                    new_ground_pollution[nx][ny] += ground_per_neighbor
        
        # Update cells and handle air-to-ground settlement
        for x, row in enumerate(self.grid):
            for y, cell in enumerate(row):
                # Some air pollution settles into the ground
                air_settling = new_air_pollution[x][y] * AIR_TO_GROUND_RATE
                new_air_pollution[x][y] -= air_settling
                new_ground_pollution[x][y] += air_settling
                
                # Update cell values
                cell.air_pollution_level = new_air_pollution[x][y]
                cell.ground_pollution_level = new_ground_pollution[x][y]


    def track_global_statistics(self):
        total_pollution = sum(cell.current_pollution_level for row in self.grid for cell in row)
        total_health = sum(cell.health_level for row in self.grid for cell in row)
        return {
            "total_pollution": total_pollution,
            "average_health": total_health / (len(self.grid) * len(self.grid[0]))
        }
