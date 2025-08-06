from pathlib import Path
from typing import List

from lattice import load

from .definitions import HomeType
from .hers_cache import HERSCache
from .home_outputs import HomeOutputs


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
        battery_storage = self.data.get("battery_storage")

        if battery_storage:
            self.battery_storage: List[float] = self.data["battery_storage"]
            self.battery_storage_annual: float = sum(self.battery_storage)
        else:
            self.battery_storage: List[float] = [0] * 8760
            self.battery_storage_annual: float = 0

        self.rated_home_output: HomeOutputs = HomeOutputs(self.data["rated_home_output"], home_type=HomeType.RATED_HOME)
        self.hers_reference_home_output: HomeOutputs = HomeOutputs(self.data["hers_reference_home_output"], home_type=HomeType.HERS_REFERENCE_HOME)
        self.co2_reference_home_output: HomeOutputs = HomeOutputs(self.data["co2_reference_home_output"], home_type=HomeType.CO2_REFERENCE_HOME)
        self.iad_rated_home_output: HomeOutputs = HomeOutputs(self.data["iad_rated_home_output"], home_type=HomeType.IAD_RATED_HOME)
        self.iad_hers_reference_home_output: HomeOutputs = HomeOutputs(
            self.data["iad_hers_reference_home_output"], home_type=HomeType.IAD_HERS_REFERENCE_HOME
        )

        self.hers_cache = HERSCache(self)

    def calculate_hers_index(self) -> float:
        return self.hers_cache.hers_index

    def calculate_carbon_index(self) -> float:
        return self.hers_cache.co2_index
