from .base_agent import BaseAgent

class HumanAgent(BaseAgent):
    """
    Agent representing a human individual in the simulation.
    Makes decisions about resource consumption and movement.
    """
    
    def __init__(self, env: simpy.Environment):
        super().__init__(env)
        self.resources = 100  # Starting resources
        
    async def run(self):
        while True:
            self.make_decision()
            yield self.env.timeout(1)  # Wait one time step
            
    def make_decision(self):
        """
        Make decisions about:
        - Resource consumption
        - Movement between cells
        - Interaction with environment
        """
        # TODO: Implement decision-making logic
        pass
