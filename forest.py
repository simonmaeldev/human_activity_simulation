from cell import Cell

class Forest(Cell):
    def process_environment(self):
        absorption = self.population * 0.2  # Each tree absorbs 0.2 units of CO2 per week
        self.global_env.global_co2_level = max(0, self.global_env.global_co2_level - absorption)
        print(f"Week {self.env.now}: Forest at ({self.x}, {self.y}) absorbed {absorption:.2f} CO2. Global CO2: {self.global_env.global_co2_level:.2f}")
