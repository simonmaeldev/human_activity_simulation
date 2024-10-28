from cell import Cell

class City(Cell):
    def process_environment(self):
        emission = self.population * 0.1  # Each person emits 0.1 units of CO2 per week
        self.global_env.global_co2_level += emission
        print(f"Week {self.env.now}: City at ({self.x}, {self.y}) emitted {emission:.2f} CO2. Global CO2: {self.global_env.global_co2_level:.2f}")
