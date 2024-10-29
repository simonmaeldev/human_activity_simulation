import simpy
import random
from pydantic import Field, field_validator
from typing import Optional, List, Dict, Tuple, ClassVar
from core_types import CoreBaseCell, CoreBaseAgent, Resource, AgentPriority

class Cell(CoreBaseCell):
    env: simpy.Environment
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    air_pollution: float = Field(default=0.0)
    ground_pollution: float = Field(default=0.0)
    agents: List[CoreBaseAgent] = Field(default_factory=list)
    process: Optional[simpy.events.Process] = None
    max_resources: float = Field(default=0.0)
    current_resources: float = Field(default=0.0)
    regeneration_rate: float = Field(default=0.0)

    @field_validator('air_pollution', 'ground_pollution')
    @classmethod
    def validate_pollution(cls, v: float) -> float:
        return max(0.0, v)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.process = self.env.process(self.run())
        
    def add_agent(self, agent: BaseAgent):
        """Add an agent to this cell"""
        self.agents.append(agent)
        
    def remove_agent(self, agent: BaseAgent):
        """Remove an agent from this cell"""
        if agent in self.agents:
            self.agents.remove(agent)

    def regenerate_resources(self) -> None:
        """Base method for resource regeneration. No-op by default."""
        pass

    def run(self):
        while True:
            # Update local pollution levels based on agent impacts
            air_impact = self.calculate_air_pollution_impact()
            ground_impact = self.calculate_ground_pollution_impact()
            
            # Update pollution levels with impacts, ensuring they don't go below 0
            self.air_pollution = max(0.0, self.air_pollution + air_impact)
            self.ground_pollution = max(0.0, self.ground_pollution + ground_impact)

            # Regenerate resources
            self.regenerate_resources()

            yield self.env.timeout(0)  # Allow all agents to request
            
            # Handle resource distribution
            self.distribute_resources()
            
            yield self.env.timeout(1)  # Wait for a week

    def calculate_co2_impact(self) -> float:
        """Calculate total CO2 impact from all agents in the cell"""
        return sum(agent.calculate_co2_impact() for agent in self.agents)
        
    def calculate_air_pollution_impact(self) -> float:
        """Calculate total air pollution impact from all agents in the cell"""
        return sum(agent.calculate_air_pollution_impact() for agent in self.agents)
        
    def calculate_ground_pollution_impact(self) -> float:
        """Calculate total ground pollution impact from all agents in the cell"""
        return sum(agent.calculate_ground_pollution_impact() for agent in self.agents)
        
    
    def get_available_resources(self) -> float:
        """Get amount of resources available for distribution"""
        return self.current_resources
