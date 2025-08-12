from typing import Dict, List, Optional

from .definitions import FuelType, HomeType, blank_energy_output, fuel_emission_factors
from .energy_output import EnergyOutput
from .functions import product_lists
from .system_output import SystemOutput


class HomeOutputs:
    def __init__(self, home_output: Dict, home_type: HomeType, electricity_co2_emissions_factors: Optional[List[float]] = None):
        self.conditioned_space_temperature = home_output["conditioned_space_temperature"]
        self.space_heating_system_output: SystemOutput = SystemOutput(home_output["space_heating_system_output"], home_type)
        self.space_cooling_system_output: SystemOutput = SystemOutput(home_output["space_cooling_system_output"], home_type)
        self.water_heating_system_output: SystemOutput = SystemOutput(home_output["water_heating_system_output"], home_type)
        self.lighting_and_appliance_energy: EnergyOutput = EnergyOutput(home_output["lighting_and_appliance_energy"])
        self.ventilation_energy: EnergyOutput = EnergyOutput(home_output["ventilation_energy"])

        dehumidification_energy = home_output.get("dehumidifaction_energy")

        if dehumidification_energy:
            self.dehumidification_energy: EnergyOutput = EnergyOutput(dehumidification_energy)
        else:
            self.dehumidification_energy: EnergyOutput = EnergyOutput(blank_energy_output)

        self.emissions_annual_total: float = 0

        def get_annual_emissions(fuel_type: FuelType, energy_hourly: List[float]) -> float:
            if fuel_type == FuelType.ELECTRICITY:
                return sum(product_lists(energy_hourly, electricity_co2_emissions_factors))  # type: ignore
            elif fuel_type == FuelType.FOSSIL_FUEL:
                return 0
            else:
                return sum(energy_hourly) * fuel_emission_factors[fuel_type]

        if electricity_co2_emissions_factors:
            for system_output in [self.space_heating_system_output, self.space_cooling_system_output, self.water_heating_system_output]:
                for fuel_type, energy_hourly in system_output.energy_hourly_fuel_type.items():
                    self.emissions_annual_total += get_annual_emissions(fuel_type, energy_hourly)
            for energy_output in [self.lighting_and_appliance_energy, self.ventilation_energy, self.dehumidification_energy]:
                for fuel_type, energy_hourly in energy_output.energy_hourly_fuel_type.items():
                    self.emissions_annual_total += get_annual_emissions(fuel_type, energy_hourly)
