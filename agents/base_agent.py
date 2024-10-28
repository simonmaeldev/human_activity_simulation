from abc import ABC, abstractmethod
from typing import Optional
import simpy

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    """
    
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.process: Optional[simpy.Process] = None
        
    @abstractmethod
    async def run(self):
        """Main behavior loop for the agent"""
        pass
    
    @abstractmethod
    def make_decision(self):
        """Make a decision based on current environment state"""
        pass
