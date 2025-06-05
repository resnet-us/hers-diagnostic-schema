"""Package calculating HERS Index."""

from enum import Enum
from typing import Dict, List

from koozie import convert  # type: ignore
import lattice  # type: ignore


def element_add(list1, list2):
    number_of_elements = len(list1)
    list3 = [0] * number_of_elements
    for i in range(number_of_elements):
        list3[i] = list1[i] + list2[i]
    return list3


def element_product(list1, list2):
    number_of_elements = len(list1)
    list3 = [0] * number_of_elements
    for i in range(number_of_elements):
        list3[i] = list1[i] * list2[i]
    return list3


class EndUseSystem:
    fuel_type: str
    end_use_type: str
    home_type: str


class HomeType(Enum):
    RATED_HOME = "rated_home"
    HERS_REFERENCE_HOME = "hers_reference_home"
    CO2_REFERENCE_HOME = "co2_reference_home"
    IAD_RATED_HOME = "iad_rated_home"
    IAD_HERS_REFERENCE_HOME = "iad_hers_reference_home"


class EndUse(Enum):
    SPACE_HEATING = "space_heating"
    SPACE_COOLING = "space_cooling"
    WATER_HEATING = "water_heating"
    LIGHTING_AND_APPLIANCE = "lighting_and_appliance"
    VENTILATION = "ventilation"
    DEHUMIDIFCATION = "dehumidification"


class FuelType(Enum):
    ELECTRICITY = "ELECTRICITY"
    BIOMASS = "BIOMASS"
    NATURAL_GAS = "NATURAL_GAS"
    FUEL_OIL_2 = "FUEL_OIL_2"
    LIQUID_PETROLEUM_GAS = "LIQUID_PETROLEUM_GAS"
    FOSSIL_FUEL = "FOSSIL_FUEL"


class HERSDiagnosticData:
    # Define coefficients 'a' and 'b based on Table 4.1.1(1) in Standard 301 for
    # space heating, space cooling, and water heating
    fuel_coefficients: Dict[tuple[EndUse, FuelType], Dict[str, float]] = {
        (EndUse.SPACE_HEATING, FuelType.ELECTRICITY): {"a": 2.2561, "b": 0.0},
        (EndUse.SPACE_HEATING, FuelType.FOSSIL_FUEL): {
            "a": 1.0943,
            "b": 0.403,
        },
        (EndUse.SPACE_HEATING, FuelType.BIOMASS): {"a": 0.885, "b": 0.4047},
        (EndUse.SPACE_COOLING, FuelType.ELECTRICITY): {"a": 3.809, "b": 0.0},
        (EndUse.WATER_HEATING, FuelType.ELECTRICITY): {"a": 0.92, "b": 0.0},
        (EndUse.WATER_HEATING, FuelType.FOSSIL_FUEL): {
            "a": 1.1877,
            "b": 1.013,
        },
    }

    co2_home_types: List[HomeType] = [HomeType.RATED_HOME, HomeType.CO2_REFERENCE_HOME]

    # Fossil fuel co2e coefficients
    # TODO: biomass is not included, and will need to be added in a future version
    fuel_emission_factors: Dict[FuelType, float] = {
        FuelType.NATURAL_GAS: convert(147.3, "lb/MBtu", "lb/kBtu"),
        FuelType.FUEL_OIL_2: convert(195.9, "lb/MBtu", "lb/kBtu"),
        FuelType.LIQUID_PETROLEUM_GAS: convert(177.8, "lb/MBtu", "lb/kBtu"),
    }

    # define FOSSIL_FUEL types to allocate proper 'a' and 'b' coefficients in fuel_coefficients dictionary
    fossil_fuel_types: List[FuelType] = [
        FuelType.NATURAL_GAS,
        FuelType.FUEL_OIL_2,
        FuelType.LIQUID_PETROLEUM_GAS,
    ]
    fuel_types: List[FuelType] = fossil_fuel_types + [FuelType.ELECTRICITY]
    system_end_uses: List[EndUse] = [
        EndUse.SPACE_HEATING,
        EndUse.SPACE_COOLING,
        EndUse.WATER_HEATING,
    ]
    other_end_uses: List[EndUse] = [
        EndUse.LIGHTING_AND_APPLIANCE,
        EndUse.VENTILATION,
        EndUse.DEHUMIDIFCATION,
    ]
    end_uses: List[EndUse] = system_end_uses + other_end_uses

    # '_system_output" and "_energy" are added to simplify code for co2e emission calculation
    end_uses_system_output: List[str] = [
        end_use.value + "_system_output" for end_use in system_end_uses
    ]
    other_end_uses_energy: List[str] = [
        other_end_use.value + "_energy" for other_end_use in other_end_uses
    ]

    INDEX_TOLERANCE = 0.005
    NUMBER_OF_TIMESTEPS = 8760

    def __init__(self, file):
        self._hers_index = -1.0
        self._co2_index = -1.0
        self._iaf_rh = -1.0
        self._aco2 = -1.0
        self._arco2 = -1.0
        self._pe_frac = -1.0
        self._tnml = -1.0
        self._trl = -1.0
        self._teu = -1.0
        self._opp = -1.0
        self._bsl = -1.0
        self._iad_save = -1.0
        self._iaf_cfa = -1.0
        self._iaf_nbr = -1.0
        self._iaf_ns = -1.0
        self._tnml_iad = -1.0
        self._trl_iad = -1.0
        self._nmeul_heat = -1.0
        self._nmeul_cool = -1.0
        self._nmeul_hw = -1.0
        self._ec_la = -1.0
        self._ec_vent = -1.0
        self._ec_dh = -1.0
        self._nmeul_heat_iad = -1.0
        self._nmeul_cool_iad = -1.0
        self._nmeul_hw_iad = -1.0
        self._ec_la_iad = -1.0
        self._ec_vent_iad = -1.0
        self._ec_dh_iad = -1.0
        self._reul_heat = -1.0
        self._reul_cool = -1.0
        self._reul_hw = -1.0
        self._rec_la = -1.0
        self._rec_vent = -1.0
        self._rec_dh = -1.0
        self._reul_heat_iad = -1.0
        self._reul_cool_iad = -1.0
        self._reul_hw_iad = -1.0
        self._rec_la_iad = -1.0
        self._rec_vent_iad = -1.0
        self._rec_dh_iad = -1.0

        self.hers_index_set = False
        self.co2_index_set = False
        self.iaf_rh_set = False
        self.aco2_set = False
        self.arco2_set = False
        self.pe_frac_set = False
        self.tnml_set = False
        self.trl_set = False
        self.teu_set = False
        self.opp_set = False
        self.bsl_set = False
        self.iad_save_set = False
        self.iaf_cfa_set = False
        self.iaf_nbr_set = False
        self.iaf_ns_set = False
        self.tnml_iad_set = False
        self.trl_iad_set = False
        self.nmeul_heat_set = False
        self.nmeul_cool_set = False
        self.nmeul_hw_set = False
        self.ec_la_set = False
        self.ec_vent_set = False
        self.ec_dh_set = False
        self.nmeul_heat_iad_set = False
        self.nmeul_cool_iad_set = False
        self.nmeul_hw_iad_set = False
        self.ec_la_iad_set = False
        self.ec_vent_iad_set = False
        self.ec_dh_iad_set = False
        self.reul_heat_set = False
        self.reul_cool_set = False
        self.reul_hw_set = False
        self.rec_la_set = False
        self.rec_vent_set = False
        self.rec_dh_set = False
        self.reul_heat_iad_set = False
        self.reul_cool_iad_set = False
        self.reul_hw_iad_set = False
        self.rec_la_iad_set = False
        self.rec_vent_iad_set = False
        self.rec_dh_iad_set = False

        # load data
        # determine number of sub-systems for each system type (ex. determine number of heating systems)
        self.data = lattice.load(file)
        self.software = self.data["software_name"]
        self.project_name = self.data["project_name"]

        self.number_of_systems: Dict[EndUse, int] = {}
        for end_use in self.system_end_uses:
            self.number_of_systems[end_use] = len(
                self.data["rated_home_output"][f"{end_use.value}_system_output"]
            )
        self.number_of_other_end_uses: Dict[EndUse, int] = {}
        for other_end_use in self.other_end_uses:
            if f"{other_end_use.value}_energy" in self.data["rated_home_output"]:
                self.number_of_other_end_uses[other_end_use] = len(
                    self.data["rated_home_output"][f"{other_end_use.value}_energy"]
                )

        # initialize energy use for each fuel type and home type to calculate co2e emissions
        # TODO: there will be several layers to the data cache
        # TODO: loop through to initialize data cache, start with loads, and then afterwards we can add other items to the cache

        self.data_cache = {}

        for home_type in self.co2_home_types:
            for energy_type in self.fuel_types:
                if energy_type == FuelType.ELECTRICITY:
                    self.data_cache[(energy_type, home_type, "hourly")] = [
                        0
                    ] * self.NUMBER_OF_TIMESTEPS
                else:
                    self.data_cache[(energy_type, home_type, "annual")] = 0

        self.emissions = {
            HomeType.RATED_HOME: 0,
            HomeType.CO2_REFERENCE_HOME: 0,
        }

        self.annual_subsystem_energy_cache = {}
        self.annual_energy_cache = {}
        self.annual_end_use_energy_cache = {}
        self.annual_fuel_type_energy_cache = {}
        self.hourly_electricity_use = {
            HomeType.RATED_HOME: [0] * self.NUMBER_OF_TIMESTEPS,
            HomeType.CO2_REFERENCE_HOME: [0] * self.NUMBER_OF_TIMESTEPS,
        }
        self.hourly_electricity_emission_factors_kwh = self.data[
            "electricity_co2_emissions_factors"
        ]
        self.hourly_electricity_emission_factors_kbtu = convert(
            self.data["electricity_co2_emissions_factors"],
            "lb/kWh",
            "lb/kBtu",
        )

    @property
    def hers_index(self):
        if self.hers_index_set:
            return self._hers_index
        else:
            self.hers_index = self.pe_frac * self.tnml / (self.trl * self.iaf_rh) * 100
            return self._hers_index

    @hers_index.setter
    def hers_index(self, hers_index):
        self._hers_index = hers_index
        self.hers_index_set = True

    @property
    def co2_index(self):
        if self.co2_index_set:
            return self._co2_index
        else:
            self.co2_index = (
                self.aco2 / (self.arco2 * self.iaf_rh) * 100
            )  # CO2 Index = ACO2 / ARCO2 * 100
            return self._co2_index

    @co2_index.setter
    def co2_index(self, co2_index):
        self._co2_index = co2_index
        self.co2_index_set = True

    @property
    def iaf_rh(self):
        if self.iaf_rh_set:
            return self._iaf_rh
        else:
            self.iaf_rh = (
                self.iaf_cfa * self.iaf_nbr * self.iaf_ns
            )  # IAF_RH = IAF_CFA * IAF_Nbr * IAF_NS
            return self._iaf_rh

    @iaf_rh.setter
    def iaf_rh(self, iaf_rh):
        self._iaf_rh = iaf_rh
        self.iaf_rh_set = True

    @property
    def aco2(self):
        if self.aco2_set:
            return self._aco2
        else:
            self.aco2 = self.get_annual_hourly_co2_emissions(HomeType.RATED_HOME)
            return self._aco2

    @aco2.setter
    def aco2(self, aco2):
        self._aco2 = aco2
        self.aco2_set = True

    @property
    def arco2(self):
        if self.arco2_set:
            return self._arco2
        else:
            self.arco2 = self.get_annual_hourly_co2_emissions(
                HomeType.CO2_REFERENCE_HOME
            )
            return self._arco2

    @arco2.setter
    def arco2(self, arco2):
        self._arco2 = arco2
        self.arco2_set = True

    @property
    def pe_frac(self):
        if self.pe_frac_set:
            return self._pe_frac
        else:
            self.pe_frac = (
                self.teu - self.opp + self.bsl
            ) / self.teu  # PEfrac = (TEU - OPP) / TEU
            return self._pe_frac

    @pe_frac.setter
    def pe_frac(self, pe_frac):
        self._pe_frac = pe_frac
        self.pe_frac_set = True

    @property
    def tnml(self):
        if self.tnml_set:
            return self._tnml
        else:
            self.tnml = self.get_total_normalized_modified_load(HomeType.RATED_HOME)
            return self._tnml

    @tnml.setter
    def tnml(self, tnml):
        self._tnml = tnml
        self.tnml_set = True

    @property
    def trl(self):
        if self.trl_set:
            return self._trl
        else:
            self.trl = self.get_total_reference_home_load(HomeType.HERS_REFERENCE_HOME)
            return self._trl

    @trl.setter
    def trl(self, trl):
        self._trl = trl
        self.trl_set = True

    @property
    def teu(self):
        if self.teu_set:
            return self._teu
        else:
            self.teu = convert(self.get_total_energy_use_rated_home(), "kWh", "MBtu")
            return self._teu

    @teu.setter
    def teu(self, teu):
        self._teu = teu
        self.teu_set = True

    @property
    def opp(self):
        if self.opp_set:
            return self._opp
        else:
            self.opp = convert(self.get_on_site_power_production(), "kWh", "MBtu")
            return self._opp

    @opp.setter
    def opp(self, opp):
        self._opp = opp
        self.opp_set = True

    @property
    def bsl(self):
        if self.bsl_set:
            return self._bsl
        else:
            self.bsl = convert(
                self.get_battery_storage_charge_discharge(), "kWh", "MBtu"
            )
            return self._bsl

    @bsl.setter
    def bsl(self, bsl):
        self._bsl = bsl
        self.bsl_set = True

    @property
    def iad_save(self):
        if self.iad_save_set:
            return self._iad_save
        else:
            self.iad_save = self.get_index_adjustment_design_savings()
            return self._iad_save

    @iad_save.setter
    def iad_save(self, iad_save):
        self._iad_save = iad_save
        self.iad_save_set = True

    @property
    def iaf_cfa(self):
        if self.iaf_cfa_set:
            return self._iaf_cfa
        else:
            self.iaf_cfa = self.get_index_adjustment_factor_conditioned_floor_area()
            return self._iaf_cfa

    @iaf_cfa.setter
    def iaf_cfa(self, iaf_cfa):
        self._iaf_cfa = iaf_cfa
        self.iaf_cfa_set = True

    @property
    def iaf_nbr(self):
        if self.iaf_nbr_set:
            return self._iaf_nbr
        else:
            self.iaf_nbr = self.get_index_adjustment_factor_number_of_bedrooms()
            return self._iaf_nbr

    @iaf_nbr.setter
    def iaf_nbr(self, iaf_nbr):
        self._iaf_nbr = iaf_nbr
        self.iaf_nbr_set = True

    @property
    def iaf_ns(self):
        if self.iaf_ns_set:
            return self._iaf_ns
        else:
            self.iaf_ns = self.get_index_adjustment_factor_number_of_stories()
            return self._iaf_ns

    @iaf_ns.setter
    def iaf_ns(self, iaf_ns):
        self._iaf_ns = iaf_ns
        self.iaf_ns_set = True

    @property
    def tnml_iad(self):
        if self.tnml_iad_set:
            return self._tnml_iad
        else:
            self.tnml_iad = self.get_total_normalized_modified_load(
                HomeType.IAD_RATED_HOME
            )
            return self._tnml_iad

    @tnml_iad.setter
    def tnml_iad(self, tnml_iad):
        self._tnml_iad = tnml_iad
        self.tnml_iad_set = True

    @property
    def trl_iad(self):
        if self.trl_iad_set:
            return self._trl_iad
        else:
            self.trl_iad = self.get_total_reference_home_load(
                HomeType.IAD_HERS_REFERENCE_HOME
            )
            return self._trl_iad

    @trl_iad.setter
    def trl_iad(self, trl_iad):
        self._trl_iad = trl_iad
        self.trl_iad_set = True

    # Rated Home
    @property
    def nmeul_heat(self):
        if self.nmeul_heat_set:
            return self._nmeul_heat
        else:
            self.nmeul_heat = self.get_end_use_energy_consumption(
                HomeType.RATED_HOME, EndUse.SPACE_HEATING
            )
            return self._nmeul_heat

    @nmeul_heat.setter
    def nmeul_heat(self, nmeul_heat):
        self._nmeul_heat = nmeul_heat
        self.nmeul_heat_set = True

    @property
    def nmeul_cool(self):
        if self.nmeul_cool_set:
            return self._nmeul_cool
        else:
            self.nmeul_cool = self.get_end_use_energy_consumption(
                HomeType.RATED_HOME, EndUse.SPACE_COOLING
            )
            return self._nmeul_cool

    @nmeul_cool.setter
    def nmeul_cool(self, nmeul_cool):
        self._nmeul_cool = nmeul_cool
        self.nmeul_cool_set = True

    @property
    def nmeul_hw(self):
        if self.nmeul_hw_set:
            return self._nmeul_hw
        else:
            self.nmeul_hw = self.get_end_use_energy_consumption(
                HomeType.RATED_HOME, EndUse.WATER_HEATING
            )
            return self._nmeul_hw

    @nmeul_hw.setter
    def nmeul_hw(self, nmeul_hw):
        self._nmeul_hw = nmeul_hw
        self.nmeul_hw_set = True

    @property
    def ec_la(self):
        if self.ec_la_set:
            return self._ec_la
        else:
            self.ec_la = self.get_annual_end_use_energy(
                HomeType.RATED_HOME, EndUse.LIGHTING_AND_APPLIANCE
            )
            return self._ec_la

    @ec_la.setter
    def ec_la(self, ec_la):
        self._ec_la = ec_la
        self.ec_la_set = True

    @property
    def ec_vent(self):
        if self.ec_vent_set:
            return self._ec_vent
        else:
            self.ec_vent = self.get_annual_end_use_energy(
                HomeType.RATED_HOME, EndUse.VENTILATION
            )
            return self._ec_vent

    @ec_vent.setter
    def ec_vent(self, ec_vent):
        self._ec_vent = ec_vent
        self.ec_vent_set = True

    @property
    def ec_dh(self):
        if self.ec_dh_set:
            return self._ec_dh
        else:
            self.ec_dh = self.get_annual_end_use_energy(
                HomeType.RATED_HOME, EndUse.DEHUMIDIFCATION
            )
            return self._ec_dh

    @ec_dh.setter
    def ec_dh(self, ec_dh):
        self._ec_dh = ec_dh
        self.ec_dh_set = True

    # Reference Home
    @property
    def reul_heat(self):
        if self.reul_heat_set:
            return self._reul_heat
        else:
            self.reul_heat = self.get_reference_home_system_load(
                HomeType.HERS_REFERENCE_HOME, EndUse.SPACE_HEATING
            )
            return self._reul_heat

    @reul_heat.setter
    def reul_heat(self, reul_heat):
        self._reul_heat = reul_heat
        self.reul_heat_set = True

    @property
    def reul_cool(self):
        if self.reul_cool_set:
            return self._reul_cool
        else:
            self.reul_cool = self.get_reference_home_system_load(
                HomeType.HERS_REFERENCE_HOME, EndUse.SPACE_COOLING
            )
            return self._reul_cool

    @reul_cool.setter
    def reul_cool(self, reul_cool):
        self._reul_cool = reul_cool
        self.reul_cool_set = True

    @property
    def reul_hw(self):
        if self.reul_hw_set:
            return self._reul_hw
        else:
            self.reul_hw = self.get_reference_home_system_load(
                HomeType.HERS_REFERENCE_HOME, EndUse.WATER_HEATING
            )
            return self._reul_hw

    @reul_hw.setter
    def reul_hw(self, reul_hw):
        self._reul_hw = reul_hw
        self.reul_hw_set = True

    @property
    def rec_la(self):
        if self.rec_la_set:
            return self._rec_la
        else:
            self.rec_la = self.get_annual_end_use_energy(
                HomeType.HERS_REFERENCE_HOME, EndUse.LIGHTING_AND_APPLIANCE
            )
            return self._rec_la

    @rec_la.setter
    def rec_la(self, rec_la):
        self._rec_la = rec_la
        self.rec_la_set = True

    @property
    def rec_vent(self):
        if self.rec_vent_set:
            return self._rec_vent
        else:
            self.rec_vent = self.get_annual_end_use_energy(
                HomeType.HERS_REFERENCE_HOME, EndUse.VENTILATION
            )
            return self._rec_vent

    @rec_vent.setter
    def rec_vent(self, rec_vent):
        self._rec_vent = rec_vent
        self.rec_vent_set = True

    @property
    def rec_dh(self):
        if self.rec_dh_set:
            return self._rec_dh
        else:
            self.rec_dh = self.get_annual_end_use_energy(
                HomeType.HERS_REFERENCE_HOME, EndUse.DEHUMIDIFCATION
            )
            return self._rec_dh

    @rec_dh.setter
    def rec_dh(self, rec_dh):
        self._rec_dh = rec_dh
        self.rec_dh_set = True

    # IAD Rated Home
    @property
    def nmeul_heat_iad(self):
        if self.nmeul_heat_iad_set:
            return self._nmeul_heat_iad
        else:
            self.nmeul_heat_iad = self.get_end_use_energy_consumption(
                HomeType.IAD_RATED_HOME, EndUse.SPACE_HEATING
            )
            return self._nmeul_heat_iad

    @nmeul_heat_iad.setter
    def nmeul_heat_iad(self, nmeul_heat_iad):
        self._nmeul_heat_iad = nmeul_heat_iad
        self.nmeul_heat_iad_set = True

    @property
    def nmeul_cool_iad(self):
        if self.nmeul_cool_iad_set:
            return self._nmeul_cool_iad
        else:
            self.nmeul_cool_iad = self.get_end_use_energy_consumption(
                HomeType.IAD_RATED_HOME, EndUse.SPACE_COOLING
            )
            return self._nmeul_cool_iad

    @nmeul_cool_iad.setter
    def nmeul_cool_iad(self, nmeul_cool_iad):
        self._nmeul_cool_iad = nmeul_cool_iad
        self.nmeul_cool_iad_set = True

    @property
    def nmeul_hw_iad(self):
        if self.nmeul_hw_iad_set:
            return self._nmeul_hw_iad
        else:
            self.nmeul_hw_iad = self.get_end_use_energy_consumption(
                HomeType.IAD_RATED_HOME, EndUse.WATER_HEATING
            )
            return self._nmeul_hw_iad

    @nmeul_hw_iad.setter
    def nmeul_hw_iad(self, nmeul_hw_iad):
        self._nmeul_hw_iad = nmeul_hw_iad
        self.nmeul_hw_iad_set = True

    @property
    def ec_la_iad(self):
        if self.ec_la_iad_set:
            return self._ec_la_iad
        else:
            self.ec_la_iad = self.get_annual_end_use_energy(
                HomeType.IAD_RATED_HOME,
                EndUse.LIGHTING_AND_APPLIANCE,
            )
            return self._ec_la_iad

    @ec_la_iad.setter
    def ec_la_iad(self, ec_la_iad):
        self._ec_la_iad = ec_la_iad
        self.ec_la_iad_set = True

    @property
    def ec_vent_iad(self):
        if self.ec_vent_iad_set:
            return self._ec_vent_iad
        else:
            self.ec_vent_iad = self.get_annual_end_use_energy(
                HomeType.IAD_RATED_HOME, EndUse.VENTILATION
            )
            return self._ec_vent_iad

    @ec_vent_iad.setter
    def ec_vent_iad(self, ec_vent_iad):
        self._ec_vent_iad = ec_vent_iad
        self.ec_vent_iad_set = True

    @property
    def ec_dh_iad(self):
        if self.ec_dh_iad_set:
            return self._ec_dh_iad
        else:
            self.ec_dh_iad = self.get_annual_end_use_energy(
                HomeType.IAD_RATED_HOME, EndUse.DEHUMIDIFCATION
            )
            return self._ec_dh_iad

    @ec_dh_iad.setter
    def ec_dh_iad(self, ec_dh_iad):
        self._ec_dh_iad = ec_dh_iad
        self.ec_dh_iad_set = True

    # IAD Reference Home
    @property
    def reul_heat_iad(self):
        if self.reul_heat_iad_set:
            return self._reul_heat_iad
        else:
            self.reul_heat_iad = self.get_reference_home_system_load(
                HomeType.IAD_HERS_REFERENCE_HOME, EndUse.SPACE_HEATING
            )
            return self._reul_heat_iad

    @reul_heat_iad.setter
    def reul_heat_iad(self, reul_heat_iad):
        self._reul_heat_iad = reul_heat_iad
        self.reul_heat_iad_set = True

    @property
    def reul_cool_iad(self):
        if self.reul_cool_iad_set:
            return self._reul_cool_iad
        else:
            self.reul_cool_iad = self.get_reference_home_system_load(
                HomeType.IAD_HERS_REFERENCE_HOME, EndUse.SPACE_COOLING
            )
            return self._reul_cool_iad

    @reul_cool_iad.setter
    def reul_cool_iad(self, reul_cool_iad):
        self._reul_cool_iad = reul_cool_iad
        self.reul_cool_iad_set = True

    @property
    def reul_hw_iad(self):
        if self.reul_hw_iad_set:
            return self._reul_hw_iad
        else:
            self.reul_hw_iad = self.get_reference_home_system_load(
                HomeType.IAD_HERS_REFERENCE_HOME, EndUse.WATER_HEATING
            )
            return self._reul_hw_iad

    @reul_hw_iad.setter
    def reul_hw_iad(self, reul_hw_iad):
        self._reul_hw_iad = reul_hw_iad
        self.reul_hw_iad_set = True

    @property
    def rec_la_iad(self):
        if self.rec_la_iad_set:
            return self._rec_la_iad
        else:
            self.rec_la_iad = self.get_annual_end_use_energy(
                HomeType.IAD_HERS_REFERENCE_HOME,
                EndUse.LIGHTING_AND_APPLIANCE,
            )
            return self._rec_la_iad

    @rec_la_iad.setter
    def rec_la_iad(self, rec_la_iad):
        self._rec_la_iad = rec_la_iad
        self.rec_la_iad_set = True

    @property
    def rec_vent_iad(self):
        if self.rec_vent_iad_set:
            return self._rec_vent_iad
        else:
            self.rec_vent_iad = self.get_annual_end_use_energy(
                HomeType.IAD_HERS_REFERENCE_HOME, EndUse.VENTILATION
            )
            return self._rec_vent_iad

    @rec_vent_iad.setter
    def rec_vent_iad(self, rec_vent_iad):
        self._rec_vent_iad = rec_vent_iad
        self.rec_vent_iad_set = True

    @property
    def rec_dh_iad(self):
        if self.rec_dh_iad_set:
            return self._rec_dh_iad
        else:
            self.rec_dh_iad = self.get_annual_end_use_energy(
                HomeType.IAD_HERS_REFERENCE_HOME, EndUse.DEHUMIDIFCATION
            )
            return self._rec_dh_iad

    @rec_dh_iad.setter
    def rec_dh_iad(self, rec_dh_iad):
        self._rec_dh_iad = rec_dh_iad
        self.rec_dh_iad_set = True

    def get_system_energy_efficiency_coefficient(
        self, home_type: HomeType, end_use: EndUse, system_index: int
    ):
        # EEC_x for rated home
        # EEC_r for reference home
        # Retrieve energy efficiency coefficient for each system type and sub-system type
        return self.data[f"{home_type.value}_output"][f"{end_use.value}_system_output"][
            system_index
        ]["equipment_efficiency_coefficient"]

    def get_system_fuel_type(
        self, home_type: HomeType, end_use: EndUse, system_index: int
    ):
        # Retrieve fuel type
        return FuelType(
            self.data[f"{home_type.value}_output"][f"{end_use.value}_system_output"][
                system_index
            ]["primary_fuel_type"]
        )

    def get_system_energy_consumption(
        self, home_type: HomeType, end_use: EndUse, system_index: int
    ):
        # EC_x for rated home
        # EC_r for reference home
        # Retrieve energy consumption for each system type and sub-system type
        energy_consumption = 0
        for energy_use in self.data[f"{home_type.value}_output"][
            f"{end_use.value}_system_output"
        ][system_index]["energy_use"]:
            energy_consumption += self.get_system_end_use_annual_energy(
                home_type, end_use, FuelType(energy_use["fuel_type"]), system_index
            )

        return energy_consumption

    def get_normalized_energy_consumption(
        self,
        home_type: HomeType,
        reference_home_type: HomeType,
        end_use: EndUse,
        system_index: int,
    ):
        # nEC_x = EC_x * (a * EEC_x - b) * (EEC_r/EEC_x)
        # Retrieve energy consumption for each sub system and normalize the energy consumption
        # with the proper energy coefficients, 'a' and 'b'
        ec_x = self.get_system_energy_consumption(home_type, end_use, system_index)
        eec_x = self.get_system_energy_efficiency_coefficient(
            home_type, end_use, system_index
        )
        eec_r = self.get_system_energy_efficiency_coefficient(
            reference_home_type, end_use, system_index
        )
        fuel_type = self.get_system_fuel_type(home_type, end_use, system_index)
        if fuel_type in self.fossil_fuel_types:
            fuel_type = FuelType.FOSSIL_FUEL
        a = self.fuel_coefficients[(end_use, fuel_type)]["a"]
        b = self.fuel_coefficients[(end_use, fuel_type)]["b"]

        return ec_x * (a * eec_x - b) * (eec_r / eec_x)

    def get_system_loads(self, home_type: HomeType, end_use: EndUse, system_index: int):
        # REUL
        return sum(
            self.data[f"{home_type.value}_output"][f"{end_use.value}_system_output"][
                system_index
            ]["load"]
        )

    def get_normalized_modified_load(
        self, home_type: HomeType, end_use: EndUse, system_index: int
    ):
        # nMEUL  = REUL * nEC_x / EC_r
        if home_type == HomeType.RATED_HOME:
            reference_home_type = HomeType.HERS_REFERENCE_HOME
        elif home_type == HomeType.IAD_RATED_HOME:
            reference_home_type = HomeType.IAD_HERS_REFERENCE_HOME
        else:
            raise NameError(
                "'home_type' must be equal to 'rated_home' or 'iad_rated_home'."
            )

        reul = self.get_system_loads(reference_home_type, end_use, system_index)
        nec_x = self.get_normalized_energy_consumption(
            home_type, reference_home_type, end_use, system_index
        )
        ec_r = self.get_system_energy_consumption(
            reference_home_type, end_use, system_index
        )

        return reul * nec_x / ec_r

    def get_end_use_energy_consumption(self, home_type: HomeType, end_use: EndUse):
        end_use_total = 0
        for system_index in range(self.number_of_systems[end_use]):
            end_use_total += self.get_normalized_modified_load(
                home_type, end_use, system_index
            )
        return end_use_total

    def get_total_normalized_modified_load(self, home_type: HomeType):
        # TnML = nMEUL_HEAT + nMEUL_COOL + nMEUL_HW + EC_LA + EC_VENT + EC_DH
        if home_type == HomeType.RATED_HOME:
            return (
                self.nmeul_heat
                + self.nmeul_cool
                + self.nmeul_hw
                + self.ec_la
                + self.ec_vent
                + self.ec_dh
            )
        elif home_type == HomeType.IAD_RATED_HOME:
            return (
                self.nmeul_heat_iad
                + self.nmeul_cool_iad
                + self.nmeul_hw_iad
                + self.ec_la_iad
                + self.ec_vent_iad
                + self.ec_dh_iad
            )
        else:
            raise NameError(
                f"{home_type.value} is not a valid home_type in calculate_total_normalized_modified_load."
            )

    def get_reference_home_system_load(self, home_type: HomeType, end_use: EndUse):
        reul_system = 0
        for system_index in range(self.number_of_systems[end_use]):
            reul_system += self.get_system_loads(home_type, end_use, system_index)
        return reul_system

    def get_total_reference_home_load(self, home_type: HomeType):
        # TRL = REUL_HEAT + REUL_COOL + REUL_HW + REC_LA + REC_VENT + REC_DH

        if home_type == HomeType.HERS_REFERENCE_HOME:
            return (
                self.reul_heat
                + self.reul_cool
                + self.reul_hw
                + self.rec_la
                + self.rec_vent
                + self.rec_dh
            )
        elif home_type == HomeType.IAD_HERS_REFERENCE_HOME:
            return (
                self.reul_heat_iad
                + self.reul_cool_iad
                + self.reul_hw_iad
                + self.rec_la_iad
                + self.rec_vent_iad
                + self.rec_dh_iad
            )
        else:
            raise NameError(
                f"{home_type} is not a valid home_type in calculate_total_reference_home_load."
            )

    def get_system_end_use_annual_energy(
        self,
        home_type: HomeType,
        end_use: EndUse,
        fuel_type: FuelType,
        system_index: int,
    ):
        if (
            home_type,
            end_use,
            fuel_type,
            system_index,
        ) not in self.annual_subsystem_energy_cache:
            self.annual_subsystem_energy_cache[
                (home_type, end_use, fuel_type, system_index)
            ] = self.get_fuel_energy(
                fuel_type,
                self.data[f"{home_type.value}_output"][
                    f"{end_use.value}_system_output"
                ][system_index]["energy_use"],
            )
        return self.annual_subsystem_energy_cache[
            (home_type, end_use, fuel_type, system_index)
        ]

    def get_fuel_energy(self, fuel_type: FuelType, energy_uses: List[Dict]):
        total_energy = 0
        for energy_use in energy_uses:
            if fuel_type.value == energy_use["fuel_type"]:
                total_energy += sum(energy_use["energy"])
        return total_energy

    def get_annual_energy(
        self, home_type: HomeType, end_use: EndUse, fuel_type: FuelType
    ):
        if (home_type, end_use, fuel_type) not in self.annual_energy_cache:
            total_energy = 0
            if end_use in self.system_end_uses:
                for system_index, energy_data in enumerate(
                    self.data[f"{home_type.value}_output"][
                        f"{end_use.value}_system_output"
                    ]
                ):
                    total_energy += self.get_system_end_use_annual_energy(
                        home_type,
                        end_use,
                        fuel_type,
                        system_index,
                    )
            else:  # other end uses
                if f"{end_use.value}_energy" in self.data[f"{home_type.value}_output"]:
                    energy_data = self.data[f"{home_type.value}_output"][
                        f"{end_use.value}_energy"
                    ]
                    total_energy += self.get_fuel_energy(fuel_type, energy_data)
            self.annual_energy_cache[(home_type, end_use, fuel_type)] = total_energy
        return self.annual_energy_cache[(home_type, end_use, fuel_type)]

    def get_annual_end_use_energy(self, home_type: HomeType, end_use: EndUse):
        if (home_type, end_use) not in self.annual_end_use_energy_cache:
            total_energy = 0
            for fuel_type in self.fuel_types:
                total_energy += self.get_annual_energy(home_type, end_use, fuel_type)
            self.annual_end_use_energy_cache[(home_type, end_use)] = total_energy
        return self.annual_end_use_energy_cache[(home_type, end_use)]

    def get_annual_fuel_type_energy(self, home_type: HomeType, fuel_type: FuelType):
        if (home_type, fuel_type) not in self.annual_fuel_type_energy_cache:
            total_energy = 0
            for end_use in self.end_uses:
                total_energy += self.get_annual_energy(home_type, end_use, fuel_type)
            self.annual_fuel_type_energy_cache[(home_type, fuel_type)] = total_energy
        return self.annual_fuel_type_energy_cache[(home_type, fuel_type)]

    def get_hourly_electricity_emissions(self, home_type: HomeType):
        for end_use in self.end_uses:
            if end_use in self.system_end_uses:
                for energy_data in self.data[f"{home_type.value}_output"][
                    f"{end_use.value}_system_output"
                ]:
                    for energy_use in energy_data["energy_use"]:
                        if energy_use["fuel_type"] == FuelType.ELECTRICITY.value:
                            self.hourly_electricity_use[home_type] = element_add(
                                energy_use["energy"],
                                self.hourly_electricity_use[home_type],
                            )
            else:  # other end uses
                if f"{end_use.value}_energy" in self.data[f"{home_type.value}_output"]:
                    for energy_use in self.data[f"{home_type.value}_output"][
                        f"{end_use.value}_energy"
                    ]:
                        if energy_use["fuel_type"] == FuelType.ELECTRICITY.value:
                            self.hourly_electricity_use[home_type] = element_add(
                                energy_use["energy"],
                                self.hourly_electricity_use[home_type],
                            )
        return self.hourly_electricity_use[home_type]

    def get_annual_hourly_co2_emissions(self, home_type: HomeType):
        emissions = 0
        for fuel_type in self.fuel_types:
            if fuel_type == FuelType.ELECTRICITY:
                emissions += sum(
                    element_product(
                        self.get_hourly_electricity_emissions(home_type),
                        self.hourly_electricity_emission_factors_kbtu,
                    )
                )
            else:
                emissions += (
                    self.get_annual_fuel_type_energy(home_type, fuel_type)
                    * self.fuel_emission_factors[fuel_type]
                )
        if "on_site_power_production" in self.data:
            emissions += sum(
                element_product(
                    [-value for value in self.data["on_site_power_production"]],  # kWh
                    self.hourly_electricity_emission_factors_kwh,  # lb/kWh
                )
            )
        if "battery_storage" in self.data:
            emissions += sum(
                element_product(
                    self.data["battery_storage"],
                    self.hourly_electricity_emission_factors_kwh,
                )
            )
        return emissions

    def get_iad_hers_index(self):
        # ERI = TnML_IAD / TRL_IAD

        return self.tnml_iad / self.trl_iad * 100

    def get_index_adjustment_design_savings(self):
        # IAD_SAVE = (100 - ERI_IAD) / 100

        eri_iad = self.get_iad_hers_index()

        return (100 - eri_iad) / 100

    def get_index_adjustment_factor_conditioned_floor_area(self):
        # IAF_RH = (2400/CFA) ^ (0.304 * IAD_SAVE)

        cfa = self.data["conditioned_floor_area"]

        return (2400 / cfa) ** (0.304 * self.iad_save)

    def get_index_adjustment_factor_number_of_bedrooms(self):
        # IAF_Nbr = 1 + (0.069 * IAD_SAVE * (NBr - 3))

        nbr = self.data["number_of_bedrooms"]

        return 1 + (0.069 * self.iad_save * (nbr - 3))

    def get_index_adjustment_factor_number_of_stories(self):
        # IAF_NS = (2/NS) ^ (0.12 * IAD_SAVE)

        ns = self.data["number_of_stories"]

        return (2 / ns) ** (0.12 * self.iad_save)

    def get_fuel_conversion(self, fuel_type: FuelType):
        # If fuel type is a fossil fuel, return 0.4, else return 1

        if fuel_type in self.fossil_fuel_types:
            return 0.4
        return 1.0

    def get_sub_system_energy_use(self, energy_use_specs):
        # Calculate the sub-system energy use, converted into kWh

        energy_use_hourly = energy_use_specs["energy"]
        fuel_type = FuelType(energy_use_specs["fuel_type"])
        return convert(
            sum(energy_use_hourly) * self.get_fuel_conversion(fuel_type),
            "kBtu",
            "kWh",
        )

    def get_total_energy_use_rated_home(self):
        # calculate total energy use from the rated home

        teu = 0
        for end_use, number_of_systems in self.number_of_systems.items():
            number_of_systems = len(
                self.data["rated_home_output"][f"{end_use.value}_system_output"]
            )
            for system_index in range(number_of_systems):
                for energy_use_specs in self.data["rated_home_output"][
                    f"{end_use.value}_system_output"
                ][system_index]["energy_use"]:
                    teu += self.get_sub_system_energy_use(energy_use_specs)
        for other_end_use, number_of_systems in self.number_of_other_end_uses.items():
            for energy_use_specs in self.data["rated_home_output"][
                f"{other_end_use.value}_energy"
            ]:
                teu += self.get_sub_system_energy_use(energy_use_specs)
        return teu

    def get_battery_storage_charge_discharge(self):
        # Calculate net annual battery storage losses of the rated home

        if "battery_storage" in self.data:
            return sum(self.data["battery_storage"])
        return 0.0

    def get_on_site_power_production(self):
        # Calculate on-site power production (OPP)

        if "on_site_power_production" in self.data:
            return sum(self.data["on_site_power_production"])
        return 0.0

    def check_index_mismatch(
        self, index_name: str, calculated_index: float, output_index: float
    ):
        difference_ratio = abs(calculated_index - output_index) / output_index
        if difference_ratio >= self.INDEX_TOLERANCE:
            raise RuntimeError(
                f"""\n{self.project_name} {index_name} outside tolerance.\nCalculated Index: {calculated_index:.2f}\nOutput Index: {output_index:.2f}\nPercent Difference: {difference_ratio * 100:.2f}%"""
            )
        else:
            print(f"""{self.project_name} {index_name} within tolerance.""")

    def verify_hers_index(self):
        self.check_index_mismatch(
            "HERS Index", self.hers_index, self.data["hers_index"]
        )

    def verify_carbon_index(self):
        self.check_index_mismatch(
            "CO2 Index", self.co2_index, self.data["carbon_index"]
        )

    def verify(self):
        self.verify_hers_index()
        self.verify_carbon_index()

    def get_hers_index_intermediaries(self) -> Dict:
        return {
            "hers_index": self.hers_index,
            "co2_index": self.co2_index,
            "iaf_rh": self.iaf_rh,
            "aco2": self.aco2,
            "arco2": self.arco2,
            "pe_frac": self.pe_frac,
            "tnml": self.tnml,
            "trl": self.trl,
            "teu": self.teu,
            "opp": self.opp,
            "bsl": self.bsl,
            "iad_save": self.iad_save,
            "iaf_cfa": self.iaf_cfa,
            "iaf_nbr": self.iaf_nbr,
            "iaf_ns": self.iaf_ns,
            "tnml_iad": self.tnml_iad,
            "trl_iad": self.trl_iad,
            "nmeul_heat": self.nmeul_heat,
            "nmeul_cool": self.nmeul_cool,
            "nmeul_hw": self.nmeul_hw,
            "ec_la": self.ec_la,
            "ec_vent": self.ec_vent,
            "ec_dh": self.ec_dh,
            "nmeul_heat_iad": self.nmeul_heat_iad,
            "nmeul_cool_iad": self.nmeul_cool_iad,
            "nmeul_hw_iad": self.nmeul_hw_iad,
            "ec_la_iad": self.ec_la_iad,
            "ec_vent_iad": self.ec_vent_iad,
            "ec_dh_iad": self.ec_dh_iad,
            "reul_heat": self.reul_heat,
            "reul_cool": self.reul_cool,
            "reul_hw": self.reul_hw,
            "rec_la": self.rec_la,
            "rec_vent": self.rec_vent,
            "rec_dh": self.rec_dh,
            "reul_heat_iad": self.reul_heat_iad,
            "reul_cool_iad": self.reul_cool_iad,
            "reul_hw_iad": self.reul_hw_iad,
            "rec_la_iad": self.rec_la_iad,
            "rec_vent_iad": self.rec_vent_iad,
            "rec_dh_iad": self.rec_dh_iad,
        }
