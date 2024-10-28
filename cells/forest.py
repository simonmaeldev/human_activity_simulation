from .cell import Cell

class Forest(Cell):
    def calculate_co2_impact(self) -> float:
        """Calculate total CO2 impact from all agents in the forest cell"""
        return sum(agent.calculate_co2_impact() for agent in self.agents)
