from .base_agent import BaseAgent

class TreeAgent(BaseAgent):
    """
    Agent representing a tree in the simulation.
    Makes decisions about growth and resource usage.
    """
    
    def __init__(self, env: simpy.Environment):
        super().__init__(env)
        self.height = 1  # Starting height in meters
        
    async def run(self):
        while True:
            self.make_decision()
            yield self.env.timeout(1)  # Wait one time step
            
    def make_decision(self):
        """
        Make decisions about:
        - Growth rate
        - Resource absorption
        - CO2 absorption
        """
        # TODO: Implement decision-making logic
        pass
