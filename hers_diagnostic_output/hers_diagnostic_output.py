from pathlib import Path
from typing import Dict, List, Optional

from lattice import load

from .definitions import FuelType, HomeType, fossil_fuel_types, fuel_coefficients
from .hers_cache import HERSCache
from .home_outputs import HomeOutputs
from .system_output import SystemOutput


class HERSDiagnosticOutput:
    def __init__(self, file_path: str | Path):
        self.data = load(file_path)

        self.software_name: str = self.data["software_name"]
        self.software_version: str = self.data["software_version"]
        self.conditioned_floor_area: float = self.data["conditioned_floor_area"]
        self.number_of_bedrooms: float = self.data["number_of_bedrooms"]
        self.number_of_stories: float = self.data["number_of_stories"]
        self.hers_index_software: float = self.data["hers_index"]
        self.carbon_index_software: float = self.data["carbon_index"]

        self.electricity_co2_emissions_factors: List[float] = self.data["electricity_co2_emissions_factors"]
        self.outdoor_drybulb_temperature: List[float] = self.data["outdoor_drybulb_temperature"]
        self.on_site_power_production: List[float] = self.data["on_site_power_production"]
        self.on_site_power_production_annual: float = sum(self.on_site_power_production)
        battery_storage: Optional[List[float]] = self.data.get("battery_storage")

        if battery_storage:
            self.battery_storage: List[float] = self.data["battery_storage"]
            self.battery_storage_annual: float = sum(self.battery_storage)
        else:
            self.battery_storage: List[float] = [0] * 8760  # type: ignore
            self.battery_storage_annual: float = 0  # type: ignore

        self.rated_home_output: HomeOutputs = HomeOutputs(self.data["rated_home_output"], home_type=HomeType.RATED_HOME)
        self.hers_reference_home_output: HomeOutputs = HomeOutputs(self.data["hers_reference_home_output"], home_type=HomeType.HERS_REFERENCE_HOME)
        self.co2_reference_home_output: HomeOutputs = HomeOutputs(self.data["co2_reference_home_output"], home_type=HomeType.CO2_REFERENCE_HOME)
        self.iad_rated_home_output: HomeOutputs = HomeOutputs(self.data["iad_rated_home_output"], home_type=HomeType.IAD_RATED_HOME)
        self.iad_hers_reference_home_output: HomeOutputs = HomeOutputs(
            self.data["iad_hers_reference_home_output"], home_type=HomeType.IAD_HERS_REFERENCE_HOME
        )

        system_types = [
            "space_heating_system_output",
            "space_cooling_system_output",
            "water_heating_system_output",
        ]

        for rated_home_output, hers_reference_home_output in zip(
            [self.rated_home_output, self.iad_rated_home_output], [self.hers_reference_home_output, self.iad_hers_reference_home_output]
        ):
            for system_type in system_types:
                rated_home_system_type: SystemOutput = getattr(rated_home_output, system_type)
                reference_home_system_type: SystemOutput = getattr(hers_reference_home_output, system_type)

                for rated_home_sub_system, reference_home_sub_system in zip(
                    rated_home_system_type.sub_system_outputs, reference_home_system_type.sub_system_outputs
                ):
                    ec_x = rated_home_sub_system.energy_use
                    eec_x = rated_home_sub_system.equipment_efficiency_coefficient
                    eec_r = reference_home_sub_system.equipment_efficiency_coefficient
                    primary_fuel_type = rated_home_sub_system.primary_fuel_type
                    if primary_fuel_type in fossil_fuel_types:
                        primary_fuel_type = FuelType.FOSSIL_FUEL
                    a = fuel_coefficients[(system_type, primary_fuel_type)]["a"]
                    b = fuel_coefficients[(system_type, primary_fuel_type)]["b"]

                    ec_r = reference_home_sub_system.energy_use
                    nec_x = ec_x * (a * eec_x - b) * (eec_r / eec_x)
                    reul = reference_home_sub_system.load

                    rated_home_system_type.nmeul += reul * nec_x / ec_r

        self.hers_cache = HERSCache(self)

    def calculate_hers_index(self) -> float:
        return self.hers_cache.hers_index

    def calculate_carbon_index(self) -> float:
        return self.hers_cache.co2_index

    def get_hers_index_intermediaries(self) -> Dict:
        return {
            "hers_index": self.hers_cache.hers_index,
            "iaf_rh": self.hers_cache.iaf_rh,
            "pe_frac": self.hers_cache.pe_frac,
            "tnml": self.hers_cache.tnml,
            "trl": self.hers_cache.trl,
            "teu": self.hers_cache.teu,
            "opp": self.hers_cache.opp,
            "bsl": self.hers_cache.bsl,
            "iad_save": self.hers_cache.iad_save,
            "iaf_cfa": self.hers_cache.iaf_cfa,
            "iaf_nbr": self.hers_cache.iaf_nbr,
            "iaf_ns": self.hers_cache.iaf_ns,
            "tnml_iad": self.hers_cache.tnml_iad,
            "trl_iad": self.hers_cache.trl_iad,
            "nmeul_heat": self.hers_cache.nmeul_heat,
            "nmeul_cool": self.hers_cache.nmeul_cool,
            "nmeul_hw": self.hers_cache.nmeul_hw,
            "ec_la": self.hers_cache.ec_la,
            "ec_vent": self.hers_cache.ec_vent,
            "ec_dh": self.hers_cache.ec_dh,
            "nmeul_heat_iad": self.hers_cache.nmeul_heat_iad,
            "nmeul_cool_iad": self.hers_cache.nmeul_cool_iad,
            "nmeul_hw_iad": self.hers_cache.nmeul_hw_iad,
            "ec_la_iad": self.hers_cache.ec_la_iad,
            "ec_vent_iad": self.hers_cache.ec_vent_iad,
            "ec_dh_iad": self.hers_cache.ec_dh_iad,
            "reul_heat": self.hers_cache.reul_heat,
            "reul_cool": self.hers_cache.reul_cool,
            "reul_hw": self.hers_cache.reul_hw,
            "rec_la": self.hers_cache.rec_la,
            "rec_vent": self.hers_cache.rec_vent,
            "rec_dh": self.hers_cache.rec_dh,
            "reul_heat_iad": self.hers_cache.reul_heat_iad,
            "reul_cool_iad": self.hers_cache.reul_cool_iad,
            "reul_hw_iad": self.hers_cache.reul_hw_iad,
            "rec_la_iad": self.hers_cache.rec_la_iad,
            "rec_vent_iad": self.hers_cache.rec_vent_iad,
            "rec_dh_iad": self.hers_cache.rec_dh_iad,
        }
