"""Package calculating HERS Index."""

import lattice  # type: ignore
from koozie import convert  # type: ignore


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


class HERSDiagnosticData:

    # Define coefficients 'a' and 'b based on Table 4.1.1(1) in Standard 301 for
    # space heating, space cooling, and water heating
    fuel_coefficients = {
        ("space_heating", "ELECTRICITY"): {"a": 2.2561, "b": 0},
        ("space_heating", "FOSSIL_FUEL"): {"a": 1.0943, "b": 0.403},
        ("space_heating", "BIOMASS"): {"a": 0.885, "b": 0.4047},
        ("space_cooling", "ELECTRICITY"): {"a": 3.809, "b": 0},
        ("water_heating", "ELECTRICITY"): {"a": 0.92, "b": 0},
        ("water_heating", "FOSSIL_FUEL"): {"a": 1.1877, "b": 1.013},
    }

    home_types = ["rated_home", "hers_reference_home", "co2_reference_home"]

    # Fossil fuel co2e coefficients
    # TODO: biomass is not included, and will need to be added in a future version
    fuel_emission_factors = {
        "NATURAL_GAS": convert(147.3, "lb/MBtu", "lb/kBtu"),
        "FUEL_OIL_2": convert(195.9, "lb/MBtu", "lb/kBtu"),
        "LIQUID_PETROLEUM_GAS": convert(177.8, "lb/MBtu", "lb/kBtu"),
    }

    # define FOSSIL_FUEL types to allocate proper 'a' and 'b' coefficients in fuel_coefficients dictionary
    fossil_fuel_types = ["NATURAL_GAS", "FUEL_OIL_2", "LIQUID_PETROLEUM_GAS"]
    energy_types = fossil_fuel_types + ["ELECTRICITY"]
    system_types = ["space_heating", "space_cooling", "water_heating"]
    other_end_uses = ["lighting_and_appliance", "ventilation", "dehumidification"]

    time_types = ["annual", "hourly"]

    # '_system_output" and "_energy" are added to simplify code for co2e emission calculation
    system_types_system_output = [
        system_type + "_system_output" for system_type in system_types
    ]
    other_end_uses_energy = [
        other_end_use + "_energy" for other_end_use in other_end_uses
    ]

    INDEX_TOLERANCE = 0.005
    NUMBER_OF_TIMESTEPS = 8760

    def __init__(self, file):
        # load data
        # determine number of sub-systems for each system type (ex. determine number of heating systems)
        self.data = lattice.load(file)
        self.number_of_systems = {}
        for system_type in self.system_types:
            self.number_of_systems[system_type] = len(
                self.data["rated_home_output"][f"{system_type}_system_output"]
            )
        self.number_of_other_end_uses = {}
        for other_end_use in self.other_end_uses:
            try:
                self.number_of_other_end_uses[other_end_use] = len(
                    self.data["rated_home_output"][f"{other_end_use}_energy"]
                )
            except:
                pass

        # initialize energy use for each fuel type and home type to calculate co2e emissions
        # TODO: there will be several layers to the data cache
        # TODO: loop through to initialize data cache, start with loads, and then afterwards we can add other items to the cache

        self.data_cache = {}

        for home_type in self.home_types:
            for energy_type in self.energy_types:
                for time_type in self.time_types:
                    if time_type == "hourly":
                        self.data_cache[(energy_type, home_type, time_type)] = [
                            0
                        ] * self.NUMBER_OF_TIMESTEPS
                    elif time_type == "annual":
                        self.data_cache[(energy_type, home_type, time_type)] = 0

        self.emissions = {"rated_home": 0, "co2_reference_home": 0}

    def get_system_energy_efficiency_coefficient(
        self, home_type, system_type, system_index
    ):
        # EEC_x for rated home
        # EEC_r for reference home
        # Retrieve energy efficiency coefficient for each system type and sub-system type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][
            system_index
        ]["equipment_efficiency_coefficient"]

    def get_system_fuel_type(self, home_type, system_type, system_index):
        # Retrieve fuel type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][
            system_index
        ]["primary_fuel_type"]

    def get_system_fuel_type_co2(self, home_type, system_type, system_index):
        # Retrieve fuel type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][
            system_index
        ]["energy_use"]

    def get_system_energy_consumption(self, home_type, system_type, system_index):
        # EC_x for rated home
        # EC_r for reference home
        # Retrieve energy consumption for each system type and sub-system type
        energy_consumption = 0
        for energy_use in self.data[f"{home_type}_output"][
            f"{system_type}_system_output"
        ][system_index]["energy_use"]:
            energy_consumption += sum(energy_use["energy"])

        return energy_consumption

    def calculate_normalized_energy_consumption(
        self, home_type, reference_home_type, system_type, system_index
    ):
        # nEC_x = EC_x * (a * EEC_x - b) * (EEC_r/EEC_x)
        # Retrieve energy consumption for each sub system and normalize the energy consumption
        # with the proper energy coefficients, 'a' and 'b'
        EC_x = self.get_system_energy_consumption(home_type, system_type, system_index)
        EEC_x = self.get_system_energy_efficiency_coefficient(
            home_type, system_type, system_index
        )
        EEC_r = self.get_system_energy_efficiency_coefficient(
            reference_home_type, system_type, system_index
        )
        fuel_type = self.get_system_fuel_type(home_type, system_type, system_index)
        if fuel_type in self.fossil_fuel_types:
            fuel_type = "FOSSIL_FUEL"
        a = self.fuel_coefficients[(system_type, fuel_type)]["a"]
        b = self.fuel_coefficients[(system_type, fuel_type)]["b"]

        return EC_x * (a * EEC_x - b) * (EEC_r / EEC_x)

    def get_system_loads(self, home_type, system_type, system_index):
        # TODO: change name to get_system...
        # TODO: if new calculation --> store, if already calculated --> retrieve
        # REUL
        return sum(
            self.data[f"{home_type}_output"][f"{system_type}_system_output"][
                system_index
            ]["load"]
        )

    def calculate_normalized_modified_load(self, system_type, system_index, home_type):
        # nMEUL  = REUL * nEC_x / EC_r
        if home_type == "rated_home":
            reference_home_type = "hers_reference_home"
        elif home_type == "iad_rated_home":
            reference_home_type = "iad_hers_reference_home"
        else:
            raise NameError(
                "'home_type' must be equal to 'rated_home' or 'iad_rated_home'."
            )

        REUL = self.get_system_loads(reference_home_type, system_type, system_index)
        nEC_x = self.calculate_normalized_energy_consumption(
            home_type, reference_home_type, system_type, system_index
        )
        EC_r = self.get_system_energy_consumption(
            reference_home_type, system_type, system_index
        )

        return REUL * nEC_x / EC_r

    def calculate_other_end_use_system_energy_types(self, home_type, other_end_use):
        # sum other end use system energy use (ex. lighting and appliances may use electricity and natural gas; this ensures both natural gas and electricity are accounted for)

        system_total = 0
        home_type_output = self.data[f"{home_type}_output"]
        other_end_use_energy = f"{other_end_use}_energy"

        if other_end_use_energy not in home_type_output:
            return system_total

        energy_output = home_type_output[other_end_use_energy]

        for fuel_type_index in range(len(energy_output)):
            system_total += sum(energy_output[fuel_type_index]["energy"])

        return system_total

    def calculate_other_end_use_energy_consumption(self, home_type):
        # EC for lighting and appliances, ventilation, and dehumidification
        # REC for lighting and appliances, ventilation, and dehumidification

        end_use_total = 0

        for other_end_use in self.other_end_uses:
            end_use_total += self.calculate_other_end_use_system_energy_types(
                home_type, other_end_use
            )

        return end_use_total

    def calculate_total_normalized_modified_load(self, home_type):
        # TnML = nMEUL_HEAT + nMEUL_COOL + nMEUL_HW + EC_LA + EC_VENT + EC_DH

        # Calculate total normalized rated home loads for heating (nMEUL_HEAT), cooling (nMEUL_COOL), and hot water (nMEUL_HW)
        nMEUL_total = 0
        for system_type in self.system_types:
            for system_index in range(self.number_of_systems[system_type]):
                nMEUL_total += self.calculate_normalized_modified_load(
                    system_type, system_index, home_type
                )

        # Calculate rated home other end use energy consumption (lighting and appliances (EC_LA),
        # ventilation (EC_VENT), and dehumidification (EC_DH))
        EC_end_use_total = self.calculate_other_end_use_energy_consumption(home_type)

        return nMEUL_total + EC_end_use_total

    def calculate_total_reference_home_load(self, home_type):
        # TRL = REUL_HEAT + REUL_COOL + REUL_HW + REC_LA + REC_VENT + REC_DH

        # Calculate total reference home loads for heating (REUL_HEAT), cooling (REUL_COOL), and hot water (REUL_HW)
        REUL_total = 0
        for system_type in self.system_types:
            for system_index in range(self.number_of_systems[system_type]):
                REUL_total += self.get_system_loads(
                    home_type, system_type, system_index
                )

        # Calculate reference home other end use energy consumption (lighting and appliances (REC_LA),
        # ventilation (REC_VENT), and dehumidification (REC_DH))
        REC_system_total = self.calculate_other_end_use_energy_consumption(home_type)

        return REUL_total + REC_system_total

    def calculate_energy_type_total_energy(self, energy_use, home_type):
        # add annual energy use by fuel type for each system to data_cache dictionary
        # data_cache will be used to sum energy use by fuel type for rated home and co2 reference home and calculate annual co2e emissions

        fuel_type = energy_use["fuel_type"]
        energy = energy_use["energy"]

        self.data_cache[(fuel_type, home_type, "hourly")] = element_add(
            self.data_cache[(fuel_type, home_type, "hourly")], energy
        )
        self.data_cache[(fuel_type, home_type, "annual")] += sum(energy)

    def multiply_energy_use_and_emission_factors(self):
        # multiply co2e emission factors with each fuel type and home type, and then find annual co2e emissions for each home type

        for key in self.data_cache.keys():
            fuel_type = key[0]
            home_type = key[1]
            if home_type != "hers_reference_home":
                if fuel_type == "ELECTRICITY":
                    # conversion of electricity co2e lb/kWh to lb/kbtu is included in calculation below
                    self.emissions[home_type] += convert(
                        sum(
                            element_product(
                                self.data["electricity_co2_emissions_factors"],
                                self.data_cache[(fuel_type, home_type, "hourly")],
                            )
                        ),
                        "lb/kWh",
                        "lb/kBtu",
                    )
                else:
                    self.emissions[home_type] += (
                        self.data_cache[(fuel_type, home_type, "annual")]
                        * self.fuel_emission_factors[fuel_type]
                    )

    def calculate_annual_hourly_co2_emissions(self):
        # retrieve energy use for each subsystem and multiply energy by emissions factors

        for home_type in ["rated_home", "co2_reference_home"]:
            for system_type in self.data[f"{home_type}_output"]:
                if system_type in self.system_types_system_output:
                    for system_index in range(
                        len(self.data[f"{home_type}_output"][system_type])
                    ):
                        for energy_use in self.data[f"{home_type}_output"][system_type][
                            system_index
                        ]["energy_use"]:
                            self.calculate_energy_type_total_energy(
                                energy_use, home_type
                            )
                elif system_type in self.other_end_uses_energy:
                    for energy_use in self.data[f"{home_type}_output"][system_type]:
                        self.calculate_energy_type_total_energy(energy_use, home_type)

        self.multiply_energy_use_and_emission_factors()

    def calculate_iad_hers_index(self):
        # ERI = TnML_IAD / TRL_IAD

        TnML_IAD = self.calculate_total_normalized_modified_load("iad_rated_home")
        TRL_IAD = self.calculate_total_reference_home_load("iad_hers_reference_home")

        return TnML_IAD / TRL_IAD

    def calculate_index_adjustment_design_savings(self):
        # IAD_SAVE = (100 - ERI_IAD) / 100

        ERI_IAD = self.calculate_iad_hers_index() * 100

        return (100 - ERI_IAD) / 100

    def calculate_index_adjustment_factor_conditioned_floor_area(self, IAD_SAVE):
        # IAF_RH = (2400/CFA) ^ (0.304 * IAD_SAVE)

        CFA = self.data["conditioned_floor_area"]

        return (2400 / CFA) ** (0.304 * IAD_SAVE)

    def calculate_index_adjustment_factor_number_of_bedrooms(self, IAD_SAVE):
        # IAF_Nbr = 1 + (0.069 * IAD_SAVE * (NBr - 3))

        NBr = self.data["number_of_bedrooms"]

        return 1 + (0.069 * IAD_SAVE * (NBr - 3))

    def calculate_index_adjustment_factor_number_of_stories(self, IAD_SAVE):
        # IAF_NS = (2/NS) ^ (0.12 * IAD_SAVE)

        NS = self.data["number_of_stories"]

        return (2 / NS) ** (0.12 * IAD_SAVE)

    def calculate_index_adjustment_factor_rated_home(self):
        # IAF_RH = IAF_CFA * IAF_Nbr * IAF_NS

        IAD_SAVE = self.calculate_index_adjustment_design_savings()
        IAF_CFA = self.calculate_index_adjustment_factor_conditioned_floor_area(
            IAD_SAVE
        )
        IAF_Nbr = self.calculate_index_adjustment_factor_number_of_bedrooms(IAD_SAVE)
        IAF_NS = self.calculate_index_adjustment_factor_number_of_stories(IAD_SAVE)

        return IAF_CFA * IAF_Nbr * IAF_NS

    def get_fuel_conversion(self, fuel_type):
        # If fuel type is a fossil fuel, return 0.4, else return 1

        if fuel_type in self.fossil_fuel_types:
            return 0.4
        else:
            return 1

    def get_annual_energy_use_or_consumption(self, energy_use_hourly):
        # return the annual energy use from an 8760 array

        return sum(energy_use_hourly)

    def calculate_sub_system_energy_use(self, energy_use_specs):
        # Calculate the sub-system energy use, converted into kWh

        energy_use_hourly = energy_use_specs["energy"]
        fuel_type = energy_use_specs["fuel_type"]
        return convert(
            self.get_annual_energy_use_or_consumption(energy_use_hourly)
            * self.get_fuel_conversion(fuel_type),
            "kBtu",
            "kWh",
        )

    def calculate_total_energy_use_rated_home(self):
        # calculate total energy use from the rated home

        TEU = 0
        for system_type, number_of_systems in self.number_of_systems.items():
            number_of_systems = len(
                self.data["rated_home_output"][f"{system_type}_system_output"]
            )
            for system_index in range(number_of_systems):
                for energy_use_specs in self.data["rated_home_output"][
                    f"{system_type}_system_output"
                ][system_index]["energy_use"]:
                    TEU += self.calculate_sub_system_energy_use(energy_use_specs)
        for other_end_use, number_of_systems in self.number_of_other_end_uses.items():
            for energy_use_specs in self.data["rated_home_output"][
                f"{other_end_use}_energy"
            ]:
                TEU += self.calculate_sub_system_energy_use(energy_use_specs)
        return TEU

    def calculate_battery_storage_charge_discharge(self):
        # Calculate net annual battery storage losses of the rated home

        try:
            return sum(self.data["battery_storage"])
        except:
            return 0.0

    def calculate_on_site_power_production(self):
        # Calculate on-site power production (OPP)

        try:
            return self.get_annual_energy_use_or_consumption(
                self.data["on_site_power_production"]
            )
        except:
            return 0.0

    def calculate_pefrac(self):
        # PEfrac = (TEU - OPP) / TEU
        TEU = convert(self.calculate_total_energy_use_rated_home(), "kWh", "MBtu")
        OPP = convert(self.calculate_on_site_power_production(), "kWh", "MBtu")
        BSL = convert(self.calculate_battery_storage_charge_discharge(), "kWh", "MBtu")
        calc = (TEU - OPP + BSL) / TEU
        return calc

    def calculate_hers_index(self):
        # ERI = PEfrac * (TnML / TRL * IAF_RH) * 100

        PEfrac = self.calculate_pefrac()
        TnML = self.calculate_total_normalized_modified_load("rated_home")
        TRL = self.calculate_total_reference_home_load("hers_reference_home")
        IAF_RH = self.calculate_index_adjustment_factor_rated_home()

        return PEfrac * TnML / (TRL * IAF_RH) * 100

    def calculate_carbon_index(self):
        # CO2 Index = ACO2 / ARCO2 * 100

        self.calculate_annual_hourly_co2_emissions()
        ACO2 = self.emissions["rated_home"]
        ARCO2 = self.emissions["co2_reference_home"]
        IAF_RH = self.calculate_index_adjustment_factor_rated_home()

        return ACO2 / (ARCO2 * IAF_RH) * 100

    def check_index_mismatch(self, index_name, calculated_index, output_index):
        difference_ratio = (calculated_index - output_index) / output_index
        if difference_ratio >= self.INDEX_TOLERANCE:
            raise RuntimeError(
                f"""\n{self.data["project_name"]} {index_name} outside tolerance.\nCalculated Index: {calculated_index:.2f}\nOutput Index: {output_index:.2f}\nPercent Difference: {difference_ratio*100:.2f}%"""
            )
        else:
            print(f"""{self.data["project_name"]} {index_name} within tolerance.""")

    def verify_hers_index(self):
        self.check_index_mismatch(
            "HERS Index", self.calculate_hers_index(), self.data["hers_index"]
        )

    def verify_carbon_index(self):
        self.check_index_mismatch(
            "CO2 Index", self.calculate_carbon_index(), self.data["carbon_index"]
        )

    def verify(self):
        self.verify_hers_index()
        self.verify_carbon_index()


# REUL calculation is repeated. This could be simplified by caching data in a dictionary.
