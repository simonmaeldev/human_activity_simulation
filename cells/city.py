from .cell import Cell
from agents import HumanAgent

class City(Cell):
    def __init__(self, **data):
        super().__init__(**data)
        # Add initial human population
        human = HumanAgent(env=self.env)
        self.add_agent(human)
