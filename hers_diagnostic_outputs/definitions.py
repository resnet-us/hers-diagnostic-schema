from enum import Enum
from typing import List


class HomeType(Enum):
    RATED_HOME = "rated_home"
    HERS_REFERENCE_HOME = "hers_reference_home"
    CO2_REFERENCE_HOME = "co2_reference_home"
    IAD_RATED_HOME = "iad_rated_home"
    IAD_HERS_REFERENCE_HOME = "iad_hers_reference_home"


class FuelType(Enum):
    ELECTRICITY = "ELECTRICITY"
    NATURAL_GAS = "NATURAL_GAS"
    FUEL_OIL_2 = "FUEL OIL #2"
    LIQUID_PETROLEUM_GAS = "LIQUID PETROLEUM GAS"
    BIOMASS = "BIOMASS"


fossil_fuel_types: List[FuelType] = [
    FuelType.NATURAL_GAS,
    FuelType.FUEL_OIL_2,
    FuelType.LIQUID_PETROLEUM_GAS,
]
