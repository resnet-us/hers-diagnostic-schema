from typing import Dict

from .definitions import HomeType
from .energy_output import EnergyOutput
from .system_output import SystemOutput


class HomeOutputs:
    def __init__(self, home_output: Dict, home_type: HomeType):
        self.conditioned_space_temperature = home_output["conditioned_space_temperature"]
        self.space_heating_system_output: SystemOutput = SystemOutput(home_output["space_heating_system_output"], home_type)
        self.space_cooling_system_output: SystemOutput = SystemOutput(home_output["space_cooling_system_output"], home_type)
        self.water_heating_system_output: SystemOutput = SystemOutput(home_output["water_heating_system_output"], home_type)
        self.lighting_and_appliance_energy: EnergyOutput = EnergyOutput(home_output["lighting_and_appliance_energy"])
        self.ventilation_energy: EnergyOutput = EnergyOutput(home_output["ventilation_energy"])
        self.dehumidification_energy: EnergyOutput = EnergyOutput(home_output["dehumidification_energy"])
