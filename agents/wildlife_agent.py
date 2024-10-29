import simpy
from pydantic import Field
from .base_agent import BaseAgent
from cells.cell import Cell
from cells.lake import Lake
from cells.forest import Forest

class WildlifeAgent(BaseAgent):
    """
    Agent representing wildlife in the simulation.
    Makes decisions about movement, feeding and reproduction.
    Basic behaviors:
    - Moves between cells searching for food
    - Reproduces when conditions are favorable
    - Health affected by environmental conditions
    """
        
    def calculate_co2_impact(self) -> float:
        """Wildlife has neutral CO2 impact in this model"""
        return 0.0
        
    def calculate_air_pollution_impact(self) -> float:
        """Wildlife has neutral air pollution impact in this model"""
        return 0.0
        
    def calculate_ground_pollution_impact(self) -> float:
        """Wildlife has neutral ground pollution impact in this model"""
        return 0.0
        
    def has_required_resources(self, cell: Cell) -> bool:
        """Wildlife looks for water or natural habitats with low pollution"""
        return (isinstance(cell, (Lake, Forest)) and 
                cell.ground_pollution < 0.5 and
                cell.current_resources > 0)
