from typing import Dict, List, Tuple, Optional
import simpy
from pydantic import Field
from core_types import CoreBaseAgent, Resource, AgentPriority
from cells.cell import Cell
from resource_manager import ResourceManager
from utils.cell_search import CellSearchManager

class BaseAgent(CoreBaseAgent):
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
    position: Tuple[int, int] = Field(...)
    search_range: int = Field(default=3)
    cell_search_manager: CellSearchManager = Field(...)
    resource_manager: "ResourceManager" = Field(...)

    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self.process = self.env.process(self.run())
    
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
        """Request resources via ResourceManager based on planned action"""
        if action['type'] == 'consume':
            target = action['target']  # Cell or Agent
            amount = action['amount']
            self.resource_manager.request_resources(self, target, amount)
    
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
        
    def has_required_resources(self, cell: 'Cell') -> bool:
        """
        Check if a cell has the resources this agent needs.
        Must be implemented by derived classes.
        """
        raise NotImplementedError("Agents must implement has_required_resources")

    def find_resource_cells(self) -> List[Tuple['Cell', float]]:
        """Find cells with available resources within range"""
        return self.cell_search_manager.get_valid_cells(
            self.position,
            self.search_range,
            self.has_required_resources
        )
