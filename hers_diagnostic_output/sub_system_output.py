from dataclasses import dataclass

from .definitions import FuelType


@dataclass
class SubSystemOutput:
    primary_fuel_type: FuelType
    equipment_efficiency_coefficient: float
    load: float
    energy_use: float
