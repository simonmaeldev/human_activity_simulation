from .cell import Cell
from agents import WildlifeAgent, PlantAgent

class Lake(Cell):
    def __init__(self, **data):
        super().__init__(**data)
        # Add initial populations
        wildlife = WildlifeAgent(env=self.env)
        plant = PlantAgent(env=self.env)
        
        self.add_agent(wildlife)
        self.add_agent(plant)
