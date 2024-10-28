import simpy
import random
from pydantic import BaseModel, Field
from typing import Optional, ForwardRef

GlobalEnvironment = ForwardRef('GlobalEnvironment')

class Cell(BaseModel):
    env: simpy.Environment
    global_env: 'GlobalEnvironment'
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    population: int = Field(default_factory=lambda: random.randint(1, 100))
    process: Optional[simpy.events.Process] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.process = self.env.process(self.run())

    async def run(self):
        while True:
            self.process_environment()
            yield self.env.timeout(1)  # Wait for a week

    def process_environment(self):
        """Each cell type must implement its environmental impact"""
        raise NotImplementedError
