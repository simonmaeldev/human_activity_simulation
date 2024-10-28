import simpy
import random
from city import City
from forest import Forest
from cell import Cell
from pydantic import BaseModel, Field
from typing import List

class Environment(BaseModel):
    env: simpy.Environment
    global_co2_level: float = Field(default=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    cells: List[List[Cell]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.cells = [[self.create_cell(x, y) for y in range(self.height)] for x in range(self.width)]

    def create_cell(self, x: int, y: int) -> Cell:
        cell_class = random.choice([City, Forest])
        return cell_class(env=self.env, environment=self, x=x, y=y)
