import simpy
import random
from typing import List, Tuple, Optional, Dict
from cell import Cell, CellType, CityCell, ForestCell, LakeCell, LandCell
from config_model import ConfigModel
from population_processes import PopulationManager
from resource_manager import ResourceManager
from pollution_manager import PollutionManager
from data_collection.data_collector import DataCollector
from data_collection.csv_exporter import CSVExporter

class Environment:
    def __init__(self, config: ConfigModel):
        self.env = simpy.Environment()
        self.grid = self._initialize_grid(config.grid_size)
        self.config = config
        self.population_manager = PopulationManager(self.env, config)
        self.resource_manager = ResourceManager(config, self.grid)
        self.pollution_manager = PollutionManager(config)
        self.data_collector = DataCollector()
        self.csv_exporter = CSVExporter()

    def _initialize_grid(self, grid_size: Tuple[int, int]) -> List[List[Cell]]:
        # Use config's random seed if provided
        if hasattr(self.config, 'random_seed') and self.config.random_seed is not None:
            random.seed(self.config.random_seed)
            
        cell_types = {
            CellType.CITY: CityCell,
            CellType.FOREST: ForestCell,
            CellType.LAKE: LakeCell,
            CellType.LAND: LandCell
        }
        
        grid = [[
            cell_types[random.choice(list(CellType))](position=(x, y))
            for y in range(grid_size[1])
        ] for x in range(grid_size[0])]
        
        # Reset random state if seed was used
        if hasattr(self.config, 'random_seed') and self.config.random_seed is not None:
            random.seed()
            
        return grid

    def get_neighbors(self, x: int, y: int) -> List[Cell]:
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]):
                neighbors.append(self.grid[nx][ny])
        return neighbors

    def update_environment(self):
        """Update environment state for one time step"""
        # Update lake networks and balance water
        self.resource_manager.water_system.update_lake_networks(self.grid)
        self.resource_manager.water_system.balance_water_levels(self.grid)
        
        # Handle pollution spread
        self.pollution_manager.spread_pollution(self.grid)
        self.resource_manager.water_system.spread_water_pollution(self.grid)
        
        # Regenerate resources
        for row in self.grid:
            for cell in row:
                self.resource_manager.regenerate_resources(cell)
        
        # Collect data
        current_step = self.env.now
        self.data_collector.collect_global_metrics(self)
        for row in self.grid:
            for cell in row:
                self.data_collector.collect_cell_data(cell, current_step)
                for population in cell.populations:
                    self.data_collector.collect_population_metrics(population, cell, current_step)


    def export_simulation_data(self) -> Dict[str, str]:
        """Export all collected data to CSV files"""
        return self.csv_exporter.export_all(self.data_collector)
