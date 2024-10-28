import simpy
from environment import Environment

def run_simulation(weeks: int):
    env = simpy.Environment()
    environment = Environment(env=env, width=10, height=10)
    env.run(until=weeks)
    print(f'total co2 after {weeks} weeks: {environment.global_co2_level}')

# Run the simulation for 52 weeks (1 year)
run_simulation(52)
