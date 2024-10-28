import simpy
import random
from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, env, global_env, x, y):
        self.env = env
        self.global_env = global_env
        self.x = x
        self.y = y
        self.population = random.randint(1, 100)
        self.env.process(self.run())

    def run(self):
        while True:
            self.process_environment()
            yield self.env.timeout(1)  # Wait for a week

    @abstractmethod
    def process_environment(self):
        """Each cell type must implement its environmental impact"""
        pass
