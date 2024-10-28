from cell import Cell
from pydantic import Field

class Forest(Cell):
    absorption_rate: float = Field(default=0.2, description="CO2 absorption per tree per week")

    def process_environment(self):
        absorption = self.population * self.absorption_rate
        self.environment.global_co2_level = max(0, self.environment.global_co2_level - absorption)
        print(f"Week {self.env.now}: Forest at ({self.x}, {self.y}) absorbed {absorption:.2f} CO2. Global CO2: {self.environment.global_co2_level:.2f}")

Forest.model_rebuild()
