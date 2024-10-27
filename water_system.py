from typing import List, Set, Tuple
from cell import Cell, CellType

class WaterSystem:
    """Manages water flow and pollution spread between connected lake cells"""
    
    def __init__(self):
        self.lake_networks: List[Set[Cell]] = []
        
    def update_lake_networks(self, grid: List[List[Cell]]) -> None:
        """Find all connected lake networks using flood fill"""
        self.lake_networks = []
        visited = set()
        
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell.cell_type == CellType.LAKE and (i,j) not in visited:
                    network = self._flood_fill(grid, i, j, visited)
                    self.lake_networks.append(network)
    
    def _flood_fill(self, grid: List[List[Cell]], i: int, j: int, visited: Set[Tuple[int, int]]) -> Set[Cell]:
        """Find all connected lake cells using flood fill algorithm"""
        if not (0 <= i < len(grid) and 0 <= j < len(grid[0])):
            return set()
        
        if (i,j) in visited or grid[i][j].cell_type != CellType.LAKE:
            return set()
            
        network = {grid[i][j]}
        visited.add((i,j))
        
        # Check all adjacent cells
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            network.update(self._flood_fill(grid, i+di, j+dj, visited))
            
        return network
    
    def balance_water_levels(self) -> None:
        """Balance water levels between connected lakes"""
        for network in self.lake_networks:
            if not network:
                continue
                
            # Calculate average water level
            total_water = sum(cell.resource_level for cell in network)
            avg_water = total_water / len(network)
            
            # Set all cells to average
            for cell in network:
                cell.resource_level = avg_water
    
    def spread_water_pollution(self) -> None:
        """Spread pollution between connected lake cells"""
        for network in self.lake_networks:
            if not network:
                continue
                
            # Calculate average pollution
            total_pollution = sum(cell.ground_pollution_level for cell in network)
            avg_pollution = total_pollution / len(network)
            
            # Set all cells to average
            for cell in network:
                cell.ground_pollution_level = avg_pollution
