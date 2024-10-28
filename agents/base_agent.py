from typing import Optional
import simpy
from pydantic import BaseModel

class BaseAgent(BaseModel):
    """
    Base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    """
    env: simpy.Environment
    process: Optional[simpy.Process] = None

    class Config:
        arbitrary_types_allowed = True
    
    async def run(self):
        """Main behavior loop for the agent"""
        raise NotImplementedError
    
    def make_decision(self):
        """Make a decision based on current environment state"""
        raise NotImplementedError
