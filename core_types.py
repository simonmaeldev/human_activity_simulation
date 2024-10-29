"""
Core types and interfaces for the simulation.

This module defines the fundamental types used throughout the simulation,
helping to avoid circular dependencies and provide a clear contract for
how different components should interact.

Design Pattern: Abstract Base Classes + Type Hints
Benefits:
- Prevents circular imports by providing base types
- Clearly defines interfaces that components must implement
- Makes the codebase easier to understand and maintain
- Enables better type checking and IDE support
"""

from enum import IntEnum
from typing import TypeVar, List, Dict, Tuple, Optional
from pydantic import BaseModel, Field
import simpy

class AgentPriority(IntEnum):
    """Priority levels for resource distribution"""
    HIGHEST = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    LOWEST = 5

class Resource(BaseModel):
    """Represents a consumable resource in the simulation"""
    name: str
    quantity: float
    quality: float = Field(ge=0.0, le=1.0)

class BaseCell(BaseModel):
    """
    Abstract base class defining the cell interface.
    All cell types must inherit from this.
    """
    env: simpy.Environment
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    air_pollution: float = Field(default=0.0)
    ground_pollution: float = Field(default=0.0)
    max_resources: float = Field(default=0.0)
    current_resources: float = Field(default=0.0)
    regeneration_rate: float = Field(default=0.0)

    class Config:
        arbitrary_types_allowed = True

class BaseAgent(BaseModel):
    """
    Abstract base class defining the agent interface.
    All agent types must inherit from this.
    """
    env: simpy.Environment
    health: float = Field(default=1.0, ge=0.0, le=1.0)
    population: int = Field(default=1)
    priority: AgentPriority = Field(default=AgentPriority.MEDIUM)
    position: Tuple[int, int] = Field(...)

    class Config:
        arbitrary_types_allowed = True

# Type variables for type hinting
CellType = TypeVar('CellType', bound=BaseCell)
AgentType = TypeVar('AgentType', bound=BaseAgent)
