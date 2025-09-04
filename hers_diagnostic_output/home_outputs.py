from typing import Dict, List, Optional, TYPE_CHECKING

from koozie import convert

from .definitions import FuelType, HomeType, fossil_fuel_types, fuel_coefficients, fuel_emission_factors
from .energy_output import EnergyOutput
from .functions import product_lists
from .system_output import SystemOutput

if TYPE_CHECKING:
    from .hers_diagnostic_output import HERSDiagnosticOutput


class HomeOutputs:
    def __init__(
        self,
        home_output: Dict,
        home_type: HomeType,
        hers_diagnostic_output: Optional["HERSDiagnosticOutput"] = None,
    ):
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
            self.dehumidification_energy: EnergyOutput = EnergyOutput()  # type: ignore

        def get_annual_emissions(fuel_type: FuelType, energy_hourly: List[float]) -> float:
            if fuel_type == FuelType.ELECTRICITY:
                return sum(product_lists(energy_hourly, hers_diagnostic_output.electricity_co2_emissions_factors))  # type: ignore
            elif fuel_type == FuelType.FOSSIL_FUEL:
                return 0
            else:
                return sum(energy_hourly) * fuel_emission_factors[fuel_type]

        def get_rated_home_system_types() -> List[SystemOutput]:
            return [
                self.space_heating_system_output,
                self.space_cooling_system_output,
                self.water_heating_system_output,
            ]

        def get_system_types() -> List[str]:
            return [
                "space_heating_system_output",
                "space_cooling_system_output",
                "water_heating_system_output",
            ]

        if hers_diagnostic_output:
            if home_type == HomeType.RATED_HOME or home_type == HomeType.CO2_REFERENCE_HOME:
                self.emissions_annual_total: float = 0
                for system_output in [self.space_heating_system_output, self.space_cooling_system_output, self.water_heating_system_output]:
                    for fuel_type, energy_hourly in system_output.energy_hourly_fuel_type.items():
                        self.emissions_annual_total += get_annual_emissions(fuel_type, energy_hourly)
                for energy_output in [self.lighting_and_appliance_energy, self.ventilation_energy, self.dehumidification_energy]:
                    for fuel_type, energy_hourly in energy_output.energy_hourly_fuel_type.items():
                        self.emissions_annual_total += get_annual_emissions(fuel_type, energy_hourly)

        rated_home_system_types: List[SystemOutput] = []
        reference_home_system_types: List[SystemOutput] = []
        system_types: List[str] = []
        if hers_diagnostic_output:
            if home_type == HomeType.RATED_HOME:
                rated_home_system_types = get_rated_home_system_types()
                reference_home_system_types = [
                    hers_diagnostic_output.hers_reference_home_output.space_heating_system_output,
                    hers_diagnostic_output.hers_reference_home_output.space_cooling_system_output,
                    hers_diagnostic_output.hers_reference_home_output.water_heating_system_output,
                ]
                system_types = get_system_types()

            elif home_type == HomeType.IAD_RATED_HOME:
                rated_home_system_types = get_rated_home_system_types()
                reference_home_system_types = [
                    hers_diagnostic_output.iad_hers_reference_home_output.space_heating_system_output,
                    hers_diagnostic_output.iad_hers_reference_home_output.space_cooling_system_output,
                    hers_diagnostic_output.iad_hers_reference_home_output.water_heating_system_output,
                ]
                system_types = get_system_types()

        for rated_home_system_type, reference_home_system_type, system_type in zip(
            rated_home_system_types, reference_home_system_types, system_types
        ):
            for rated_home_sub_system, reference_home_sub_system in zip(
                rated_home_system_type.sub_system_outputs, reference_home_system_type.sub_system_outputs
            ):
                ec_x = convert(rated_home_sub_system.energy_use, "kBtu", "MBtu")
                eec_x = rated_home_sub_system.equipment_efficiency_coefficient
                eec_r = reference_home_sub_system.equipment_efficiency_coefficient
                primary_fuel_type = rated_home_sub_system.primary_fuel_type
                if primary_fuel_type in fossil_fuel_types:
                    primary_fuel_type = FuelType.FOSSIL_FUEL
                a = fuel_coefficients[(system_type, primary_fuel_type)]["a"]
                b = fuel_coefficients[(system_type, primary_fuel_type)]["b"]

                ec_r = convert(reference_home_sub_system.energy_use, "kBtu", "MBtu")
                nec_x = ec_x * (a * eec_x - b) * (eec_r / eec_x)
                reul = convert(reference_home_sub_system.load, "kBtu", "MBtu")
                nmeul = reul * nec_x / ec_r

                rated_home_system_type.nmeul += nmeul

                rated_home_system_type.ec_x_list.append(ec_x)
                rated_home_system_type.eec_x_list.append(eec_x)
                rated_home_system_type.eec_r_list.append(eec_r)
                rated_home_system_type.a_list.append(a)
                rated_home_system_type.b_list.append(b)
                rated_home_system_type.ec_r_list.append(ec_r)
                rated_home_system_type.nec_x_list.append(nec_x)
                rated_home_system_type.reul_list.append(reul)
                rated_home_system_type.nmeul_list.append(nmeul)
