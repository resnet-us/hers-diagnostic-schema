from dataclasses import dataclass
from typing import List

from .definitions import FuelType


@dataclass
class SubEnergyOutput:
    fuel_type: FuelType
    energy: List[float]
