from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
from cell import Cell, CellType
from population import PopulationType

class DataCollector:
    """
    Collects and manages simulation data for analysis and export.
    Tracks global metrics, cell-specific data, population metrics,
    resource levels, and pollution levels.
    """
    def __init__(self):
        self.global_metrics: List[Dict[str, Any]] = []
        self.cell_data: Dict[CellType, List[Dict[str, Any]]] = {
            cell_type: [] for cell_type in CellType
        }
        self.population_metrics: Dict[PopulationType, List[Dict[str, Any]]] = {
            pop_type: [] for pop_type in PopulationType
        }

    def collect_global_metrics(self, environment) -> None:
        """Collect global simulation metrics"""
        timestamp = datetime.now()
        total_population = sum(
            pop.size for row in environment.grid 
            for cell in row 
            for pop in cell.populations
        )
        metrics = {
            'step': environment.env.now,
            'co2_level': environment.pollution_manager.get_current_co2(),
            'total_population': total_population,
            'average_pollution': sum(
                cell.current_pollution_level 
                for row in environment.grid 
                for cell in row
            ) / (len(environment.grid) * len(environment.grid[0])),
            'average_health': sum(
                cell.health_level 
                for row in environment.grid 
                for cell in row
            ) / (len(environment.grid) * len(environment.grid[0]))
        }
        self.global_metrics.append(metrics)

    def collect_cell_data(self, cell: Cell, step: int) -> None:
        """Collect data for a specific cell"""
        data = {
            'step': step,
            'position': cell.position,
            'health_level': cell.health_level,
            'resource_level': cell.resource_level,
            'air_pollution': cell.air_pollution_level,
            'ground_pollution': cell.ground_pollution_level
        }
        self.cell_data[cell.cell_type].append(data)

    def collect_population_metrics(self, population, cell: Cell, step: int) -> None:
        """Collect metrics for a specific population"""
        metrics = {
            'step': step,
            'cell_position': cell.position,
            'cell_type': cell.cell_type.value,
            'population_size': population.size,
            'health_level': population.health_level,
            'resource_consumption': population.resource_consumption_rate,
            'pollution_generation': population.pollution_generation_rate
        }
        self.population_metrics[population.type].append(metrics)

    def get_global_metrics_df(self) -> pd.DataFrame:
        """Convert global metrics to DataFrame"""
        return pd.DataFrame(self.global_metrics)

    def get_cell_data_df(self, cell_type: CellType) -> pd.DataFrame:
        """Convert cell data to DataFrame for specific cell type"""
        return pd.DataFrame(self.cell_data[cell_type])

    def get_population_metrics_df(self, pop_type: PopulationType) -> pd.DataFrame:
        """Convert population metrics to DataFrame for specific population type"""
        return pd.DataFrame(self.population_metrics[pop_type])
