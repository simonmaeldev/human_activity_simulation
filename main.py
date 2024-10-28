import simpy
import random
from city import City
from forest import Forest
from cell import Cell
from pydantic import BaseModel, Field

class GlobalEnvironment(BaseModel):
    global_co2_level: float = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

class Grid(BaseModel):
    env: simpy.Environment
    global_env: GlobalEnvironment
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    cells: list[list[Cell]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.cells = [[self.create_cell(x, y) for y in range(self.height)] for x in range(self.width)]

    def create_cell(self, x, y):
        cell_class = random.choice([City, Forest])
        return cell_class(self.env, self.global_env, x, y)

def run_simulation(weeks):
    env = simpy.Environment()
    global_env = GlobalEnvironment()
    grid = Grid(env, global_env, 10, 10)
    env.run(until=weeks)
    print(f'total co2 after {weeks} weeks: {global_env.global_co2_level}')

# Run the simulation for 52 weeks (1 year)
run_simulation(52)
