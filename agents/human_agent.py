import simpy
from pydantic import Field
from .base_agent import BaseAgent

class HumanAgent(BaseAgent):
    """
    Agent representing a human individual in the simulation.
    Makes decisions about resource consumption and movement.
    """
    base_co2_emission: float = Field(default=1.0, description="Base CO2 emission per person")
    base_pollution_emission: float = Field(default=1.0, description="Base pollution emission per person")
    air_pollution_ratio: float = Field(default=0.7, description="70% of pollution goes to air")
    ground_pollution_ratio: float = Field(default=0.3, description="30% of pollution goes to ground")
    
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
        return self.base_co2_emission * self.population
        
    def calculate_air_pollution_impact(self) -> float:
        """Calculate air pollution impact based on population"""
        return self.base_pollution_emission * self.population * self.air_pollution_ratio
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate ground pollution impact based on population"""
        return self.base_pollution_emission * self.population * self.ground_pollution_ratio
