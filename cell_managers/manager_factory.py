from typing import Dict, Type
from cell import CellType
from config_model import ConfigModel
from .base_manager import BaseCellManager
from .city_manager import CityManager
from .forest_manager import ForestManager
from .lake_manager import LakeManager
from .land_manager import LandManager

class CellManagerFactory:
    """Factory for creating appropriate cell managers"""
    
    _managers: Dict[CellType, Type[BaseCellManager]] = {
        CellType.CITY: CityManager,
        CellType.FOREST: ForestManager,
        CellType.LAKE: LakeManager,
        CellType.LAND: LandManager
    }
    
    @classmethod
    def get_manager(cls, cell_type: CellType, config: ConfigModel) -> BaseCellManager:
        """Get appropriate manager for cell type"""
        manager_class = cls._managers.get(cell_type, BaseCellManager)
        return manager_class(config)
