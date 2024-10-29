from typing import Dict, List, Tuple, Optional
import simpy
from pydantic import BaseModel, Field
from enum import IntEnum

class AgentPriority(IntEnum):
    HIGHEST = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    LOWEST = 5

class BaseAgent(BaseModel):
    """
    Base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    """
    env: simpy.Environment
    process: Optional[simpy.Process] = None
    health: float = Field(default=1.0, ge=0.0, le=1.0)  # Health level between 0 and 1
    population: int = Field(default=1)  # Current number of individuals
    priority: AgentPriority = Field(default=AgentPriority.MEDIUM)
    pending_resources: List["Resource"] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
    
    def run(self):
        """Main behavior loop for the agent"""
        while True:
            # Phase 1: All agents request resources
            self.pending_resources.clear()
            action = self.plan_action()
            self.request_resources(action)
            yield self.env.timeout(0)  # Allow all agents to request
            
            # Phase 2: Resource owners distribute resources
            self.distribute_resources()
            yield self.env.timeout(0)  # Allow all distribution to complete
            
            # Phase 3: Consume allocated resources and update state
            self.execute_action(action)
            yield self.env.timeout(1)  # Wait for next day

    def plan_action(self) -> dict:
        """Plan what resources to consume and from where."""
        raise NotImplementedError
    
    def request_resources(self, action: dict):
        """Request resources from cells/agents based on planned action"""
        if action['type'] == 'consume':
            target = action['target']  # Cell or Agent
            amount = action['amount']
            target.add_resource_request(self, amount)
    
    def distribute_resources(self):
        """Distribute resources to requesting agents based on priority"""
        if not hasattr(self, 'resource_requests'):
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
                    quality=self.health,
                    source=self
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
                        quality=self.health,
                        source=self
                    )
                    agent.pending_resources.append(resource)
                    available -= fair_share
            
            if available <= 0:
                break
        
        self.resource_requests.clear()
    
    def execute_action(self, action: dict):
        """Execute the planned action using allocated resources"""
        raise NotImplementedError
    
    def get_available_resources(self) -> float:
        """Get amount of resources available for distribution"""
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
