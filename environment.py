import simpy
import random
import logging
from typing import List, Tuple, Optional, Dict
from cell import Cell, CellType, CityCell, ForestCell, LakeCell, LandCell
from config_model import ConfigModel
from population_processes import PopulationManager
from resource_manager import ResourceManager
from pollution_manager import PollutionManager
from data_collection.data_collector import DataCollector
from data_collection.csv_exporter import CSVExporter
from population import Population, PopulationType
from constants import MAX_HUMAN_DENSITY, MAX_TREE_DENSITY

class Environment:
    def __init__(self, config: ConfigModel):
        self.config = config  # Store config first so it's available for _initialize_grid
        self.env = simpy.Environment()
        self.grid = self._initialize_grid(config.grid_size)
        self.population_manager = PopulationManager(self.env, config)
        self.resource_manager = ResourceManager(config, self.grid)
        self.pollution_manager = PollutionManager(config)
        self.data_collector = DataCollector()
        self.csv_exporter = CSVExporter(config.simulation_dir if hasattr(config, 'simulation_dir') else None)

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
        
        grid = []
        for x in range(grid_size[0]):
            row = []
            for y in range(grid_size[1]):
                # Use numpy's random number generator for better statistical properties
                cell_type = random.choice(list(CellType))
                cell = cell_types[cell_type](position=(x, y))
                
                # Initialize populations based on cell type
                if cell_type == CellType.CITY:
                    # Humans in cities (20-50% of max density)
                    human_size = int(MAX_HUMAN_DENSITY * random.uniform(0.2, 0.5))
                    cell.populations.append(Population(
                        type=PopulationType.HUMANS,
                        size=human_size,
                        health_level=100.0,
                        resource_consumption_rate=1.0,
                        pollution_generation_rate=0.5
                    ))
                
                elif cell_type == CellType.FOREST:
                    # Trees in forests (70-100% of max density)
                    tree_size = int(MAX_TREE_DENSITY * random.uniform(0.7, 1.0))
                    cell.populations.append(Population(
                        type=PopulationType.TREES,
                        size=tree_size,
                        health_level=100.0,
                        resource_consumption_rate=0.1,
                        pollution_generation_rate=0.0
                    ))
                
                elif cell_type == CellType.LAKE:
                    # Fish in lakes (70-100% capacity)
                    fish_size = int(1000 * random.uniform(0.7, 1.0))  # Using 1000 as base capacity
                    cell.populations.append(Population(
                        type=PopulationType.FISH,
                        size=fish_size,
                        health_level=100.0,
                        resource_consumption_rate=0.3,
                        pollution_generation_rate=0.0
                    ))
                
                elif cell_type == CellType.LAND:
                    # Wildlife on land (70-100% capacity)
                    wildlife_size = int(500 * random.uniform(0.7, 1.0))  # Using 500 as base capacity
                    cell.populations.append(Population(
                        type=PopulationType.WILDLIFE,
                        size=wildlife_size,
                        health_level=100.0,
                        resource_consumption_rate=0.5,
                        pollution_generation_rate=0.1
                    ))
                
                row.append(cell)
            grid.append(row)
        
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

    def update_populations(self):
        """
        Update all population activities:
        - Daily cycles (work, resource consumption)
        - Growth and decline
        - Health updates
        """
        self.population_manager.update_populations(self.grid)
        
    def process_agent_decisions(self):
        """
        Process all agent decisions:
        - Resource gathering locations
        - Cell conversion decisions
        - Movement choices
        """
        for cell in [cell for row in self.grid for cell in row]:
            for population, agent in self.population_manager.agents.items():
                if population in cell.populations:
                    decisions = agent.make_decisions()
                    if decisions:
                        logging.info(f"Agent decisions for {population.type} in {cell.position}: {decisions}")
                        
    def update_environmental_processes(self):
        """
        Update environmental processes:
        - Pollution spread through air
        - Water flow and pollution in water systems
        - Resource transfer between cells
        """
        # Handle pollution spread
        self.pollution_manager.spread_pollution(self.grid)
        
        # Update water systems (now only in resource_manager)
        self.resource_manager.water_system.update_lake_networks(self.grid)
        self.resource_manager.water_system.balance_water_levels(self.grid)
        self.resource_manager.water_system.spread_water_pollution(self.grid)
        
    def regenerate_resources(self):
        """
        Handle resource regeneration:
        - Natural resource regeneration
        - Resource quality updates
        """
        for row in self.grid:
            for cell in row:
                self.resource_manager.regenerate_resources(cell)
                
    def collect_daily_data(self):
        """Collect all simulation data for the current day"""
        current_step = self.env.now
        self.data_collector.collect_global_metrics(self)
        for row in self.grid:
            for cell in row:
                self.data_collector.collect_cell_data(cell, current_step)
                for population in cell.populations:
                    self.data_collector.collect_population_metrics(population, cell, current_step)


    def export_simulation_data(self) -> Dict[str, str]:
        """Export all collected data to CSV files"""
        return self.csv_exporter.export_all(self.data_collector, self.config)
