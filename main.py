import simpy
import random
from city import City
from forest import Forest

class GlobalEnvironment:
    def __init__(self):
        self.global_co2_level = 0

class Grid:
    def __init__(self, env, global_env, width, height):
        self.env = env
        self.global_env = global_env
        self.width = width
        self.height = height
        self.cells = [[self.create_cell(x, y) for y in range(height)] for x in range(width)]

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
