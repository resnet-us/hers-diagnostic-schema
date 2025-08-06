from typing import Dict, List, Optional

from .definitions import HomeType, FuelType
from .energy_output import EnergyOutput
from .functions import get_annual_data, get_fuel_conversion, sum_lists, to_upper_case
from .sub_system_output import SubSystemOutput


class SystemOutput:
    def __init__(self, system_output: List[Dict[str, str | float | List[float] | Dict[str, str | List[float]]]], home_type):
        # self.sub_system_outputs: List[SubSystemOutput] = []
        self.load_annual_total: float = 0
        self.energy_electricity_use_equivalent: float = 0

        self.load_annual_fuel_type: Dict[FuelType, float] = {fuel_type: 0.0 for fuel_type in FuelType}
        self.energy_annual_fuel_type: Dict[FuelType, float] = {fuel_type: 0.0 for fuel_type in FuelType}
        self.load_hourly_fuel_type: Dict[FuelType, List[float]] = {fuel_type: [0.0] * 8760 for fuel_type in FuelType}
        self.energy_hourly_fuel_type: Dict[FuelType, List[float]] = {fuel_type: [0.0] * 8760 for fuel_type in FuelType}

        for sub_system_output in system_output:
            primary_fuel_type: FuelType = FuelType(to_upper_case(sub_system_output["primary_fuel_type"]))  # type: ignore
            equipment_efficiency_coefficient: float = sub_system_output["equipment_efficiency_coefficient"]  # type: ignore

            load: Optional[List[float]] = sub_system_output.get("load")  # type: ignore

            if load:
                annual_load = get_annual_data(load)
                self.load_annual_total += annual_load
                self.load_annual_fuel_type[primary_fuel_type] += annual_load
                self.load_hourly_fuel_type[primary_fuel_type] = sum_lists(self.load_hourly_fuel_type[primary_fuel_type], load)

            energy_use: EnergyOutput = EnergyOutput(sub_system_output["energy_use"])  # type: ignore

            for (fuel_type, energy_annual_fuel_type), (fuel_type, energy_hourly_fuel_type) in zip(
                energy_use.energy_annual_fuel_type_cache.items(), energy_use.energy_hourly_fuel_type_cache.items()
            ):
                self.energy_annual_fuel_type[fuel_type] += energy_annual_fuel_type
                self.energy_hourly_fuel_type[fuel_type] = sum_lists(self.energy_hourly_fuel_type[fuel_type], energy_hourly_fuel_type)
                self.energy_electricity_use_equivalent += energy_annual_fuel_type * get_fuel_conversion(fuel_type)

            # sub_system_output = SubSystemOutput(
            #     primary_fuel_type,
            #     equipment_efficiency_coefficient,
            #     load,
            #     energy_use,
            # )

            # self.sub_system_outputs.append(sub_system_output)
