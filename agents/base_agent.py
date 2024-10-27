from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from cell import Cell, CellType
from population import Population, PopulationType

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    
    Each agent represents an autonomous entity that can:
    - Make decisions about resource usage
    - Evaluate and respond to environmental conditions
    - Move between cells when needed
    - Track its history and learn from past decisions
    """
    def __init__(self, population: Population, cell: Cell):
        self.population = population
        self.cell = cell
        self.memory: Dict[str, Any] = {
            'previous_decisions': [],
            'visited_cells': set(),
            'resource_history': [],
            'health_history': []
        }
        
    @abstractmethod
    def make_decisions(self) -> List[str]:
        """
        Core decision-making method that each agent type must implement.
        Returns list of decisions made for logging/analysis.
        
        Decisions should consider:
        - Current cell conditions (health, pollution, resources)
        - Population needs (size, health, resource consumption)
        - Historical data (past decisions, visited locations)
        - Environmental threats (high pollution, low resources)
        """
        pass
        
    def evaluate_cell_quality(self, cell: Cell) -> float:
        """
        Evaluate a cell's quality for this agent type.
        Considers health, resources, pollution, and cell type.
        
        Returns:
            float: Quality score between 0.0 (worst) and 1.0 (best)
        """
        # Base factors
        resource_quality = cell.resource_level / 100
        health_quality = cell.health_level / 100
        pollution_impact = cell.current_pollution_level / 100
        
        # Cell type specific modifiers
        type_modifier = {
            CellType.CITY: 0.8 if self.population.type == PopulationType.HUMANS else 0.2,
            CellType.FOREST: 1.2 if self.population.type == PopulationType.TREES else 0.6,
            CellType.LAKE: 1.0 if self.population.type == PopulationType.FISH else 0.7,
            CellType.LAND: 0.9
        }.get(cell.cell_type, 0.5)
        
        base_score = (
            resource_quality * 0.4 + 
            health_quality * 0.4 + 
            (1 - pollution_impact) * 0.2
        )
        
        return min(1.0, base_score * type_modifier)
                
    def find_best_neighbor(self, neighbors: List[Cell]) -> Optional[Cell]:
        """
        Find the best neighboring cell for potential migration.
        
        Evaluates neighbors based on:
        - Cell quality score
        - Historical data (if previously visited)
        - Current population needs
        
        Returns:
            Optional[Cell]: Best neighbor cell or None if no suitable options
        """
        if not neighbors:
            return None
            
        scored_neighbors = []
        for cell in neighbors:
            base_score = self.evaluate_cell_quality(cell)
            
            # Apply historical knowledge modifier
            if cell.position in self.memory['visited_cells']:
                base_score *= 0.9  # Slight penalty for revisiting
                
            # Population size considerations
            if hasattr(self, 'get_density_score'):
                base_score *= self.get_density_score(cell)
                
            scored_neighbors.append((base_score, cell))
            
        return max(scored_neighbors, key=lambda x: x[0])[1]
        
    def update_memory(self, decision: str) -> None:
        """
        Update agent's memory with new decision and current state.
        
        Args:
            decision: String describing the decision made
        """
        self.memory['previous_decisions'].append(decision)
        self.memory['visited_cells'].add(self.cell.position)
        self.memory['resource_history'].append(self.cell.resource_level)
        self.memory['health_history'].append(self.population.health_level)
        
        # Keep memory size manageable
        if len(self.memory['previous_decisions']) > 100:
            self.memory['previous_decisions'] = self.memory['previous_decisions'][-100:]
        if len(self.memory['resource_history']) > 100:
            self.memory['resource_history'] = self.memory['resource_history'][-100:]
        if len(self.memory['health_history']) > 100:
            self.memory['health_history'] = self.memory['health_history'][-100:]
