from config_model import ConfigModel
from simulation_controller import SimulationController
import logging
import traceback

def main():
    # Create simulation configuration with fixed seed for reproducibility
    config = ConfigModel(grid_size=(10,10), random_seed=42)
    
    # Initialize simulation controller
    controller = SimulationController(config)
    
    try:
        # Run simulation for 365 days
        results = controller.run(duration=100)
        
        # Print summary statistics
        logging.info("Simulation Results:")
        logging.info(f"Start time: {results['start_time']}")
        logging.info(f"End time: {results['end_time']}")
        logging.info(f"Duration: {results['duration_seconds']:.2f} seconds")
        logging.info(f"Export files: {results['export_results']}")
        
    except Exception as e:
        logging.error(f"Simulation failed: {str(e)}")
        logging.error(f"Traceback:\n{traceback.format_exc()}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
