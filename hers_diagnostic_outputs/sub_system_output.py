from dataclasses import dataclass
from typing import List, Optional

from .definitions import FuelType
from .energy_output import EnergyOutput


@dataclass
class SubSystemOutput:
    primary_fuel_type: FuelType
    equipment_efficiency_coefficient: float
    load: Optional[List[float]]
    energy_use: EnergyOutput
