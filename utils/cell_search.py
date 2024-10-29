from typing import List, Tuple, Set, Dict, Optional
from collections import defaultdict
import numpy as np

class CellSearch:
    def __init__(self, grid_width: int, grid_height: int):
        self.width = grid_width
        self.height = grid_height
        # Cache format: {(from_x, from_y): {distance: set((to_x, to_y))}}
        self._distance_cache: Dict[Tuple[int, int], Dict[int, Set[Tuple[int, int]]]] = {}
        self._build_distance_cache()

    def _build_distance_cache(self):
        """Pre-compute Manhattan distances between all cells"""
        for x in range(self.width):
            for y in range(self.height):
                distances = defaultdict(set)
                # Using numpy for efficient coordinate calculations
                y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
                manhattan_distances = np.abs(x_coords - x) + np.abs(y_coords - y)
                
                # Group coordinates by their distances
                for dist in range(manhattan_distances.max() + 1):
                    coords = np.where(manhattan_distances == dist)
                    distances[dist] = set(zip(coords[1], coords[0]))  # (x,y) format
                
                self._distance_cache[(x, y)] = distances

    def get_cells_at_distance(self, from_pos: Tuple[int, int], 
                            distance: int) -> Set[Tuple[int, int]]:
        """Get all cell coordinates exactly at specified Manhattan distance"""
        return self._distance_cache[from_pos][distance]

    def get_cells_in_range(self, from_pos: Tuple[int, int], 
                          min_distance: int = 0,
                          max_distance: int = None) -> Set[Tuple[int, int]]:
        """
        Get all cell coordinates within specified Manhattan distance range.
        Args:
            from_pos: Starting position (x,y)
            min_distance: Minimum distance (inclusive)
            max_distance: Maximum distance (inclusive), if None uses grid maximum
        """
        if max_distance is None:
            max_distance = self.width + self.height
            
        result = set()
        cache = self._distance_cache[from_pos]
        for dist in range(min_distance, max_distance + 1):
            if dist in cache:
                result.update(cache[dist])
        return result

class CellSearchManager:
    """Manages cell searching and filtering for the simulation"""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.searcher = CellSearch(grid_width, grid_height)
        self.grid = None

    def set_grid(self, grid):
        """Set the current grid reference"""
        self.grid = grid

    def get_valid_cells(self, from_pos: Tuple[int, int], 
                       max_distance: int,
                       filter_func) -> List[Tuple['Cell', float]]:
        """
        Get all valid cells within range, sorted by distance.
        Args:
            from_pos: Starting position (x,y)
            max_distance: Maximum search distance
            filter_func: Function(cell) -> bool to determine valid cells
        Returns:
            List of (cell, distance) tuples sorted by distance
        """
        coords = self.searcher.get_cells_in_range(from_pos, 0, max_distance)
        results = []
        
        for x, y in coords:
            cell = self.grid[x][y]
            if filter_func(cell):
                distance = abs(x - from_pos[0]) + abs(y - from_pos[1])
                results.append((cell, distance))
                
        return sorted(results, key=lambda x: x[1])
