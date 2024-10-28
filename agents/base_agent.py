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
    
    async def run(self):
        """Main behavior loop for the agent"""
        while True:
            # Update health based on local pollution
            if hasattr(self, 'cell') and self.cell:
                pollution_impact = self.cell.co2_level / 1000  # Scale factor for pollution impact
                self.health = max(0.0, min(1.0, self.health - pollution_impact))
                
                # Agent dies if health reaches 0
                if self.health <= 0:
                    print(f"{self.__class__.__name__} died due to pollution")
                    return
                
            self.make_decision()
            yield self.env.timeout(1)
    
    def make_decision(self):
        """Make a decision based on current environment state"""
        raise NotImplementedError
