from cell import Cell
from pydantic import Field

class City(Cell):
    emission_rate: float = Field(default=0.1, description="CO2 emission per person per week")

    def calculate_co2_impact(self) -> float:
        return self.population * self.emission_rate
