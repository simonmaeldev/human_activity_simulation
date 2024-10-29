import simpy
import random
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Tuple, ClassVar, TYPE_CHECKING
from agents.enums import AgentPriority
from consumableResource import Resource

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

class Cell(BaseModel):
    env: simpy.Environment
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    air_pollution: float = Field(default=0.0)
    ground_pollution: float = Field(default=0.0)
    agents: List["BaseAgent"] = Field(default_factory=list)
    process: Optional[simpy.events.Process] = None
    resource_requests: Dict[BaseAgent, float] = Field(default_factory=dict)
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
                # Single agent at this priority - give what's available
                agent, amount = requests[0]
                allocated = min(amount, available)
                resource = Resource(
                    name=self.resource_type,
                    quantity=allocated,
                    # For cells, quality is inverse of ground pollution
                    quality=max(0.0, 1.0 - self.ground_pollution)
                )
                agent.pending_resources.append(resource)
                available -= allocated
            else:
                # Multiple agents at same priority - split equally
                total_requested = sum(amount for _, amount in requests)
                for agent, amount in requests:
                    if available <= 0:
                        break
                    fair_share = (amount / total_requested) * available
                    resource = Resource(
                        name=self.resource_type,
                        quantity=fair_share,
                        # For cells, quality is inverse of ground pollution
                        quality=max(0.0, 1.0 - self.ground_pollution),
                    )
                    agent.pending_resources.append(resource)
                    available -= fair_share
            
            if available <= 0:
                break
        
        self.resource_requests.clear()
    
    def get_available_resources(self) -> float:
        """Get amount of resources available for distribution"""
        return self.current_resources
