from typing import Optional
import simpy
from pydantic import BaseModel, Field

class BaseAgent(BaseModel):
    """
    Base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    """
    env: simpy.Environment
    process: Optional[simpy.Process] = None
    health: float = Field(default=1.0, ge=0.0, le=1.0)  # Health level between 0 and 1
    initial_population: int = Field(default=1)  # Initial number of individuals
    population: int = Field(default=None)  # Current number of individuals 

    class Config:
        arbitrary_types_allowed = True
    
    def run(self):
        """Main behavior loop for the agent"""
        while True:
            self.make_decision()
            yield self.env.timeout(1)
    
    def make_decision(self):
        """Make a decision based on current environment state"""
        raise NotImplementedError
        
    def calculate_co2_impact(self) -> float:
        """Calculate how much CO2 this agent produces (positive) or absorbs (negative)"""
        raise NotImplementedError
        
    def calculate_air_pollution_impact(self) -> float:
        """Calculate how much air pollution this agent produces (positive) or removes (negative)"""
        raise NotImplementedError
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate how much ground pollution this agent produces (positive) or removes (negative)"""
        raise NotImplementedError
