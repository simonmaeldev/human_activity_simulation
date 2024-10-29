import simpy
from pydantic import Field
from .base_agent import BaseAgent

class PlantAgent(BaseAgent):
    # Base rates for environmental impact
    BASE_CO2_ABSORPTION = -0.5  # Base CO2 absorption per plant (negative means absorption)
    BASE_GROUND_CLEANUP = -0.3  # Base ground pollution removal rate (negative means removal)
    """
    Agent representing a plant in the simulation.
    Makes decisions about growth, reproduction and resource usage.
    Basic behaviors:
    - Grows based on available sunlight and nutrients
    - Absorbs CO2 during photosynthesis
    - Can spread seeds to nearby cells
    """
    
    def run(self):
        while True:
            self.make_decision()
            yield self.env.timeout(1)  # Wait one time step
            
    def make_decision(self):
        """
        Make decisions about:
        - Growth rate based on environmental conditions
        - CO2 absorption through photosynthesis
        - Seed dispersal when mature
        """
        # TODO: Implement decision-making logic
        pass
        
    def calculate_co2_impact(self) -> float:
        """Calculate CO2 absorption based on population and health"""
        return self.BASE_CO2_ABSORPTION * self.population * self.health
        
    def calculate_air_pollution_impact(self) -> float:
        """Plants don't affect air pollution directly"""
        return 0.0
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate ground pollution removal based on population and health"""
        return self.BASE_GROUND_CLEANUP * self.population * self.health
