from typing import TYPE_CHECKING

from koozie import convert

if TYPE_CHECKING:
    from .hers_diagnostic_output import HERSDiagnosticOutput


class HERSCache:
    def __init__(self, hers_diagnostic_output: "HERSDiagnosticOutput"):
        self.hers_diagnostic_output = hers_diagnostic_output

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
            self.co2_index = self.aco2 / (self.arco2 * self.iaf_rh) * 100  # CO2 Index = ACO2 / ARCO2 * 100
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
            self.iaf_rh = self.iaf_cfa * self.iaf_nbr * self.iaf_ns  # IAF_RH = IAF_CFA * IAF_Nbr * IAF_NS
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
            self.arco2 = self.get_annual_hourly_co2_emissions(HomeType.CO2_REFERENCE_HOME)
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
            self.pe_frac = (self.teu - self.opp + self.bsl) / self.teu  # PEfrac = (TEU - OPP) / TEU
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
            self.tnml = (
                self.hers_diagnostic_output.rated_home_output.space_heating_system_output.nmeul
                + self.hers_diagnostic_output.rated_home_output.space_cooling_system_output.nmeul
                + self.hers_diagnostic_output.rated_home_output.water_heating_system_output.nmeul
                + self.hers_diagnostic_output.rated_home_output.lighting_and_appliance_energy.energy_annual_total
                + self.hers_diagnostic_output.rated_home_output.ventilation_energy.energy_annual_total
                + self.hers_diagnostic_output.rated_home_output.dehumidification_energy.energy_annual_total
            )

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
            self.trl = (
                self.hers_diagnostic_output.hers_reference_home_output.space_heating_system_output.reul
                + self.hers_diagnostic_output.hers_reference_home_output.space_cooling_system_output.reul
                + self.hers_diagnostic_output.hers_reference_home_output.water_heating_system_output.reul
                + self.hers_diagnostic_output.hers_reference_home_output.lighting_and_appliance_energy.energy_annual_total
                + self.hers_diagnostic_output.hers_reference_home_output.ventilation_energy.energy_annual_total
                + self.hers_diagnostic_output.hers_reference_home_output.dehumidification_energy.energy_annual_total
            )
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
            self.teu = convert(
                self.hers_diagnostic_output.rated_home_output.space_heating_system_output.energy_electricity_use_equivalent
                + self.hers_diagnostic_output.rated_home_output.space_cooling_system_output.energy_electricity_use_equivalent
                + self.hers_diagnostic_output.rated_home_output.water_heating_system_output.energy_electricity_use_equivalent
                + self.hers_diagnostic_output.rated_home_output.lighting_and_appliance_energy.energy_electricity_use_equivalent
                + self.hers_diagnostic_output.rated_home_output.ventilation_energy.energy_electricity_use_equivalent
                + self.hers_diagnostic_output.rated_home_output.dehumidification_energy.energy_electricity_use_equivalent,
                "kWh",
                "MWh",
            )
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
            self.opp = convert(self.hers_diagnostic_output.on_site_power_production_annual, "kWh", "MBtu")
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
            self.bsl = convert(self.hers_diagnostic_output.battery_storage_annual, "kWh", "MBtu")
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
            self.tnml_iad = self.get_total_normalized_modified_load(HomeType.IAD_RATED_HOME)
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
            self.trl_iad = self.get_total_reference_home_load(HomeType.IAD_HERS_REFERENCE_HOME)
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
            self.nmeul_heat = self.hers_diagnostic_output.rated_home_output.space_heating_system_output.nmeul
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
            self.nmeul_cool = self.hers_diagnostic_output.rated_home_output.space_cooling_system_output.nmeul
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
            self.nmeul_hw = self.hers_diagnostic_output.rated_home_output.water_heating_system_output.nmeul
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
            self.ec_la = self.hers_diagnostic_output.rated_home_output.lighting_and_appliance_energy.energy_annual_total
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
            self.ec_vent = self.hers_diagnostic_output.rated_home_output.ventilation_energy.energy_annual_total
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
            self.ec_dh = self.hers_diagnostic_output.rated_home_output.dehumidification_energy.energy_annual_total
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
            self.reul_heat = self.hers_diagnostic_output.hers_reference_home_output.space_heating_system_output.reul
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
            self.reul_cool = self.hers_diagnostic_output.hers_reference_home_output.space_cooling_system_output.reul
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
            self.reul_hw = self.hers_diagnostic_output.hers_reference_home_output.water_heating_system_output.reul
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
            self.rec_la = self.hers_diagnostic_output.hers_reference_home_output.lighting_and_appliance_energy.energy_annual_total
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
            self.rec_vent = self.hers_diagnostic_output.hers_reference_home_output.ventilation_energy.energy_annual_total
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
            self.rec_dh = self.hers_diagnostic_output.hers_reference_home_output.dehumidification_energy.energy_annual_total
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
            self.nmeul_heat_iad = self.hers_diagnostic_output.iad_rated_home_output.space_heating_system_output.nmeul
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
            self.nmeul_cool_iad = self.hers_diagnostic_output.iad_rated_home_output.space_cooling_system_output.nmeul
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
            self.nmeul_hw_iad = self.hers_diagnostic_output.iad_rated_home_output.water_heating_system_output.nmeul
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
            self.ec_la_iad = self.hers_diagnostic_output.iad_rated_home_output.lighting_and_appliance_energy.energy_annual_total
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
            self.ec_vent_iad = self.hers_diagnostic_output.iad_rated_home_output.ventilation_energy.energy_annual_total
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
            self.ec_dh_iad = self.hers_diagnostic_output.iad_rated_home_output.dehumidification_energy.energy_annual_total
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
            self.reul_heat_iad = self.hers_diagnostic_output.iad_hers_reference_home_output.space_heating_system_output.reul
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
            self.reul_cool_iad = self.hers_diagnostic_output.iad_hers_reference_home_output.space_cooling_system_output.reul
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
            self.reul_hw_iad = self.hers_diagnostic_output.iad_hers_reference_home_output.water_heating_system_output.reul
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
            self.rec_la_iad = self.hers_diagnostic_output.iad_hers_reference_home_output.lighting_and_appliance_energy.energy_annual_total
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
            self.rec_vent_iad = self.hers_diagnostic_output.iad_hers_reference_home_output.ventilation_energy.energy_annual_total
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
            self.rec_dh_iad = self.hers_diagnostic_output.iad_hers_reference_home_output.dehumidification_energy.energy_annual_total
            return self._rec_dh_iad

    @rec_dh_iad.setter
    def rec_dh_iad(self, rec_dh_iad):
        self._rec_dh_iad = rec_dh_iad
        self.rec_dh_iad_set = True
