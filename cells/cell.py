import simpy
import random
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from agents.base_agent import BaseAgent

class Cell(BaseModel):
    env: simpy.Environment
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    air_pollution: float = Field(default=0.0)
    ground_pollution: float = Field(default=0.0)
    agents: List["BaseAgent"] = Field(default_factory=list)
    process: Optional[simpy.events.Process] = None

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

    def run(self):
        while True:
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
