from .cell import Cell
from pydantic import Field

class Forest(Cell):
    absorption_rate: float = Field(default=0.2, description="CO2 absorption per tree per week")

    def calculate_co2_impact(self) -> float:
        return -self.population * self.absorption_rate  # Negative because it absorbs CO2
