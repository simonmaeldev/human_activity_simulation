from cell import Cell
from pydantic import Field

class City(Cell):
    emission_rate: float = Field(default=0.1, description="CO2 emission per person per week")

City.model_rebuild()

    def process_environment(self):
        emission = self.population * self.emission_rate
        self.environment.global_co2_level += emission
        print(f"Week {self.env.now}: City at ({self.x}, {self.y}) emitted {emission:.2f} CO2. Global CO2: {self.environment.global_co2_level:.2f}")
