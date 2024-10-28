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
    process: simpy.Process

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.cells = [[self.create_cell(x, y) for y in range(self.height)] for x in range(self.width)]
        self.process = self.env.process(self.run())

    def create_cell(self, x: int, y: int) -> Cell:
        cell_class = random.choice([City, Forest])
        return cell_class(env=self.env, x=x, y=y)

    def run(self):
        while True:
            self.update_co2_levels()
            yield self.env.timeout(1)

    def update_co2_levels(self):
        for row in self.cells:
            for cell in row:
                impact = cell.calculate_co2_impact()
                self.global_co2_level = max(0, self.global_co2_level + impact)
                cell_type = "City" if isinstance(cell, City) else "Forest"
                print(f"Week {self.env.now}: {cell_type} at ({cell.x}, {cell.y}) CO2 impact: {impact:.2f}. Global CO2: {self.global_co2_level:.2f}")
