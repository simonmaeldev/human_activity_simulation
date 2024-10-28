import simpy
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import os

from environment import Environment
from config_model import ConfigModel
from resource_manager import ResourceManager
from pollution_manager import PollutionManager
from water_system import WaterSystem
from population_processes import PopulationManager
from data_collection.data_collector import DataCollector

class SimulationController:
    """
    Main controller for the environmental simulation.
    Manages the simulation lifecycle, configuration, and data collection.
    """
    def __init__(self, config:ConfigModel):
        """
        Initialize simulation controller with configuration.
        
        Args:
            config: Configuration parameters for the simulation
        """
        config.simulation_dir = f"simulation_data/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = config
        self.environment = Environment(config)
        self.data_collector = DataCollector()
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None

        # Create timestamped directories
        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        self.log_dir = f"logs/{timestamp}"
        self.simulation_dir = f"simulation_data/{timestamp}"
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.simulation_dir).mkdir(parents=True, exist_ok=True)
        
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging for the simulation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, 'simulation.log')),
                logging.StreamHandler()
            ]
        )

    async def run(self) -> Dict[str, Any]:
        """
        Run the simulation for specified duration.
        
        The simulation follows this order each day:
        1. Population activities (consumption, movement, growth)
        2. Agent decisions (resource gathering, cell conversion)
        3. Environmental processes (pollution spread, water flow)
        4. Resource regeneration
        5. Data collection
        
        Args:
            duration: Number of simulation days to run
            
        Returns:
            Dict containing simulation results and statistics
        """
        duration = self.config.duration
        logging.info(f"Starting simulation for {duration} days")

        try:
            # Run the simulation
            self.environment.env.run(until=duration)

            # Export final data
            export_results = self.environment.export_simulation_data()
            
            self.end_time = datetime.now()
            duration_seconds = (self.end_time - self.start_time).total_seconds()
            
            logging.info(f"Simulation completed in {duration_seconds:.2f} seconds")
            
            # Return simulation results
            return {
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_seconds': duration_seconds,
                'export_results': export_results
            }

        except Exception as e:
            logging.error(f"Simulation failed: {str(e)}")
            raise
