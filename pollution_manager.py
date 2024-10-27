from typing import List, Tuple
from cell import Cell, CellType
from config_model import ConfigModel
from constants import (
    AIR_SPREAD_RATE, GROUND_SPREAD_RATE,
    AIR_TO_GROUND_RATE
)

class PollutionManager:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.global_co2_level = config.initial_co2_level
        self.spread_rates = config.pollution_spread_rates

    def add_co2(self, amount: float):
        """Add CO2 from human activity"""
        self.global_co2_level += amount

    def reduce_co2(self, amount: float):
        """Reduce CO2 from tree absorption"""
        self.global_co2_level = max(0, self.global_co2_level - amount)

    def spread_pollution(self, grid: List[List[Cell]]):
        """Handle all pollution spread mechanics"""
        new_air = [[0.0 for _ in row] for row in grid]
        new_ground = [[0.0 for _ in row] for row in grid]
        
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                neighbors = self._get_valid_neighbors(grid, i, j)
                
                # Air pollution spread
                air_out = cell.air_pollution_level * AIR_SPREAD_RATE
                air_per_neighbor = air_out / (len(neighbors) or 1)
                new_air[i][j] = cell.air_pollution_level - air_out
                
                # Ground pollution spread
                ground_out = cell.ground_pollution_level * GROUND_SPREAD_RATE
                ground_per_neighbor = ground_out / (len(neighbors) or 1)
                new_ground[i][j] = cell.ground_pollution_level - ground_out
                
                # Distribute to neighbors
                for ni, nj in neighbors:
                    new_air[ni][nj] += air_per_neighbor
                    new_ground[ni][nj] += ground_per_neighbor
        
        # Update cells with new values and handle settling
        self._update_pollution_levels(grid, new_air, new_ground)

    def _get_valid_neighbors(self, grid: List[List[Cell]], i: int, j: int) -> List[Tuple[int, int]]:
        """Get valid neighboring cell coordinates"""
        neighbors = []
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < len(grid) and 0 <= nj < len(grid[0]):
                neighbors.append((ni, nj))
        return neighbors

    def _update_pollution_levels(self, grid: List[List[Cell]], new_air: List[List[float]], 
                               new_ground: List[List[float]]):
        """Update pollution levels and handle air-to-ground settling"""
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                # Air pollution settling into ground
                settling = new_air[i][j] * AIR_TO_GROUND_RATE
                new_air[i][j] -= settling
                new_ground[i][j] += settling
                
                # Apply natural decay based on cell type and health
                base_decay = self.config.base_pollution_decay_rate
                
                # Cell type specific decay rates
                type_multiplier = {
                    CellType.FOREST: 2.0,  # Forests clean pollution fastest
                    CellType.LAKE: 1.5,    # Lakes help clean pollution
                    CellType.LAND: 1.2,    # Natural land has some cleaning effect
                    CellType.CITY: 0.8     # Cities are less effective at cleaning
                }.get(cell.cell_type, 1.0)
                
                # Health impact on decay (healthier ecosystems clean better)
                health_multiplier = 0.5 + (cell.health_level / 200)  # 0.5 to 1.0
                
                # Calculate final decay rate
                decay_rate = base_decay * type_multiplier * health_multiplier
                
                # Apply decay with diminishing returns for high pollution
                pollution_factor = 1.0 / (1.0 + max(new_air[i][j], new_ground[i][j]) / 100)
                effective_decay = decay_rate * pollution_factor
                
                new_air[i][j] *= (1 - effective_decay)
                new_ground[i][j] *= (1 - effective_decay)
                
                # Update cell values
                cell.air_pollution_level = new_air[i][j]
                cell.ground_pollution_level = new_ground[i][j]

    def get_current_co2(self) -> float:
        """Get current global CO2 level"""
        return self.global_co2_level
