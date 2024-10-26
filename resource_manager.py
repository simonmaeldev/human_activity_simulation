from typing import Dict, List
from cell import Cell, CellType
from config_model import ConfigModel
from population import Population, PopulationType

class ResourceManager:
    """
    Manages all resource-related operations in the simulation including:
    - Resource consumption with priority system (humans first, then wildlife, etc.)
    - Resource regeneration based on cell health and pollution
    - Resource transfer between cells
    - Resource quality calculations
    """
    def __init__(self, config: ConfigModel):
        self.config = config
        # Priority system ensures humans get resources first in times of scarcity
        # Lower number = higher priority
        self.resource_priorities = {
            PopulationType.HUMANS: 1,    # Humans get first access
            PopulationType.WILDLIFE: 2,  # Wildlife and fish share second priority
            PopulationType.FISH: 2,      # Important for ecosystem balance
            PopulationType.TREES: 3,     # Trees can survive longer without resources
            PopulationType.PESTS: 4      # Pests get last priority
        }

    def consume_resources(self, cell: Cell) -> Dict[Population, float]:
        """
        Handles resource consumption with priority system.
        
        This is a critical function that:
        1. Sorts populations by priority (humans first)
        2. Allocates resources based on need and availability
        3. Ensures higher priority populations get resources first
        4. Returns exactly how much each population consumed
        
        Returns:
            Dict[Population, float]: Maps each population to amount of resources they received
        
        Design choices:
        - Priority system prevents resource conflicts
        - Returns consumption data for tracking/statistics
        - Handles resource scarcity gracefully
        """
        consumption_results = {}
        available_resources = cell.resource_level
        
        # Sort populations by priority
        sorted_populations = sorted(
            cell.populations,
            key=lambda p: self.resource_priorities[p.type]
        )
        
        for population in sorted_populations:
            needed = population.resource_consumption_rate * population.size
            consumed = min(needed, available_resources)
            consumption_results[population] = consumed
            available_resources -= consumed
            
            if available_resources <= 0:
                break
                
        cell.resource_level = available_resources
        return consumption_results

    def regenerate_resources(self, cell: Cell):
        """
        Regenerates resources in a cell based on multiple factors.
        
        This function models natural resource regeneration by:
        1. Using base regeneration rate specific to cell type (forests regenerate faster than cities)
        2. Scaling by cell health (damaged cells regenerate slower)
        3. Reducing regeneration based on pollution (polluted areas recover slower)
        4. Capping resources at 100% to prevent overflow
        
        Design choices:
        - Multiplicative factors rather than additive to model compound effects
        - Cell type specific rates allow fine-tuning of different biomes
        - Resource cap prevents unrealistic accumulation
        """
        base_rate = self.config.resource_regeneration_rates[cell.cell_type.value]
        health_factor = cell.health_level / 100
        pollution_factor = 1 - (cell.current_pollution_level / 100)
        
        regeneration = base_rate * health_factor * pollution_factor
        cell.resource_level = min(100, cell.resource_level + regeneration)

    def transfer_resources(self, source: Cell, target: Cell, amount: float):
        """
        Transfers resources between cells safely.
        
        This critical function:
        1. Ensures we never transfer more than available
        2. Maintains conservation of resources
        3. Returns actual amount transferred for tracking
        
        Design choices:
        - Uses min() to prevent negative resources
        - Atomic operation (both cells updated together)
        - Returns transfer amount for verification
        
        Args:
            source: Cell giving resources
            target: Cell receiving resources
            amount: Desired transfer amount
            
        Returns:
            float: Actual amount transferred
        """
        actual_transfer = min(amount, source.resource_level)
        source.resource_level -= actual_transfer
        target.resource_level += actual_transfer
        return actual_transfer

    def calculate_resource_quality(self, cell: Cell) -> float:
        """
        Calculates the quality of resources in a cell.
        
        This function determines resource quality by:
        1. Converting pollution level to quality impact (higher pollution = lower quality)
        2. Factoring in cell health (healthier cells = better quality)
        3. Averaging these factors for final quality score
        4. Clamping result between 0-1
        
        Design choices:
        - Equal weighting between health and pollution
        - Uses average rather than multiplication to avoid too-low values
        - Bounded output ensures consistent range for consumers
        
        Returns:
            float: Resource quality score between 0.0 (worst) and 1.0 (best)
        """
        pollution_impact = cell.current_pollution_level / 100
        health_factor = cell.health_level / 100
        return max(0, min(1, (health_factor + (1 - pollution_impact)) / 2))
