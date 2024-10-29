import simpy
import random
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Tuple
from agents.base_agent import BaseAgent, AgentPriority

class Cell(BaseModel):
    env: simpy.Environment
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    air_pollution: float = Field(default=0.0)
    ground_pollution: float = Field(default=0.0)
    agents: List["BaseAgent"] = Field(default_factory=list)
    process: Optional[simpy.events.Process] = None
    resource_requests: Dict[BaseAgent, float] = Field(default_factory=dict)

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
            # Update local pollution levels based on agent impacts
            air_impact = self.calculate_air_pollution_impact()
            ground_impact = self.calculate_ground_pollution_impact()
            
            # Update pollution levels with impacts, ensuring they don't go below 0
            self.air_pollution = max(0.0, self.air_pollution + air_impact)
            self.ground_pollution = max(0.0, self.ground_pollution + ground_impact)
            
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
        
    def add_resource_request(self, agent: BaseAgent, amount: float):
        """Register a resource request from an agent"""
        self.resource_requests[agent] = amount
    
    def distribute_resources(self):
        """Distribute cell resources to requesting agents based on priority"""
        if not self.resource_requests:
            return
            
        requests_by_priority: Dict[AgentPriority, List[Tuple[BaseAgent, float]]] = {}
        for agent, amount in self.resource_requests.items():
            priority = agent.priority
            if priority not in requests_by_priority:
                requests_by_priority[priority] = []
            requests_by_priority[priority].append((agent, amount))
        
        available = self.get_available_resources()
        
        for priority in sorted(requests_by_priority.keys()):
            requests = requests_by_priority[priority]
            if not requests:
                continue
                
            if len(requests) == 1:
                agent, amount = requests[0]
                allocated = min(amount, available)
                agent.pending_resources[self.resource_type] = allocated
                available -= allocated
            else:
                total_requested = sum(amount for _, amount in requests)
                for agent, amount in requests:
                    if available <= 0:
                        break
                    fair_share = (amount / total_requested) * available
                    agent.pending_resources[self.resource_type] = fair_share
                    available -= fair_share
            
            if available <= 0:
                break
        
        self.resource_requests.clear()
    
    def get_available_resources(self) -> float:
        """Get amount of resources available for distribution"""
        raise NotImplementedError
