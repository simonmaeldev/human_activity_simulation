import simpy
import random
from typing import List, Dict, Optional
from cell import Cell, CellType
from population import Population, PopulationType
from config_model import ConfigModel

class BasePopulationProcess:
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        self.env = env
        self.population = population
        self.cell = cell
        self.config = config
        self.active = True
        self.process = env.process(self.run())

    def stop(self):
        self.active = False

    async def run(self):
        raise NotImplementedError("Subclasses must implement run()")

    async def update_health(self, amount: float):
        self.population.health_level = max(0.0, min(100.0, self.population.health_level + amount))

class HumanPopulation(BasePopulationProcess):
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.work_cycle = env.process(self.daily_cycle())
        self.growth_cycle = env.process(self.growth_process())
        self.health_cycle = env.process(self.health_update_process())

    async def daily_cycle(self):
        while self.active:
            # Morning commute
            self.cell.current_pollution_level += self.population.pollution_generation_rate
            await self.env.timeout(1)

            # Work period
            await self.env.timeout(self.config.human_work_cycle_duration)

            # Resource consumption
            self.cell.resource_level -= (self.population.resource_consumption_rate * self.population.size)
            await self.env.timeout(1)

            # Evening commute
            self.cell.current_pollution_level += self.population.pollution_generation_rate
            await self.env.timeout(1)

            # Rest period
            await self.env.timeout(12)  # 12-hour rest period

    async def growth_process(self):
        while self.active:
            if (self.cell.health_level > self.config.health_thresholds["good"] and 
                self.cell.resource_level > self.config.population_growth_decline_thresholds["growth"]):
                self.population.size = int(self.population.size * 1.1)  # 10% growth
            elif (self.cell.health_level < self.config.health_thresholds["poor"] or 
                  self.cell.resource_level < self.config.population_growth_decline_thresholds["decline"]):
                self.population.size = int(self.population.size * 0.9)  # 10% decline
            
            await self.env.timeout(24 * 7)  # Check weekly

    async def health_update_process(self):
        while self.active:
            # Health impact from polluted resources
            pollution_impact = -0.1 * self.cell.current_pollution_level
            
            # Benefit from nearby nature
            nature_bonus = sum(1 for neighbor in self.cell.neighbors 
                             if neighbor.cell_type in [CellType.FOREST, CellType.LAKE]) * 0.05
            
            await self.update_health(pollution_impact + nature_bonus)
            await self.env.timeout(1)

class TreePopulation(BasePopulationProcess):
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.co2_process = env.process(self.co2_absorption_process())
        self.growth_process = env.process(self.growth_cycle())

    async def co2_absorption_process(self):
        while self.active:
            # CO2 absorption rate based on health and pollution
            absorption_rate = (self.population.size * 0.1 * 
                             (self.population.health_level / 100) * 
                             (1 - self.cell.current_pollution_level / 100))
            
            self.cell.global_co2_level -= absorption_rate
            await self.env.timeout(1)

    async def growth_cycle(self):
        while self.active:
            if (self.cell.health_level > 70 and 
                self.cell.resource_level > self.config.resource_regeneration_rates["forest"]):
                self.population.size = int(self.population.size * 1.05)  # 5% growth
                
                # Potential spread to adjacent cells
                for neighbor in self.cell.neighbors:
                    if (neighbor.cell_type == CellType.LAND and 
                        neighbor.health_level > 80 and 
                        neighbor.resource_level > self.config.resource_regeneration_rates["forest"]):
                        # Chance to convert to forest
                        if random.random() < 0.1:  # 10% chance
                            neighbor.cell_type = CellType.FOREST
            
            await self.env.timeout(24 * 30)  # Monthly growth check

class WildlifePopulation(BasePopulationProcess):
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.consumption_process = env.process(self.resource_consumption_process())
        self.relocation_process = env.process(self.relocation_check_process())

    async def resource_consumption_process(self):
        while self.active:
            consumed = min(self.cell.resource_level, 
                         self.population.resource_consumption_rate * self.population.size)
            self.cell.resource_level -= consumed
            
            # Health impact based on resource quality
            quality_factor = 1 - (self.cell.current_pollution_level / 100)
            await self.update_health((consumed / self.population.size) * quality_factor - 0.1)
            
            await self.env.timeout(1)

    async def relocation_check_process(self):
        while self.active:
            if self.cell.health_level < self.config.health_thresholds["critical"]:
                suitable_cell = self.find_suitable_cell()
                if suitable_cell:
                    # Move population to new cell
                    suitable_cell.populations.append(self.population)
                    self.cell.populations.remove(self.population)
                    self.cell = suitable_cell
                else:
                    # Population dies off
                    self.population.size = int(self.population.size * 0.5)
                    if self.population.size <= 0:
                        self.stop()
            
            await self.env.timeout(24)  # Daily check

    def find_suitable_cell(self) -> Optional[Cell]:
        # Find nearest cell with good health and matching type
        # Implementation depends on grid structure
        return None

class PopulationManager:
    def __init__(self, env: simpy.Environment, config: ConfigModel):
        self.env = env
        self.config = config
        self.populations: Dict[Cell, List[BasePopulationProcess]] = {}

    def add_population(self, population: Population, cell: Cell):
        if cell not in self.populations:
            self.populations[cell] = []

        process_class = {
            PopulationType.HUMANS: HumanPopulation,
            PopulationType.TREES: TreePopulation,
            PopulationType.WILDLIFE: WildlifePopulation,
        }.get(population.type)

        if process_class:
            process = process_class(self.env, population, cell, self.config)
            self.populations[cell].append(process)

    def manage_resources(self):
        """Ensure humans have priority access to resources"""
        for cell, processes in self.populations.items():
            # Sort processes to prioritize humans
            processes.sort(key=lambda p: p.population.type != PopulationType.HUMANS)
