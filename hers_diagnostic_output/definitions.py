from enum import Enum
from typing import Dict, List


class HomeType(Enum):
    RATED_HOME = "rated_home"
    HERS_REFERENCE_HOME = "hers_reference_home"
    CO2_REFERENCE_HOME = "co2_reference_home"
    IAD_RATED_HOME = "iad_rated_home"
    IAD_HERS_REFERENCE_HOME = "iad_hers_reference_home"


class FuelType(Enum):
    ELECTRICITY = "Electricity"
    NATURAL_GAS = "Natural Gas"
    FUEL_OIL_2 = "Fuel Oil #2"
    LIQUID_PETROLEUM_GAS = "Liquid Petroleum Gas"
    BIOMASS = "Biomass"
    FOSSIL_FUEL = "Fossil Fuel"


fossil_fuel_types: List[FuelType] = [
    FuelType.NATURAL_GAS,
    FuelType.FUEL_OIL_2,
    FuelType.LIQUID_PETROLEUM_GAS,
]

fuel_coefficients: Dict[tuple[str, FuelType], Dict[str, float]] = {
    ("space_heating_system_output", FuelType.ELECTRICITY): {"a": 2.2561, "b": 0.0},
    ("space_heating_system_output", FuelType.FOSSIL_FUEL): {
        "a": 1.0943,
        "b": 0.403,
    },
    ("space_heating_system_output", FuelType.BIOMASS): {"a": 0.885, "b": 0.4047},
    ("space_cooling_system_output", FuelType.ELECTRICITY): {"a": 3.809, "b": 0.0},
    ("water_heating_system_output", FuelType.ELECTRICITY): {"a": 0.92, "b": 0.0},
    ("water_heating_system_output", FuelType.FOSSIL_FUEL): {
        "a": 1.1877,
        "b": 1.013,
    },
}
