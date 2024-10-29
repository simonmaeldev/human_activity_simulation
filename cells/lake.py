from typing import ClassVar
from .cell import Cell
from agents import WildlifeAgent, PlantAgent

class Lake(Cell):
    resource_type: ClassVar[str] = "water"
    
    def __init__(self, **data):
        # Set lake-specific resource values
        data.setdefault("max_resources", 1000.0)  # 1000 units of water
        data.setdefault("current_resources", 1000.0)  # Start full
        data.setdefault("regeneration_rate", 100.0)  # Regenerate 100 units per tick
        super().__init__(**data)
        # Add initial populations
        wildlife = WildlifeAgent(env=self.env)
        plant = PlantAgent(env=self.env)
        
        self.add_agent(wildlife)
        self.add_agent(plant)
        
    def regenerate_resources(self) -> None:
        """Regenerate water resources in the lake"""
        new_amount = min(
            self.max_resources,
            self.current_resources + self.regeneration_rate
        )
        self.current_resources = new_amount
