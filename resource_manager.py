from typing import Dict, List, Optional
from cell import Cell, CellType
from config_model import ConfigModel
from population import Population, PopulationType
from water_system import WaterSystem

class ResourceManager:
    """
    Manages all resource-related operations in the simulation including:
    - Resource consumption with priority system (humans first, then wildlife, etc.)
    - Resource regeneration based on cell health and pollution
    - Resource transfer between cells
    - Resource quality calculations
    - Water flow between connected lakes
    - Irrigation effects on pollution
    
    Design Pattern: Manager/Service Pattern
    This class uses the Manager pattern instead of putting resource logic in Cell classes because:
    1. System-wide Policies: Manages global resource priorities across all cells
    2. Cross-Cell Interactions: Handles resource transfers and water flow between multiple cells
    3. Consistency: Ensures uniform resource rules across the simulation
    4. Single Responsibility: Separates resource logic from cell state management
    5. Easier Updates: Changes to resource rules only need to be made in one place
    
    Example: When a human population needs resources, instead of:
        cell.consume_resources(population)  # OOP way
    We use:
        resource_manager.consume_resources(cell)  # Manager pattern
    
    This allows the manager to enforce priorities and handle complex interactions
    between different populations and cell types consistently.
    """
    def __init__(self, config: ConfigModel, grid: List[List[Cell]]):
        self.config = config
        self.water_system = WaterSystem()
        self.grid = grid
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
        Handle resource consumption with priority system
        
        This method demonstrates why we use a manager:
        1. Priority System: Controls which populations get resources first
        2. Cross-Population Logic: Manages resource distribution across different types
        3. Pollution Transfer: Handles complex interactions between resources and pollution
        
        If this was in Cell class, each cell would need to implement its own
        priority system, leading to potential inconsistencies.
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
            
            # Transfer proportional pollution with consumed resources
            if consumed > 0:
                pollution_transfer = (consumed / cell.resource_level) * cell.ground_pollution_level
                cell.ground_pollution_level -= pollution_transfer
            
            available_resources -= consumed
            if available_resources <= 0:
                break
                
        cell.resource_level = available_resources
        return consumption_results

    def regenerate_resources(self, cell: Cell):
        """
        Handle resource regeneration based on cell type
        
        Manager Pattern Benefits Here:
        1. Different cell types (LAKE, LAND, FOREST) have different regeneration rules
        2. Centralized configuration of regeneration rates
        3. Consistent handling of health factors across all types
        4. Complex irrigation logic involving multiple cells
        
        This would be harder to maintain if split across different Cell subclasses.
        """
        if cell.cell_type == CellType.LAKE:
            self._regenerate_lake_resources(cell)
        elif cell.cell_type == CellType.LAND:
            self._regenerate_land_resources(cell)
        elif cell.cell_type == CellType.FOREST:
            self._regenerate_forest_resources(cell)
            
    def _regenerate_lake_resources(self, cell: Cell):
        """Handle lake water regeneration"""
        base_rate = self.config.resource_regeneration_rates["lake"]
        health_factor = cell.health_level / 100
        regeneration = base_rate * health_factor
        cell.resource_level = min(100, cell.resource_level + regeneration)
        
    def _regenerate_land_resources(self, cell: Cell):
        """Handle land food production with irrigation effects"""
        base_rate = self.config.resource_regeneration_rates["land"]
        health_factor = cell.health_level / 100
        
        # Find adjacent lake for irrigation
        adjacent_lake = self._find_adjacent_lake(cell)
        if adjacent_lake and adjacent_lake.resource_level > 20:  # Minimum water needed
            # Use water for irrigation
            water_used = min(20, adjacent_lake.resource_level)
            adjacent_lake.resource_level -= water_used
            
            # Irrigation helps clean pollution
            pollution_cleaned = water_used * 0.1  # 10% cleaning rate
            cell.ground_pollution_level = max(0, cell.ground_pollution_level - pollution_cleaned)
            
            # Bonus to food production from irrigation
            regeneration = base_rate * health_factor * 1.5  # 50% bonus
        else:
            regeneration = base_rate * health_factor
            
        cell.resource_level = min(100, cell.resource_level + regeneration)
        
    def _regenerate_forest_resources(self, cell: Cell):
        """Handle forest resource regeneration with water consumption"""
        base_rate = self.config.resource_regeneration_rates["forest"]
        health_factor = cell.health_level / 100
        
        # Find adjacent lake for water
        adjacent_lake = self._find_adjacent_lake(cell)
        if adjacent_lake and adjacent_lake.resource_level > 10:  # Minimum water needed
            water_used = min(10, adjacent_lake.resource_level)
            adjacent_lake.resource_level -= water_used
            regeneration = base_rate * health_factor
        else:
            regeneration = base_rate * health_factor * 0.5  # 50% penalty without water
            
        cell.resource_level = min(100, cell.resource_level + regeneration)
        
    def _find_adjacent_lake(self, cell: Cell) -> Optional[Cell]:
        """Find an adjacent lake cell if one exists"""
        if not hasattr(cell, 'position'):
            return None
            
        x, y = cell.position
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            # Need to access grid through environment - this needs to be passed in
            if (0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]) and 
                self.grid[nx][ny].cell_type == CellType.LAKE):
                return self.grid[nx][ny]
        return None

    def transfer_resources(self, source: Cell, target: Cell, amount: float):
        """
        Transfers resources between cells safely.
        
        Perfect example of why we use a Manager:
        1. Atomic Operations: Updates both cells in one transaction
        2. Resource Conservation: Ensures resources aren't created/lost
        3. Validation: Checks transfer amounts centrally
        4. Tracking: Returns actual transfer amount for verification
        
        If this was in Cell class:
            source_cell.transfer_to(target_cell, amount)
        It would be harder to:
        - Ensure atomicity
        - Prevent cells from creating resources
        - Track transfers system-wide
        - Maintain consistent transfer rules
        
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
        3. Considering cell type specific factors
        4. Averaging these factors for final quality score
        5. Clamping result between 0-1
        
        Design choices:
        - Cell type weighting (forests and lakes provide better quality)
        - Uses weighted average for more realistic modeling
        - Bounded output ensures consistent range for consumers
        
        Returns:
            float: Resource quality score between 0.0 (worst) and 1.0 (best)
        """
        pollution_impact = cell.current_pollution_level / 100
        health_factor = cell.health_level / 100
        
        # Cell type specific quality bonuses
        type_bonus = {
            CellType.FOREST: 0.2,  # Forests provide better quality resources
            CellType.LAKE: 0.15,   # Lakes provide clean water
            CellType.LAND: 0.1,    # Natural land has some quality
            CellType.CITY: 0.0     # Cities have no natural quality bonus
        }.get(cell.cell_type, 0.0)
        
        # Weighted average of factors
        quality = (
            (health_factor * 0.4) +           # Health is important
            ((1 - pollution_impact) * 0.4) +  # Pollution has major impact
            (type_bonus * 0.2)                # Cell type provides bonus
        )
        
        return max(0, min(1, quality))
