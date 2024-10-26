import simpy
import random
from typing import List, Tuple
from cell import Cell, CellType
from config_model import ConfigModel

class Environment:
    def __init__(self, config: ConfigModel):
        self.env = simpy.Environment()
        self.grid = self._initialize_grid(config.grid_size)
        self.global_co2_level = config.initial_co2_level
        self.config = config

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
        for row in self.grid:
            for cell in row:
                neighbors = self.get_neighbors(*cell.position)
                for neighbor in neighbors:
                    spread_rate = self.config.pollution_spread_rates[cell.cell_type.value]
                    neighbor.current_pollution_level += cell.current_pollution_level * spread_rate

    def manage_cell_type_conversions(self):
        for row in self.grid:
            for cell in row:
                if cell.cell_type == CellType.FOREST and cell.current_pollution_level > self.config.cell_conversion_thresholds["forest_to_land"]:
                    cell.cell_type = CellType.LAND
                elif cell.cell_type == CellType.LAND and cell.health_level > self.config.cell_conversion_thresholds["land_to_city"]:
                    cell.cell_type = CellType.CITY

    def track_global_statistics(self):
        total_pollution = sum(cell.current_pollution_level for row in self.grid for cell in row)
        total_health = sum(cell.health_level for row in self.grid for cell in row)
        return {
            "total_pollution": total_pollution,
            "average_health": total_health / (len(self.grid) * len(self.grid[0]))
        }
