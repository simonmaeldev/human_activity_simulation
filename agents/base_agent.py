from abc import ABC, abstractmethod
from typing import List, Optional
from cell import Cell, CellType
from population import Population, PopulationType

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    """
    def __init__(self, population: Population, cell: Cell):
        self.population = population
        self.cell = cell
        self.memory = {}  # Store agent's experiences/knowledge
        
    @abstractmethod
    def make_decisions(self) -> List[str]:
        """
        Core decision-making method that each agent type must implement.
        Returns list of decisions made for logging/analysis.
        """
        pass
        
    def evaluate_cell_quality(self, cell: Cell) -> float:
        """
        Evaluate a cell's quality for this agent type.
        Considers health, resources, pollution, and cell type.
        """
        resource_quality = cell.resource_level / 100
        health_quality = cell.health_level / 100
        pollution_impact = cell.current_pollution_level / 100
        
        return (resource_quality * 0.4 + 
                health_quality * 0.4 + 
                (1 - pollution_impact) * 0.2)
                
    def find_best_neighbor(self, neighbors: List[Cell]) -> Optional[Cell]:
        """Find the best neighboring cell for potential migration"""
        if not neighbors:
            return None
            
        scored_neighbors = [
            (self.evaluate_cell_quality(cell), cell)
            for cell in neighbors
        ]
        return max(scored_neighbors, key=lambda x: x[0])[1]
