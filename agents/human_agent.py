import simpy
from pydantic import Field
from .base_agent import BaseAgent

from cells.cell import Cell

class HumanAgent(BaseAgent):
    """
    Agent representing a human individual in the simulation.
    Makes decisions about resource consumption and movement.
    """
    base_co2_emission: float = Field(default=1.0, description="Base CO2 emission per person")
    base_pollution_emission: float = Field(default=1.0, description="Base pollution emission per person")
    air_pollution_ratio: float = Field(default=0.7, description="70% of pollution goes to air")
    ground_pollution_ratio: float = Field(default=0.3, description="30% of pollution goes to ground")
        
    def calculate_co2_impact(self) -> float:
        """Calculate CO2 emissions based on population"""
        return self.base_co2_emission * self.population
        
    def calculate_air_pollution_impact(self) -> float:
        """Calculate air pollution impact based on population"""
        return self.base_pollution_emission * self.population * self.air_pollution_ratio
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate ground pollution impact based on population"""
        return self.base_pollution_emission * self.population * self.ground_pollution_ratio
        
    def has_required_resources(self, cell: "Cell") -> bool:
        """Humans look for water in lakes or food in forests"""
        from cells.lake import Lake
        from cells.forest import Forest
        return (isinstance(cell, (Lake, Forest)) and 
                cell.current_resources > 0)
