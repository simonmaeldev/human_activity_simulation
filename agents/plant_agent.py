import simpy
from pydantic import Field
from .base_agent import BaseAgent

class PlantAgent(BaseAgent):
    base_co2_absorption: float = Field(default=-0.5, description="Base CO2 absorption per plant (negative means absorption)")
    base_ground_cleanup: float = Field(default=-0.3, description="Base ground pollution removal rate (negative means removal)")
    """
    Agent representing a plant in the simulation.
    Makes decisions about growth, reproduction and resource usage.
    Basic behaviors:
    - Grows based on available sunlight and nutrients
    - Absorbs CO2 during photosynthesis
    - Can spread seeds to nearby cells
    """
        
    def calculate_co2_impact(self) -> float:
        """Calculate CO2 absorption based on population and health"""
        return self.base_co2_absorption * self.population * self.health
        
    def calculate_air_pollution_impact(self) -> float:
        """Plants don't affect air pollution directly"""
        return 0.0
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate ground pollution removal based on population and health"""
        return self.base_ground_cleanup * self.population * self.health
