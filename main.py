import simpy
import random

class GlobalEnvironment:
    def __init__(self):
        self.global_co2_level = 0

class Cell:
    def __init__(self, env, global_env, x, y, cell_type):
        self.env = env
        self.global_env = global_env
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.population = random.randint(1, 100)
        self.env.process(self.run())

    def run(self):
        while True:
            if self.cell_type == 'city':
                self.emit_co2()
            elif self.cell_type == 'forest':
                self.absorb_co2()
            yield self.env.timeout(1)  # Wait for a week

    def emit_co2(self):
        emission = self.population * 0.1  # Each person emits 0.1 units of CO2 per week
        self.global_env.global_co2_level += emission
        print(f"Week {self.env.now}: City at ({self.x}, {self.y}) emitted {emission:.2f} CO2. Global CO2: {self.global_env.global_co2_level:.2f}")

    def absorb_co2(self):
        absorption = self.population * 0.2  # Each tree absorbs 0.2 units of CO2 per week
        self.global_env.global_co2_level = max(0, self.global_env.global_co2_level - absorption)
        print(f"Week {self.env.now}: Forest at ({self.x}, {self.y}) absorbed {absorption:.2f} CO2. Global CO2: {self.global_env.global_co2_level:.2f}")

class Grid:
    def __init__(self, env, global_env, width, height):
        self.env = env
        self.global_env = global_env
        self.width = width
        self.height = height
        self.cells = [[self.create_cell(x, y) for y in range(height)] for x in range(width)]

    def create_cell(self, x, y):
        cell_type = random.choice(['city', 'forest'])
        return Cell(self.env, self.global_env, x, y, cell_type)

def run_simulation(weeks):
    env = simpy.Environment()
    global_env = GlobalEnvironment()
    grid = Grid(env, global_env, 10, 10)
    env.run(until=weeks)
    print(f'total co2 after {weeks} weeks: {global_env.global_co2_level}')

# Run the simulation for 52 weeks (1 year)
run_simulation(52)