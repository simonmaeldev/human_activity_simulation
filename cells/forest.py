from typing import ClassVar
from .cell import Cell

class Forest(Cell):
    resource_type: ClassVar[str] = "wood"
    
    def __init__(self, **data):
        # Set forest-specific resource values
        data.setdefault("max_resources", 500.0)  # 500 units of wood
        data.setdefault("current_resources", 500.0)  # Start full
        data.setdefault("regeneration_rate", 10.0)  # Regenerate 10 units per tick
        super().__init__(**data)
        
    def regenerate_resources(self) -> None:
        """Regenerate wood resources in the forest"""
        new_amount = min(
            self.max_resources,
            self.current_resources + self.regeneration_rate
        )
        self.current_resources = new_amount
