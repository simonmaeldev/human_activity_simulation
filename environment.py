import simpy
import random
from cells import Cell, City, Forest, Lake
from pydantic import BaseModel, Field
from typing import List, Optional
from agents import HumanAgent, WildlifeAgent, PlantAgent, TreeAgent
from utils.cell_search import CellSearchManager
from resource_manager import ResourceManager

class Environment(BaseModel):
    env: simpy.Environment
    global_co2_level: float = Field(default=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    cells: List[List[Cell]] = Field(default_factory=list)
    process: Optional[simpy.Process] = None
    cell_search_manager: Optional[CellSearchManager] = None
    resource_manager: Optional[ResourceManager] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.cell_search_manager = CellSearchManager(self.width, self.height)
        self.resource_manager = ResourceManager(self.env)
        self.cells = [[self.create_cell(x, y) for y in range(self.height)] for x in range(self.width)]
        self.cell_search_manager.set_grid(self.cells)
        self.process = self.env.process(self.run())

    def create_cell(self, x: int, y: int) -> Cell:
        cell_class = random.choice([City, Forest, Lake])
        cell = cell_class(env=self.env, x=x, y=y)
        
        # Add initial populations based on cell type
        if isinstance(cell, City):
            human = HumanAgent(
                env=self.env,
                position=(x,y),
                cell_search_manager=self.cell_search_manager,
                resource_manager=self.resource_manager
            )
            cell.add_agent(human)
        elif isinstance(cell, Forest):
            wildlife = WildlifeAgent(
                env=self.env,
                position=(x,y),
                cell_search_manager=self.cell_search_manager,
                resource_manager=self.resource_manager
            )
            plant = PlantAgent(
                env=self.env,
                position=(x,y),
                cell_search_manager=self.cell_search_manager,
                resource_manager=self.resource_manager
            )
            tree = TreeAgent(
                env=self.env,
                position=(x,y),
                cell_search_manager=self.cell_search_manager,
                resource_manager=self.resource_manager
            )
            cell.add_agent(wildlife)
            cell.add_agent(plant)
            cell.add_agent(tree)
        elif isinstance(cell, Lake):
            wildlife = WildlifeAgent(
                env=self.env,
                position=(x,y),
                cell_search_manager=self.cell_search_manager,
                resource_manager=self.resource_manager
            )
            plant = PlantAgent(
                env=self.env,
                position=(x,y),
                cell_search_manager=self.cell_search_manager,
                resource_manager=self.resource_manager
            )
            cell.add_agent(wildlife)
            cell.add_agent(plant)
            
        return cell

    def run(self):
        while True:
            self.update_co2_levels()
            yield self.env.timeout(1)

    def update_co2_levels(self):
        total_impact = 0
        for row in self.cells:
            for cell in row:
                impact = cell.calculate_co2_impact()
                total_impact += impact
                cell_type = "City" if isinstance(cell, City) else "Forest"
                print(f"Week {self.env.now}: {cell_type} at ({cell.x}, {cell.y}) CO2 impact: {impact:.2f}")
        
        self.global_co2_level = max(0, self.global_co2_level + total_impact)
        print(f"Week {self.env.now}: Total CO2 impact: {total_impact:.2f}. Global CO2: {self.global_co2_level:.2f}")
