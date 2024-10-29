from .cell import Cell
from agents import HumanAgent

class City(Cell):
    def __init__(self, **data):
        super().__init__(**data)
