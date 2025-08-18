from pathlib import Path
from typing import Dict, List, Optional

from koozie import convert
from lattice import load  # type: ignore

from .definitions import HomeType, INDEX_TOLERANCE
from .functions import product_lists
from .hers_cache import HERSCache
from .home_outputs import HomeOutputs


class HERSDiagnosticOutput:
    def __init__(self, file_path: str | Path):
        def get_annual_emissions(annual_emissions: Optional[List[float]], emissions_factors: List[float]) -> float:
            """Calculate total annual CO2 emissions."""
            if annual_emissions:
                return sum(product_lists(annual_emissions, emissions_factors))
            return 0.0

        def get_annual_energy(annual_energy: Optional[List[float]]) -> float:
            """Calculate total annual energy."""
            if annual_energy:
                return sum(annual_energy)
            return 0.0

        def get_hourly_energy(hourly_energy: Optional[List[float]]) -> List[float]:
            """Return hourly energy list, or 8760 zeros if missing."""
            if hourly_energy:
                return hourly_energy
            return [0.0] * 8760

        self.data = load(file_path)

        self.project_name: str = self.data["project_name"]
        self.software_name: str = self.data["software_name"]
        self.software_version: str = self.data["software_version"]
        self.conditioned_floor_area: float = self.data["conditioned_floor_area"]
        self.number_of_bedrooms: float = self.data["number_of_bedrooms"]
        self.number_of_stories: float = self.data["number_of_stories"]
        self.hers_index_software: float = self.data["hers_index"]
        self.carbon_index_software: float = self.data["carbon_index"]

        self.electricity_co2_emissions_factors: List[float] = convert(
            self.data["electricity_co2_emissions_factors"],
            "lb/kWh",
            "lb/kBtu",
        )

        self.outdoor_drybulb_temperature: List[float] = self.data["outdoor_drybulb_temperature"]

        self.on_site_power_production_annual_emissions = get_annual_emissions(
            self.data.get("on_site_power_production"), self.data["electricity_co2_emissions_factors"]
        )
        self.on_site_power_production_annual = get_annual_energy(self.data.get("on_site_power_production"))
        self.on_site_power_production_hourly = get_hourly_energy(self.data.get("on_site_power_production"))

        self.battery_storage_annual_emissions = get_annual_emissions(self.data.get("battery_storage"), self.data["electricity_co2_emissions_factors"])
        self.battery_storage_annual = get_annual_energy(self.data.get("battery_storage"))
        self.battery_storage_hourly = get_hourly_energy(self.data.get("battery_storage"))

        self.hers_reference_home_output: HomeOutputs = HomeOutputs(self.data["hers_reference_home_output"], home_type=HomeType.HERS_REFERENCE_HOME)
        self.co2_reference_home_output: HomeOutputs = HomeOutputs(
            self.data["co2_reference_home_output"],
            home_type=HomeType.CO2_REFERENCE_HOME,
            hers_diagnostic_output=self,
        )
        self.iad_hers_reference_home_output: HomeOutputs = HomeOutputs(
            self.data["iad_hers_reference_home_output"], home_type=HomeType.IAD_HERS_REFERENCE_HOME
        )
        self.rated_home_output: HomeOutputs = HomeOutputs(
            self.data["rated_home_output"],
            home_type=HomeType.RATED_HOME,
            hers_diagnostic_output=self,
        )

        self.iad_rated_home_output: HomeOutputs = HomeOutputs(
            self.data["iad_rated_home_output"], home_type=HomeType.IAD_RATED_HOME, hers_diagnostic_output=self
        )

        self.hers_cache = HERSCache(self)

    def calculate_hers_index(self) -> float:
        return self.hers_cache.hers_index

    def calculate_carbon_index(self) -> float:
        return self.hers_cache.co2_index

    def check_index_mismatch(self, index_name: str, calculated_index: float, output_index: float):
        difference_ratio = (calculated_index - output_index) / output_index
        if abs(difference_ratio) >= INDEX_TOLERANCE:
            raise RuntimeError(
                f"""\n{self.project_name} {index_name} outside tolerance.\nCalculated Index: {calculated_index:.2f}\nOutput Index: {output_index:.2f}\nPercent Difference: {difference_ratio:.2%}"""
            )
        else:
            print(f"""{self.project_name} {index_name} within tolerance.""")

    def verify_hers_index(self):
        self.check_index_mismatch("HERS Index", self.hers_cache.hers_index, self.data["hers_index"])

    def verify_carbon_index(self):
        self.check_index_mismatch("CO2 Index", self.hers_cache.co2_index, self.data["carbon_index"])

    def verify(self):
        self.verify_hers_index()
        self.verify_carbon_index()

    def get_hers_index_intermediaries(self) -> Dict:
        return {
            "hers_index": self.hers_cache.hers_index,
            "co2_index": self.hers_cache.co2_index,
            "iaf_rh": self.hers_cache.iaf_rh,
            "aco2 [lbs]": self.hers_cache.aco2,
            "arco2 [lbs]": self.hers_cache.arco2,
            "pe_frac": self.hers_cache.pe_frac,
            "tnml [MBtu]": self.hers_cache.tnml,
            "trl [MBtu]": self.hers_cache.trl,
            "teu [kWh]": self.hers_cache.teu,
            "opp [kWh]": self.hers_cache.opp,
            "bsl [kWh]": self.hers_cache.bsl,
            "iad_save": self.hers_cache.iad_save,
            "iaf_cfa": self.hers_cache.iaf_cfa,
            "iaf_nbr": self.hers_cache.iaf_nbr,
            "iaf_ns": self.hers_cache.iaf_ns,
            "tnml_iad [MBtu]": self.hers_cache.tnml_iad,
            "trl_iad [MBtu]": self.hers_cache.trl_iad,
            "nmeul_heat [MBtu]": self.hers_cache.nmeul_heat,
            "nmeul_cool [MBtu]": self.hers_cache.nmeul_cool,
            "nmeul_hw [MBtu]": self.hers_cache.nmeul_hw,
            "ec_la [MBtu]": self.hers_cache.ec_la,
            "ec_vent [MBtu]": self.hers_cache.ec_vent,
            "ec_dh [MBtu]": self.hers_cache.ec_dh,
            "nmeul_heat_iad [MBtu]": self.hers_cache.nmeul_heat_iad,
            "nmeul_cool_iad [MBtu]": self.hers_cache.nmeul_cool_iad,
            "nmeul_hw_iad [MBtu]": self.hers_cache.nmeul_hw_iad,
            "ec_la_iad [MBtu]": self.hers_cache.ec_la_iad,
            "ec_vent_iad [MBtu]": self.hers_cache.ec_vent_iad,
            "ec_dh_iad [MBtu]": self.hers_cache.ec_dh_iad,
            "reul_heat [MBtu]": self.hers_cache.reul_heat,
            "reul_cool [MBtu]": self.hers_cache.reul_cool,
            "reul_hw [MBtu]": self.hers_cache.reul_hw,
            "rec_la [MBtu]": self.hers_cache.rec_la,
            "rec_vent [MBtu]": self.hers_cache.rec_vent,
            "rec_dh [MBtu]": self.hers_cache.rec_dh,
            "reul_heat_iad [MBtu]": self.hers_cache.reul_heat_iad,
            "reul_cool_iad [MBtu]": self.hers_cache.reul_cool_iad,
            "reul_hw_iad [MBtu]": self.hers_cache.reul_hw_iad,
            "rec_la_iad [MBtu]": self.hers_cache.rec_la_iad,
            "rec_vent_iad [MBtu]": self.hers_cache.rec_vent_iad,
            "rec_dh_iad [MBtu]": self.hers_cache.rec_dh_iad,
        }
