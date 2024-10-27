from pydantic import BaseModel, Field
from typing import Tuple, Dict, Optional, Any

class ConfigModel(BaseModel):
    grid_size: Tuple[int, int] = Field(default=(100, 100), description="Grid size as (width, height)")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducible simulations")
    simulation_dir: Optional[str] = Field(default=None, description="Directory for simulation output files")
    initial_co2_level: float = Field(default=0.0, description="Initial global CO2 level")
    base_pollution_decay_rate: float = Field(default=0.01, description="Base rate at which pollution decays")
    health_thresholds: Dict[str, float] = Field(default={"critical": 20.0, "poor": 50.0, "good": 80.0}, description="Health thresholds for populations")
    resource_regeneration_rates: Dict[str, float] = Field(default={"city": 0.1, "forest": 0.5, "lake": 0.3, "land": 0.2}, description="Resource regeneration rates per cell type")
    population_growth_decline_thresholds: Dict[str, float] = Field(default={"growth": 0.2, "decline": 0.1}, description="Population growth and decline thresholds")
    cell_conversion_thresholds: Dict[str, float] = Field(default={"forest_to_land": 0.3, "land_to_city": 0.5}, description="Thresholds for converting cell types")
    pollution_spread_rates: Dict[str, float] = Field(default={"city": 0.2, "forest": 0.1, "lake": 0.05, "land": 0.15}, description="Pollution spread rates per cell type")
    resource_consumption_rates: Dict[str, float] = Field(default={"humans": 1.0, "wildlife": 0.5, "fish": 0.3, "pests": 0.2, "trees": 0.1}, description="Resource consumption rates per population type")
    human_work_cycle_duration: int = Field(default=8, description="Duration of human work cycle in hours")
    visualization_figsize: Tuple[int, int] = Field(default=(10, 10), description="Figure size for visualizations (width, height)")
    resource_manager: Any = Field(default=None, description="Resource manager instance")

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
