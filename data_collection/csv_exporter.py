from typing import Dict, Optional
import os
import json
from datetime import datetime
import pandas as pd
from cell import CellType
from population import PopulationType
from .data_collector import DataCollector

class CSVExporter:
    """
    Handles exporting collected simulation data to CSV files.
    Creates separate files for each cell type, global metrics,
    and population statistics.
    """
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir
        self._ensure_output_dir()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_filename(self, prefix: str) -> str:
        """Generate filename"""
        return os.path.join(
            self.output_dir,
            f"{prefix}.csv"
        )

    def export_global_metrics(self, data_collector: DataCollector) -> str:
        """Export global metrics to CSV"""
        filename = self._get_filename("global_metrics")
        df = data_collector.get_global_metrics_df()
        df.to_csv(filename, index=False)
        return filename

    def export_cell_data(self, data_collector: DataCollector) -> Dict[CellType, str]:
        """Export cell-specific data to separate CSVs by cell type"""
        filenames = {}
        for cell_type in CellType:
            filename = self._get_filename(f"cell_data_{cell_type.value}")
            df = data_collector.get_cell_data_df(cell_type)
            df.to_csv(filename, index=False)
            filenames[cell_type] = filename
        return filenames

    def export_population_metrics(self, data_collector: DataCollector) -> Dict[PopulationType, str]:
        """Export population metrics to separate CSVs by population type"""
        filenames = {}
        for pop_type in PopulationType:
            filename = self._get_filename(f"population_{pop_type.value}")
            df = data_collector.get_population_metrics_df(pop_type)
            df.to_csv(filename, index=False)
            filenames[pop_type] = filename
        return filenames

    def export_config(self, config) -> str:
        """Export configuration to JSON file"""
        filename = self._get_filename("config")
        filename = filename.replace('.csv', '.json')
        with open(filename, 'w') as f:
            json.dump(config.dict(), f, indent=4)
        return filename

    def export_all(self, data_collector: DataCollector, config) -> Dict[str, str]:
        """Export all collected data to CSV files and configuration"""
        results = {
            'global_metrics': self.export_global_metrics(data_collector),
            'cell_data': self.export_cell_data(data_collector),
            'population_metrics': self.export_population_metrics(data_collector),
            'config': self.export_config(config)
        }
        return results
