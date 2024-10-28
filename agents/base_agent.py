from typing import Optional
import simpy
from pydantic import BaseModel, Field

class BaseAgent(BaseModel):
    """
    Base class for all agents in the simulation.
    Defines core agent behaviors and decision-making interface.
    """
    env: simpy.Environment
    process: Optional[simpy.Process] = None
    health: float = Field(default=1.0, ge=0.0, le=1.0)  # Health level between 0 and 1

    class Config:
        arbitrary_types_allowed = True
    
    def run(self):
        """Main behavior loop for the agent"""
        while True:
            self.make_decision()
            yield self.env.timeout(1)
    
    def make_decision(self):
        """Make a decision based on current environment state"""
        raise NotImplementedError
