from typing import Dict, List

from .definitions import FuelType
from .functions import to_upper_case, get_annual_data, get_fuel_conversion, sum_lists
from .sub_energy_output import SubEnergyOutput


class EnergyOutput:
    def __init__(self, energy_output: Dict):
        self.sub_energy_outputs: List[SubEnergyOutput] = []

        self.energy_electricity_use_equivalent: float = 0.0

        # EnergyOutput in HERSDiagnosticOutput files are reported in kBtu
        self.energy_annual_fuel_type_cache: Dict[FuelType, float] = {fuel_type: 0.0 for fuel_type in FuelType}
        self.energy_hourly_fuel_type_cache: Dict[FuelType, List[float]] = {fuel_type: [0.0] * 8760 for fuel_type in FuelType}

        for sub_energy_output in energy_output:
            fuel_type: FuelType = FuelType(to_upper_case(sub_energy_output["fuel_type"]))
            energy: List[float] = sub_energy_output["energy"]

            annual_energy = get_annual_data(energy)
            self.energy_annual_fuel_type_cache[fuel_type] += annual_energy
            self.energy_electricity_use_equivalent += annual_energy * get_fuel_conversion(fuel_type)

            # Update energy_hourly_fuel_type_cache[fuel_type] in place.
            self.energy_hourly_fuel_type_cache[fuel_type] = sum_lists(self.energy_hourly_fuel_type_cache[fuel_type], energy)

            sub_energy_output = SubEnergyOutput(fuel_type, energy)

            self.sub_energy_outputs.append(sub_energy_output)
