import simpy
import random
from pydantic import BaseModel, Field
from typing import Optional

class Cell(BaseModel):
    env: simpy.Environment
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    population: int = Field(default_factory=lambda: random.randint(1, 100))
    process: Optional[simpy.events.Process] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.process = self.env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(1)  # Wait for a week

    def calculate_co2_impact(self) -> float:
        """Calculate how much CO2 this cell produces (positive) or absorbs (negative)"""
        raise NotImplementedError
