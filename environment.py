import simpy
import random
from typing import List, Tuple, Optional, Dict
from cell import Cell, CellType
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
        self.resource_manager = ResourceManager(config)
        self.pollution_manager = PollutionManager(config)
        self.data_collector = DataCollector()
        self.csv_exporter = CSVExporter()

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
        # Update lake networks and balance water
        self.resource_manager.water_system.update_lake_networks(self.grid)
        self.resource_manager.water_system.balance_water_levels()
        
        # Handle pollution spread
        self.pollution_manager.spread_pollution(self.grid)
        self.resource_manager.water_system.spread_water_pollution()
        
        # Regenerate resources
        for row in self.grid:
            for cell in row:
                self.resource_manager.regenerate_resources(cell)
        
        # Collect data
        self.data_collector.collect_global_metrics(self)
        for row in self.grid:
            for cell in row:
                self.data_collector.collect_cell_data(cell)
                for population in cell.populations:
                    self.data_collector.collect_population_metrics(population, cell)


    def export_simulation_data(self) -> Dict[str, str]:
        """Export all collected data to CSV files"""
        return self.csv_exporter.export_all(self.data_collector)
