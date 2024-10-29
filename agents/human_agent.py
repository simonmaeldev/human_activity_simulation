import simpy
from pydantic import Field
from .base_agent import BaseAgent

class HumanAgent(BaseAgent):
    """
    Agent representing a human individual in the simulation.
    Makes decisions about resource consumption and movement.
    """
    # Base emission rates per individual
    BASE_CO2_EMISSION = 1.0  # Base CO2 emission per person
    BASE_POLLUTION_EMISSION = 1.0  # Base pollution emission per person
    AIR_POLLUTION_RATIO = 0.7  # 70% of pollution goes to air
    GROUND_POLLUTION_RATIO = 0.3  # 30% of pollution goes to ground
    def run(self):
        while True:
            self.make_decision()
            yield self.env.timeout(1)  # Wait one time step
            
    def make_decision(self):
        """
        Make decisions about:
        - Resource consumption
        - Movement between cells
        - Interaction with environment
        """
        # TODO: Implement decision-making logic
        pass
        
    def calculate_co2_impact(self) -> float:
        """Calculate CO2 emissions based on population"""
        return self.BASE_CO2_EMISSION * self.population
        
    def calculate_air_pollution_impact(self) -> float:
        """Calculate air pollution impact based on population"""
        return self.BASE_POLLUTION_EMISSION * self.population * self.AIR_POLLUTION_RATIO
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate ground pollution impact based on population"""
        return self.BASE_POLLUTION_EMISSION * self.population * self.GROUND_POLLUTION_RATIO
