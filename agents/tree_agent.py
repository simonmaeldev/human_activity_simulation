import simpy
from pydantic import Field
from .base_agent import BaseAgent

class TreeAgent(BaseAgent):
    """
    Agent representing a tree in the simulation.
    Makes decisions about growth and resource usage.
    """
    height: float = Field(default=1)  # Starting height in meters
    base_co2_absorption: float = Field(default=-2.0, description="Base CO2 absorption per tree (negative means absorption)")
    
    def run(self):
        while True:
            self.make_decision()
            yield self.env.timeout(1)  # Wait one time step
            
    def make_decision(self):
        """
        Make decisions about:
        - Growth rate
        - Resource absorption
        - CO2 absorption
        """
        # TODO: Implement decision-making logic
        pass

    def calculate_co2_impact(self) -> float:
        """Calculate CO2 absorption based on population and health"""
        return self.base_co2_absorption * self.population * self.health
        
    def calculate_air_pollution_impact(self) -> float:
        """Trees don't affect air pollution directly"""
        return 0.0
        
    def calculate_ground_pollution_impact(self) -> float:
        """Trees don't affect ground pollution directly"""
        return 0.0
