import simpy
import random
import logging
from typing import List, Dict, Optional, Tuple
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
    CITY_ABANDONMENT_DAYS, LAND_TO_FOREST_DAYS,
    MAX_WILDLIFE_MOVEMENT_RADIUS, WILDLIFE_BASE_SUCCESS_RATE,
    WILDLIFE_DISTANCE_PENALTY, WILDLIFE_HEALTH_BONUS
)
from agents.base_agent import BaseAgent

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
        self.process = None
        self.work_cycle = None
        self.growth_cycle = None
        self.health_cycle = None

    def stop(self):
        """Gracefully stop this population process"""
        self.active = False

    def run(self):
        """Base run method that implements basic population mechanics"""
        try:
            # Start the growth and health cycles for all populations
            self.growth_cycle = self.env.process(self.growth_process())
            self.health_cycle = self.env.process(self.health_update_process())
            
            # Only start daily cycle if the population type has one
            if hasattr(self, 'daily_cycle'):
                self.work_cycle = self.env.process(self.daily_cycle())
            
            while self.active:
                # Basic population mechanics
                yield self.env.process(self.update_health(0))  # Base health change
                
                # Check for population extinction
                if self.population.size <= 0 or self.population.health_level <= 0:
                    self.stop()
                    if self.population in self.cell.populations:
                        self.cell.populations.remove(self.population)
                    break
                
                yield self.env.timeout(1)  # One step = one day
                
        except Exception as e:
            logging.error(f"Error in population process: {str(e)}")
            raise

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
        self.days_abandoned = 0  # Track how long a city has been below viable population

    def daily_cycle(self):
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
            yield self.env.timeout(1)  # One step = one day

    def growth_process(self):
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
                    yield self.env.process(self.try_expand_city())
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
            
            yield self.env.timeout(7)  # Weekly population assessment

    def try_expand_city(self):
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
        self.days_unused = 0  # Track how long land has been unused
        # Start the main process
        self.process = env.process(self.run())

    def co2_absorption_process(self):
        """Process CO2 absorption by trees through the environment's pollution manager"""
        while self.active:
            # CO2 absorption rate based on health and pollution
            absorption_rate = (self.population.size * TREE_CO2_ABSORPTION_FACTOR * 
                             (self.population.health_level / 100) * 
                             (1 - self.cell.current_pollution_level / 100))
            
            # Use environment's pollution manager to reduce CO2
            from environment import Environment
            env = Environment._instance
            env.pollution_manager.reduce_co2(absorption_rate)
            
            yield self.env.timeout(1)

    def health_update_process(self):
        """
        Update tree population health based on water consumption and pollution.
        Trees consume water from all adjacent water sources.
        Health changes are based on the pollution levels of consumed water.
        """
        while self.active:
            # Find all adjacent lake cells
            adjacent_lakes = [cell for cell in self.cell.neighbors 
                            if cell.cell_type == CellType.LAKE]
            
            if adjacent_lakes:
                total_health_change = 0
                water_sources = len(adjacent_lakes)
                
                for lake in adjacent_lakes:
                    # Calculate health impact from this water source
                    pollution_level = lake.current_pollution_level
                    health_change = self._calculate_health_change(pollution_level)
                    total_health_change += health_change / water_sources  # Average impact
                    
                    # Consume some water from this source
                    consumed = min(lake.resource_level, 
                                 self.population.resource_consumption_rate / water_sources)
                    lake.resource_level -= consumed
                
                # Apply total health change
                self.population.health_level = max(0.0, min(100.0, 
                    self.population.health_level + total_health_change))
            else:
                # Trees without water access slowly lose health
                self.population.health_level = max(0.0, 
                    self.population.health_level - 0.01)
            
            yield self.env.timeout(1)

    def _calculate_health_change(self, pollution_level: float) -> float:
        """
        Calculate health change based on pollution level of consumed water.
        
        Args:
            pollution_level: Current pollution level (0-100)
            
        Returns:
            float: Health change amount (-0.01 to +0.01)
        """
        # Linear interpolation between max gain (0% pollution) and max loss (100% pollution)
        max_change = 0.01
        return max_change * (1 - (2 * pollution_level / 100))

    def growth_process(self):
        """
        Manages tree population growth and spread based on environmental conditions.
        
        This process:
        1. Evaluates environmental conditions (health and resources)
        2. Triggers growth when conditions are favorable
        3. Manages natural spread to adjacent cells
        4. Runs on a monthly cycle (trees grow slower than other populations)
        """
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
            
            yield self.env.timeout(30)  # Monthly growth check

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
        self.process = env.process(self.run())

    async def health_update_process(self):
        """
        Update wildlife population health based on:
        - Resource quality (pollution levels)
        - Available food sources
        - Environmental conditions
        """
        while self.active:
            # Base health decline from natural causes
            health_change = -WILDLIFE_BASE_HEALTH_DECLINE
            
            # Calculate health impact from pollution
            pollution_impact = (
                AIR_POLLUTION_HEALTH_IMPACT * self.cell.air_pollution_level +
                GROUND_POLLUTION_HEALTH_IMPACT * self.cell.ground_pollution_level
            )
            
            # Bonus from being in natural habitat
            if self.cell.cell_type == CellType.FOREST:
                health_change += NATURE_PROXIMITY_BONUS
            
            # Resource quality impact
            consumed_resources = min(
                self.cell.resource_level,
                self.population.resource_consumption_rate * self.population.size
            )
            if consumed_resources > 0:
                quality_factor = 1 - (self.cell.current_pollution_level / 100)
                health_change += (consumed_resources / self.population.size) * quality_factor
            
            await self.update_health(health_change)
            await self.env.timeout(1)

    def resource_consumption_process(self):
        """
        Manages wildlife resource consumption and related health impacts.
        """
        while self.active:
            # Calculate and apply resource consumption
            consumed = min(self.cell.resource_level, 
                         self.population.resource_consumption_rate * self.population.size)
            self.cell.resource_level -= consumed
            
            # Calculate health impact based on resource quality
            quality_factor = 1 - (self.cell.current_pollution_level / 100)
            self.update_health((consumed / self.population.size) * quality_factor - WILDLIFE_BASE_HEALTH_DECLINE)
            
            yield self.env.timeout(1)  # Daily consumption cycle

    def relocation_check_process(self):
        """
        Manages wildlife population movement and survival based on environmental conditions.
        """
        while self.active:
            if self.cell.health_level < self.config.health_thresholds["critical"]:
                suitable_cell = self.find_suitable_cell()
                if suitable_cell:
                    # Relocate population to healthier habitat
                    suitable_cell.populations.append(self.population)
                    self.cell.populations.remove(self.population)
                    logging.info(
                        f"Wildlife migration: {self.population.size} animals migrated from "
                        f"cell {self.cell.position} to {suitable_cell.position} due to poor conditions"
                    )
                    self.cell = suitable_cell
                else:
                    # Population decline due to habitat loss
                    self.population.size = int(self.population.size * 0.5)
                    if self.population.size <= 0:
                        self.stop()  # Population extinction
            
            yield self.env.timeout(24)  # Daily habitat assessment

    def find_suitable_cell(self) -> Optional[Cell]:
        """Find suitable cells for wildlife within movement radius"""
        from environment import Environment
        env = Environment._instance
        
        suitable_cells = []
        x, y = self.cell.position
        
        # Check cells within radius
        for i in range(-MAX_WILDLIFE_MOVEMENT_RADIUS, MAX_WILDLIFE_MOVEMENT_RADIUS + 1):
            for j in range(-MAX_WILDLIFE_MOVEMENT_RADIUS, MAX_WILDLIFE_MOVEMENT_RADIUS + 1):
                if i == 0 and j == 0:  # Skip current cell
                    continue
                    
                # Check if within radius
                if (i*i + j*j) > MAX_WILDLIFE_MOVEMENT_RADIUS * MAX_WILDLIFE_MOVEMENT_RADIUS:
                    continue
                    
                new_x, new_y = x + i, y + j
                if 0 <= new_x < len(env.grid) and 0 <= new_y < len(env.grid[0]):
                    cell = env.grid[new_x][new_y]
                    if (cell.cell_type == CellType.FOREST and
                        cell.health_level > 70 and
                        cell.resource_level > 50):
                        suitable_cells.append(cell)
        
        return random.choice(suitable_cells) if suitable_cells else None

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def colonization_process(self):
        """
        Manages wildlife colonization of new territories.
        
        This process:
        1. Attempts to colonize nearby forests within movement radius
        2. Success chance based on:
           - Population health (higher health = better chance)
           - Distance to target (further = lower chance)
           - Base success rate
        3. May result in population loss during travel
        """
        while self.active:
            if (self.population.size > 50 and  # Minimum population for colonization
                self.population.health_level > 70):  # Good health required
                
                suitable_cell = self.find_suitable_cell()
                if suitable_cell:
                    distance = self._calculate_distance(self.cell.position, suitable_cell.position)
                    
                    # Calculate success chance
                    success_chance = (WILDLIFE_BASE_SUCCESS_RATE +
                                   (self.population.health_level / 100 * WILDLIFE_HEALTH_BONUS) -
                                   (distance * WILDLIFE_DISTANCE_PENALTY))
                    
                    if random.random() < success_chance:
                        # Determine colonizing population size (10-20% of current)
                        colonists = int(self.population.size * random.uniform(0.1, 0.2))
                        self.population.size -= colonists
                        
                        # Create new population in target cell
                        new_population = Population(
                            type=PopulationType.WILDLIFE,
                            size=colonists,
                            health_level=self.population.health_level * 0.8,  # Slight health penalty from travel
                            resource_consumption_rate=self.population.resource_consumption_rate,
                            pollution_generation_rate=self.population.pollution_generation_rate
                        )
                        
                        suitable_cell.populations.append(new_population)
                        logging.info(
                            f"Wildlife colonization: {colonists} animals successfully colonized "
                            f"from {self.cell.position} to {suitable_cell.position}"
                        )
                    else:
                        # Failed colonization attempt - some population lost
                        lost_population = int(self.population.size * 0.05)  # 5% loss on failure
                        self.population.size -= lost_population
                        logging.info(
                            f"Failed wildlife colonization: Lost {lost_population} animals "
                            f"attempting to move from {self.cell.position} to {suitable_cell.position}"
                        )
            
            yield self.env.timeout(30)  # Monthly colonization attempts
            
    def run(self):
        """Main process that starts all sub-processes"""
        while self.active:
            # Start all processes
            self.env.process(self.resource_consumption_process())
            self.env.process(self.relocation_check_process())
            self.env.process(self.colonization_process())
            self.env.process(self.health_update_process())
            yield self.env.timeout(1)

from agents.human_agent import HumanAgent
from agents.tree_agent import TreeAgent

class PopulationManager:
    def __init__(self, env: simpy.Environment, config: ConfigModel):
        self.env = env
        self.config = config
        self.populations: Dict[Tuple[int, int], List[BasePopulationProcess]] = {}
        self.agents: Dict[Population, BaseAgent] = {}
        self.resource_manager = None  # Will be set by SimulationController

    async def update_populations(self, grid: List[List[Cell]]):
        """Update all populations across the grid"""
        for cell in [cell for row in grid for cell in row]:
            # Create processes for new populations if needed
            for population in cell.populations:
                if cell.position not in self.populations:
                    await self.add_population(population, cell)
            
            # Run population processes
            if cell.position in self.populations:
                for process in self.populations[cell.position]:
                    # Ensure process is active
                    if not process.active:
                        process.active = True
                        process.process = self.env.process(await process.run())
            
            # Resource consumption for all populations
            if self.resource_manager:
                self.resource_manager.consume_resources(cell)

    async def add_population(self, population: Population, cell: Cell):
        if cell.position not in self.populations:
            self.populations[cell.position] = []

        process_class = {
            PopulationType.HUMANS: HumanPopulation,
            PopulationType.TREES: TreePopulation,
            PopulationType.WILDLIFE: WildlifePopulation,
        }.get(population.type)

        if process_class:
            process = process_class(self.env, population, cell, self.config)
            process.active = True
            process.process = self.env.process(process.run())
            self.populations[cell.position].append(process)
            
            # Create corresponding agent
            agent_class = {
                PopulationType.HUMANS: HumanAgent,
                PopulationType.TREES: TreeAgent,
            }.get(population.type)
            
            if agent_class:
                self.agents[population] = agent_class(population, cell, self.config)

    def manage_resources(self):
        """Ensure humans have priority access to resources"""
        # First let agents make decisions
        for population, agent in self.agents.items():
            decisions = agent.make_decisions()
            # Log decisions for analysis
            if decisions:
                logging.info(f"Agent decisions for {population.type}: {decisions}")
        for cell, processes in self.populations.items():
            # Sort processes to prioritize humans
            processes.sort(key=lambda p: p.population.type != PopulationType.HUMANS)
