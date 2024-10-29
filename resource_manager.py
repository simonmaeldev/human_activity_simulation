"""
Central manager for all resource-related operations in the simulation.

Design Pattern: Manager Pattern (a form of Mediator)
Benefits:
- Decouples resource distribution logic from cells and agents
- Provides a single source of truth for resource operations
- Makes the system easier to modify and extend
- Simplifies testing by centralizing complex logic
- Enables global resource policies and constraints
"""

from typing import Dict, List, Tuple, Optional
from core_types import CoreBaseAgent, CoreBaseCell, Resource, AgentPriority
import simpy

class ResourceManager:
    """
    Manages all resource distribution in the simulation.
    Acts as a mediator between agents and cells for resource requests.
    """
    
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.pending_requests: Dict[CoreBaseCell, Dict[CoreBaseAgent, float]] = {}
        
    def request_resources(self, agent: CoreBaseAgent, cell: CoreBaseCell, amount: float) -> None:
        """
        Register a resource request from an agent to a cell.
        
        Args:
            agent: The requesting agent
            cell: The target cell containing resources
            amount: Amount of resources requested
        """
        if cell not in self.pending_requests:
            self.pending_requests[cell] = {}
        self.pending_requests[cell][agent] = amount

    def distribute_resources(self) -> None:
        """
        Process all pending resource requests and distribute resources.
        Takes into account agent priorities and available resources.
        """
        for cell, requests in self.pending_requests.items():
            # Group requests by priority
            requests_by_priority: Dict[AgentPriority, List[Tuple[CoreBaseAgent, float]]] = {}
            for agent, amount in requests.items():
                priority = agent.priority
                if priority not in requests_by_priority:
                    requests_by_priority[priority] = []
                requests_by_priority[priority].append((agent, amount))
            
            # Distribute resources starting with highest priority
            available = cell.current_resources
            for priority in sorted(requests_by_priority.keys()):
                priority_requests = requests_by_priority[priority]
                
                if len(priority_requests) == 1:
                    # Single agent at this priority - give what's available
                    agent, amount = priority_requests[0]
                    allocated = min(amount, available)
                    self._allocate_resource(cell, agent, allocated)
                    available -= allocated
                else:
                    # Multiple agents at same priority - split equally
                    total_requested = sum(amount for _, amount in priority_requests)
                    for agent, amount in priority_requests:
                        if available <= 0:
                            break
                        fair_share = (amount / total_requested) * available
                        self._allocate_resource(cell, agent, fair_share)
                        available -= fair_share
                
                if available <= 0:
                    break
                    
        # Clear processed requests
        self.pending_requests.clear()
    
    def _allocate_resource(self, cell: CoreBaseCell, agent: CoreBaseAgent, amount: float) -> None:
        """
        Create and allocate a resource to an agent.
        
        Args:
            cell: Source cell of the resource
            agent: Target agent receiving the resource
            amount: Amount of resource to allocate
        """
        if not hasattr(agent, 'pending_resources'):
            agent.pending_resources = []
            
        resource = Resource(
            name=getattr(cell, 'resource_type', 'generic'),
            quantity=amount,
            # Resource quality decreases with pollution
            quality=max(0.0, 1.0 - cell.ground_pollution)
        )
        agent.pending_resources.append(resource)
        cell.current_resources -= amount
