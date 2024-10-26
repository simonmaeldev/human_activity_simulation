import simpy
import random
from typing import List, Dict, Optional
from cell import Cell, CellType
from population import Population, PopulationType
from config_model import ConfigModel
from constants import (
    HUMAN_GROWTH_RATE, HUMAN_DECLINE_RATE,
    AIR_POLLUTION_HEALTH_IMPACT, GROUND_POLLUTION_HEALTH_IMPACT,
    NATURE_PROXIMITY_BONUS, WILDLIFE_BASE_HEALTH_DECLINE,
    TREE_CO2_ABSORPTION_FACTOR, TREE_GROWTH_RATE,
    FOREST_SPREAD_CHANCE, COMMUTE_POLLUTION_MULTIPLIER,
    MAX_HUMAN_DENSITY, MAX_TREE_DENSITY,
    CITY_ABANDONMENT_DAYS, LAND_TO_FOREST_DAYS
)

class BasePopulationProcess:
    """
    Base class for all population processes in the simulation.
    Provides common functionality for population management and health updates.
    
    This abstract class defines the interface that all population types must implement,
    ensuring consistent behavior across different population types (humans, trees, wildlife).
    """
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        """
        Initialize a population process with its environment and configuration.
        
        Args:
            env: SimPy environment for process scheduling
            population: The population being managed
            cell: The cell where this population exists
            config: Global configuration parameters
        """
        self.env = env
        self.population = population
        self.cell = cell
        self.config = config
        self.active = True
        self.process = env.process(self.run())

    def stop(self):
        """Gracefully stop this population process"""
        self.active = False

    async def run(self):
        """
        Abstract method that must be implemented by subclasses.
        Defines the main behavior loop for each population type.
        """
        raise NotImplementedError("Subclasses must implement run()")

    async def update_health(self, amount: float):
        """
        Update population health level, keeping it within 0-100 range.
        
        Args:
            amount: Health change amount (positive or negative)
        """
        self.population.health_level = max(0.0, min(100.0, self.population.health_level + amount))

class HumanPopulation(BasePopulationProcess):
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.work_cycle = env.process(self.daily_cycle())
        self.growth_cycle = env.process(self.growth_process())
        self.health_cycle = env.process(self.health_update_process())

    async def daily_cycle(self):
        """
        Simulates daily human activities including:
        - Work commuting and associated pollution generation
        - Resource consumption for daily needs
        - Environmental impact calculations
        
        This cycle runs continuously while the population is active, with each
        iteration representing one day in the simulation. The pollution generated
        and resources consumed scale with population size.
        """
        while self.active:
            # Calculate and apply commuting pollution impact
            pollution_generated = (self.population.pollution_generation_rate * 
                                 self.population.size * 
                                 COMMUTE_POLLUTION_MULTIPLIER)
            self.cell.air_pollution_level += pollution_generated  # Pollution goes into the air first
            
            # Calculate and apply daily resource consumption
            self.cell.resource_level -= (self.population.resource_consumption_rate * 
                                       self.population.size)
            
            # Wait for next day
            await self.env.timeout(1)  # One step = one day

    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.work_cycle = env.process(self.daily_cycle())
        self.growth_cycle = env.process(self.growth_process())
        self.health_cycle = env.process(self.health_update_process())
        self.days_abandoned = 0  # Track how long a city has been below viable population

    async def growth_process(self):
        """
        Manages population growth and decline based on environmental conditions.
        
        This process:
        1. Evaluates environmental conditions (health and resources)
        2. Triggers growth when conditions are favorable
        3. Manages population decline in poor conditions
        4. Handles city expansion and abandonment
        5. Runs on a weekly cycle
        
        The process implements realistic urban dynamics where:
        - Cities grow when conditions are good
        - Population declines in poor conditions
        - Cities can be abandoned if population drops too low
        - New cities can form through expansion
        """
        while self.active:
            current_density = self.population.size
            
            # Check environmental conditions for growth/decline
            growth_conditions = (
                self.cell.health_level > self.config.health_thresholds["good"] and 
                self.cell.resource_level > self.config.population_growth_decline_thresholds["growth"]
            )
            decline_conditions = (
                self.cell.health_level < self.config.health_thresholds["poor"] or 
                self.cell.resource_level < self.config.population_growth_decline_thresholds["decline"]
            )

            if growth_conditions:
                if current_density < MAX_HUMAN_DENSITY:
                    # Normal growth within density limits
                    self.population.size = int(self.population.size * HUMAN_GROWTH_RATE)
                else:
                    # Try to expand to adjacent land when at capacity
                    await self.try_expand_city()
            elif decline_conditions:
                # Apply population decline
                self.population.size = int(self.population.size * HUMAN_DECLINE_RATE)
                
                # Track potential city abandonment
                if self.population.size < MAX_HUMAN_DENSITY * 0.1:  # Less than 10% capacity
                    self.days_abandoned += 7
                    if self.days_abandoned >= CITY_ABANDONMENT_DAYS:
                        self.cell.cell_type = CellType.LAND  # Convert abandoned city to land
                else:
                    self.days_abandoned = 0
            
            await self.env.timeout(7)  # Weekly population assessment

    async def try_expand_city(self):
        for neighbor in self.cell.neighbors:
            if (neighbor.cell_type == CellType.LAND and 
                neighbor.health_level > self.config.health_thresholds["good"] and
                not any(p.type == PopulationType.HUMANS for p in neighbor.populations)):
                # Convert land to city
                neighbor.cell_type = CellType.CITY
                # Create new human population in the new city
                initial_population = int(self.population.size * 0.1)  # 10% of original population moves
                self.population.size -= initial_population
                new_pop = Population(
                    type=PopulationType.HUMANS,
                    size=initial_population,
                    health_level=self.population.health_level,
                    resource_consumption_rate=self.population.resource_consumption_rate,
                    pollution_generation_rate=self.population.pollution_generation_rate
                )
                neighbor.populations.append(new_pop)
                break

    async def health_update_process(self):
        while self.active:
            # Health impact from both air and ground pollution
            pollution_impact = (AIR_POLLUTION_HEALTH_IMPACT * self.cell.air_pollution_level + 
                              GROUND_POLLUTION_HEALTH_IMPACT * self.cell.ground_pollution_level)
            
            # Benefit from nearby nature
            nature_bonus = sum(1 for neighbor in self.cell.neighbors 
                             if neighbor.cell_type in [CellType.FOREST, CellType.LAKE]) * NATURE_PROXIMITY_BONUS
            
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
            absorption_rate = (self.population.size * TREE_CO2_ABSORPTION_FACTOR * 
                             (self.population.health_level / 100) * 
                             (1 - self.cell.current_pollution_level / 100))
            
            self.cell.global_co2_level -= absorption_rate
            await self.env.timeout(1)

    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.co2_process = env.process(self.co2_absorption_process())
        self.growth_process = env.process(self.growth_cycle())
        self.days_unused = 0  # Track how long land has been unused

    async def growth_cycle(self):
        while self.active:
            current_density = self.population.size
            growth_conditions = (
                self.cell.health_level > 70 and 
                self.cell.resource_level > self.config.resource_regeneration_rates["forest"]
            )

            if growth_conditions:
                if current_density < MAX_TREE_DENSITY:
                    self.population.size = int(self.population.size * TREE_GROWTH_RATE)
                
                # Potential spread to adjacent cells
                for neighbor in self.cell.neighbors:
                    if neighbor.cell_type == CellType.LAND:
                        if not any(p.type != PopulationType.TREES for p in neighbor.populations):
                            neighbor.days_unused += 30
                            if (neighbor.days_unused >= LAND_TO_FOREST_DAYS and
                                neighbor.health_level > 80 and
                                neighbor.resource_level > self.config.resource_regeneration_rates["forest"] and
                                random.random() < FOREST_SPREAD_CHANCE):
                                neighbor.cell_type = CellType.FOREST
                                neighbor.days_unused = 0
                    elif neighbor.cell_type == CellType.CITY:
                        if neighbor.days_abandoned >= CITY_ABANDONMENT_DAYS:
                            # Abandoned cities can be reclaimed by forest
                            if random.random() < FOREST_SPREAD_CHANCE:
                                neighbor.cell_type = CellType.FOREST
                                neighbor.days_abandoned = 0
            
            await self.env.timeout(30)  # Monthly growth check

class WildlifePopulation(BasePopulationProcess):
    def __init__(self, env: simpy.Environment, population: Population, cell: Cell, config: ConfigModel):
        super().__init__(env, population, cell, config)
        self.consumption_process = env.process(self.resource_consumption_process())
        self.relocation_process = env.process(self.relocation_check_process())

    async def resource_consumption_process(self):
        """
        Manages wildlife resource consumption and related health impacts.
        
        This process:
        1. Calculates and consumes resources based on population size
        2. Adjusts health based on resource quality and pollution
        3. Applies base health decline to model natural attrition
        4. Runs daily to simulate continuous resource needs
        
        The process models realistic wildlife behavior where:
        - Resource consumption is limited by availability
        - Polluted resources negatively impact health
        - Population naturally declines without sufficient resources
        """
        while self.active:
            # Calculate and apply resource consumption
            consumed = min(self.cell.resource_level, 
                         self.population.resource_consumption_rate * self.population.size)
            self.cell.resource_level -= consumed
            
            # Calculate health impact based on resource quality
            quality_factor = 1 - (self.cell.current_pollution_level / 100)
            await self.update_health((consumed / self.population.size) * quality_factor - WILDLIFE_BASE_HEALTH_DECLINE)
            
            await self.env.timeout(1)  # Daily consumption cycle

    async def relocation_check_process(self):
        """
        Manages wildlife population movement and survival based on environmental conditions.
        
        This process:
        1. Monitors cell health conditions
        2. Triggers wildlife relocation when conditions become critical
        3. Reduces population if no suitable habitat is found
        4. Can lead to local extinction if conditions remain poor
        
        The process models realistic wildlife behavior where:
        - Animals attempt to relocate when habitat becomes unhealthy
        - Population declines if unable to find suitable new habitat
        - Complete population loss can occur in sustained poor conditions
        """
        while self.active:
            if self.cell.health_level < self.config.health_thresholds["critical"]:
                suitable_cell = self.find_suitable_cell()
                if suitable_cell:
                    # Relocate population to healthier habitat
                    suitable_cell.populations.append(self.population)
                    self.cell.populations.remove(self.population)
                    self.cell = suitable_cell
                else:
                    # Population decline due to habitat loss
                    self.population.size = int(self.population.size * 0.5)
                    if self.population.size <= 0:
                        self.stop()  # Population extinction
            
            await self.env.timeout(24)  # Daily habitat assessment

    def find_suitable_cell(self) -> Optional[Cell]:
        """
        Searches for a suitable new habitat cell for wildlife relocation.
        
        This method:
        1. Evaluates neighboring cells for habitat suitability
        2. Considers cell health and existing populations
        3. Prioritizes cells of matching type (forest/lake)
        
        Returns:
            Optional[Cell]: A suitable cell for relocation, or None if none found
        
        Note: Current implementation is a placeholder. Full implementation
        would need to consider:
        - Distance from current cell
        - Resource availability
        - Existing wildlife populations
        - Migration corridors
        """
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
