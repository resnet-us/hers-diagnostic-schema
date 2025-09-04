from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from koozie import convert  # type: ignore


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


@dataclass
class NMEULComponents:
    name: str
    units: str | None
    values: List[float]


INDEX_TOLERANCE = 0.005


# Fossil fuel co2e coefficients
# TODO: biomass is not included, and will need to be added in a future version
fuel_emission_factors: Dict[FuelType, float] = {
    FuelType.NATURAL_GAS: convert(147.3, "lb/MBtu", "lb/kBtu"),
    FuelType.FUEL_OIL_2: convert(195.9, "lb/MBtu", "lb/kBtu"),
    FuelType.LIQUID_PETROLEUM_GAS: convert(177.8, "lb/MBtu", "lb/kBtu"),
    FuelType.BIOMASS: convert(0.0, "lb/MBtu", "lb/kBtu"),  # TODO: Need to update biomass fuel emission factor
}


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
