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
    def __init__(self, config: ConfigModel):
        """
        Initialize simulation controller with configuration.
        
        Args:
            config: Configuration parameters for the simulation
        """
        # Set simulation directory in config
        config.simulation_dir = f"simulation_data/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = config
        
        # Initialize environment first to get access to grid and env
        self.environment = Environment(config)
        self.env = self.environment.env
        self.grid = self.environment.grid
        
        # Initialize managers
        self.resource_manager = ResourceManager(config, self.grid)
        self.pollution_manager = PollutionManager(config)
        self.water_system = WaterSystem()
        
        # Connect resource manager to config for other components to access
        self.config.resource_manager = self.resource_manager
        
        # Initialize population manager last so it has access to other systems
        self.population_manager = PopulationManager(self.env, config)
        
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

    def initialize_simulation(self) -> None:
        """
        Set up initial simulation state.
        Initializes simulation components.
        """
        logging.info("Initializing simulation...")

    def run(self, duration: int) -> Dict[str, Any]:
        """
        Run the simulation for specified duration.
        
        Args:
            duration: Number of simulation days to run
            
        Returns:
            Dict containing simulation results and statistics
        """
        self.initialize_simulation()
        logging.info(f"Starting simulation for {duration} days")

        try:
            # Run for specified duration
            for day in range(duration):
                # Update environment state
                self.environment.update_environment()
                
                # Process SimPy events for one day
                self.environment.env.run(until=day + 1)
                
                # Log progress every week
                if day % 7 == 0:
                    logging.info(f"Simulation progress: Day {day}/{duration}")

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

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current simulation statistics.
        
        Returns:
            Dict containing current simulation metrics
        """
        if not self.environment:
            return {}

        return {
            'current_time': self.environment.env.now,
            'global_co2': self.environment.pollution_manager.get_current_co2(),
            'total_population': sum(
                pop.size
                for row in self.environment.grid
                for cell in row
                for pop in cell.populations
            )
        }
