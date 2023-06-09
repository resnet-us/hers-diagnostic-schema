import lattice

from koozie import convert

def element_add(list1, list2):
    number_of_elements = len(list1)
    list3 = [0]*number_of_elements
    for i in range(number_of_elements):
        list3[i] = list1[i] + list2[i]
    return list3

def element_product(list1, list2):
    number_of_elements = len(list1)
    list3 = [0]*number_of_elements
    for i in range(number_of_elements):
        list3[i] = list1[i]*list2[i]
    return list3

class HERSDiagnosticData:

    # Define coefficients 'a' and 'b based on Table 4.1.1(1) in Standard 301 for
    # space heating, space cooling, and water heating
    fuel_coefficients = {("space_heating","ELECTRICITY"):{"a":2.2561,"b":0},
                         ("space_heating","FOSSIL_FUEL"):{"a":1.0943,"b":0.403},
                         ("space_heating","BIOMASS"):{"a":0.885,"b":0.4047},
                         ("space_cooling","ELECTRICITY"):{"a":3.809,"b":0},
                         ("water_heating","ELECTRICITY"):{"a":0.92,"b":0},
                         ("water_heating","FOSSIL_FUEL"):{"a":1.1877,"b":1.013}}

    home_types = ['rated_home','hers_reference_home','co2_reference_home']

    # Fossil fuel co2e coefficients
    # TODO: biomass is not included, and will need to be added in a future version
    fuel_emission_factors = {'NATURAL_GAS': convert(147.3, "lb/MBtu", "lb/kBtu"),
                             'FUEL_OIL_2': convert(195.9, "lb/MBtu", "lb/kBtu"),
                             'LIQUID_PETROLEUM_GAS': convert(177.8, "lb/MBtu", "lb/kBtu")
                             }

    # define FOSSIL_FUEL types to allocate proper 'a' and 'b' coefficients in fuel_coefficients dictionary
    fossil_fuel_types = ['NATURAL_GAS','FUEL_OIL_2','LIQUID_PETROLEUM_GAS']
    energy_types = fossil_fuel_types + ['ELECTRICITY']
    system_types = ['space_heating','space_cooling','water_heating'] 
    other_end_uses = ['lighting_and_appliance','ventilation','dehumidification']

    # '_system_output" and "_energy" are added to simplify code for co2e emission calculation
    system_types_system_output = [system_type + '_system_output' for system_type in system_types]
    other_end_uses_energy = [other_end_use + '_energy' for other_end_use in other_end_uses]

    INDEX_TOLERANCE = 0.01
    NUMBER_OF_TIMESTEPS = 8760

    def __init__(self, file):
        # load data
        # determine number of sub-systems for each system type (ex. determine number of heating systems)
        self.data = lattice.load(file)
        self.number_of_systems = {}
        for system_type in self.system_types:
            self.number_of_systems[system_type] = len(self.data["rated_home_output"][f"{system_type}_system_output"])

        # initialize energy use for each fuel type and home type to calculate co2e emissions
        # TODO: there will be several layers to the data cashe
        # TODO: loop through home type and fuel type to initialize data cashe dictionary
        # TODO: start with loads, and then afterwards we can add other items to the cashe

        self.data_cashe = {}

        for home_type in self.home_types:
            for energy_type in self.energy_types:
                if energy_type == 'ELECTRICITY':
                    self.data_cashe[(energy_type,home_type)] = [0]*self.NUMBER_OF_TIMESTEPS
                else:
                    self.data_cashe[(energy_type,home_type)] = 0

        self.emissions = {'rated_home':0,
                          'co2_reference_home':0
                          }

    def get_system_energy_efficiency_coefficient(self,home_type,system_type,system_index):
        # EEC_x for rated home
        # EEC_r for reference home
        # Retrieve energy efficiency coefficient for each system type and sub-system type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['equipment_efficiency_coefficient']

    def get_system_fuel_type(self,home_type,system_type,system_index):
        # Retrieve fuel type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['primary_fuel_type']


    def get_system_fuel_type_co2(self,home_type,system_type,system_index):
        # Retrieve fuel type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['energy_use']

    def get_system_energy_consumption(self,home_type,system_type,system_index):
        # EC_x for rated home
        # EC_r for reference home
        # Retrieve energy consumption for each system type and sub-system type
        energy_consumption = 0
        for energy_use in self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['energy_use']:
            energy_consumption += sum(energy_use['energy'])

        return energy_consumption

    def calculate_normalized_energy_consumption(self,system_type,system_index):
        # nEC_x = EC_x * (a * EEC_x - b) * (EEC_r/EEC_x)
        # Retrieve energy consumption for each sub system and normalize the energy consumption
        # with the proper energy coefficients, 'a' and 'b'
        EC_x = self.get_system_energy_consumption('rated_home',system_type,system_index)
        EEC_x = self.get_system_energy_efficiency_coefficient('rated_home',system_type,system_index)
        EEC_r = self.get_system_energy_efficiency_coefficient('hers_reference_home',system_type,system_index)
        fuel_type = self.get_system_fuel_type('rated_home',system_type,system_index)
        if fuel_type in self.fossil_fuel_types:
            fuel_type = "FOSSIL_FUEL"
        a = self.fuel_coefficients[(system_type,fuel_type)]['a']
        b = self.fuel_coefficients[(system_type,fuel_type)]['b']

        return EC_x * (a * EEC_x - b) * (EEC_r/EEC_x)

    def calculate_system_loads(self,home_type,system_type,system_index):
        # TODO: change name to get_system...
        # TODO: if new calculation --> store, if already calculated --> retrieve
        # REUL
        return sum(self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['load'])

    def calculate_normalized_modified_load(self,system_type,system_index):
        # nMEUL  = REUL * nEC_x / EC_r
        REUL = self.calculate_system_loads('hers_reference_home',system_type,system_index)
        nEC_x = self.calculate_normalized_energy_consumption(system_type,system_index)
        EC_r = self.get_system_energy_consumption('hers_reference_home',system_type,system_index)

        return REUL * nEC_x / EC_r

    def calculate_other_end_use_system_energy_types(self,home_type,other_end_use):
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

    def calculate_other_end_use_energy_consumption(self,home_type):
        # EC for lighting and appliances, ventilation, and dehumidification
        # REC for lighting and appliances, ventilation, and dehumidification

        end_use_total = 0

        for other_end_use in self.other_end_uses:
            end_use_total += self.calculate_other_end_use_system_energy_types(home_type,other_end_use)

        return end_use_total

    def calculate_total_normalized_modified_load(self):
        # TnML = nMEUL_HEAT + nMEUL_COOL + nMEUL_HW + EC_LA + EC_VENT + EC_DH

        # Calculate total normalized rated home loads for heating (nMEUL_HEAT), cooling (nMEUL_COOL), and hot water (nMEUL_HW)
        nMEUL_total = 0
        for system_type in self.system_types:
            for system_index in range(self.number_of_systems[system_type]):
                nMEUL_total += self.calculate_normalized_modified_load(system_type,system_index)

        # Calculate rated home other end use energy consumption (lighting and appliances (EC_LA),
        # ventilation (EC_VENT), and dehumidification (EC_DH))
        EC_end_use_total = self.calculate_other_end_use_energy_consumption('rated_home')

        return nMEUL_total + EC_end_use_total

    def calculate_total_reference_home_load(self):
        # TRL = REUL_HEAT + REUL_COOL + REUL_HW + REC_LA + REC_VENT + REC_DH

        # Calculate total reference home loads for heating (REUL_HEAT), cooling (REUL_COOL), and hot water (REUL_HW)
        REUL_total = 0
        for system_type in self.system_types:
            for system_index in range(self.number_of_systems[system_type]):
                REUL_total += self.calculate_system_loads('hers_reference_home',system_type,system_index)

        # Calculate reference home other end use energy consumption (lighting and appliances (REC_LA),
        # ventilation (REC_VENT), and dehumidification (REC_DH))
        REC_system_total = self.calculate_other_end_use_energy_consumption('hers_reference_home')

        return REUL_total + REC_system_total

    def calculate_energy_type_total_energy(self,energy_use,home_type):
        # add annual energy use by fuel type for each system to data_cashe dictionary
        # data_cashe will be used to sum energy use by fuel type for rated home and co2 reference home and calculate annual co2e emissions

        fuel_type = energy_use["fuel_type"]
        energy = energy_use["energy"]

        if fuel_type == 'ELECTRICITY':
            self.data_cashe[(fuel_type,home_type)] = element_add(self.data_cashe[(fuel_type,home_type)], energy)
        else:
            self.data_cashe[(fuel_type,home_type)] += sum(energy)

    def multiply_energy_use_and_emission_factors(self):
        # multiply co2e emission factors with each fuel type and home type, and then find annual co2e emissions for each home type

        for key in self.data_cashe.keys():
            fuel_type = key[0]
            home_type = key[1]
            if home_type != 'hers_reference_home':
                if fuel_type == "ELECTRICITY":
                    # conversion of electricity co2e lb/kWh to lb/kbtu is included in calculation below
                    self.emissions[home_type] += convert(sum(element_product(self.data["electricity_co2_emissions_factors"],self.data_cashe[(fuel_type,home_type)])), "lb/kWh", "lb/kBtu")
                else:
                    self.emissions[home_type] += self.data_cashe[(fuel_type,home_type)]*self.fuel_emission_factors[fuel_type]

    def calculate_annual_hourly_co2_emissions(self):
        # retrieve energy use for each subsystem and multiply energy by emissions factors

        for home_type in ['rated_home','co2_reference_home']:
            for system_type in self.data[f"{home_type}_output"]:
                if system_type in self.system_types_system_output:
                    for system_index in range(len(self.data[f"{home_type}_output"][system_type])):
                        for energy_use in self.data[f"{home_type}_output"][system_type][system_index]["energy_use"]:
                            self.calculate_energy_type_total_energy(energy_use,home_type)
                elif system_type in self.other_end_uses_energy:
                    for energy_use in self.data[f"{home_type}_output"][system_type]:
                        self.calculate_energy_type_total_energy(energy_use,home_type)

        self.multiply_energy_use_and_emission_factors()

    def calculate_hers_index(self):
        # ERI = TnML / TRL * 100

        TnML = self.calculate_total_normalized_modified_load()

        TRL = self.calculate_total_reference_home_load()

        return TnML / TRL * 100

    def calculate_carbon_index(self):
        # CO2 Index = ACO2 / ARCO2 * 100

        self.calculate_annual_hourly_co2_emissions()
        ACO2 = self.emissions["rated_home"]
        ARCO2 = self.emissions["co2_reference_home"]

        return ACO2 / ARCO2 * 100

    def check_index_mismatch(self, index_name, calculated_index, output_index):
        difference = calculated_index - output_index
        if abs(difference) > self.INDEX_TOLERANCE:
            raise Exception(f"Calculated {index_name} {calculated_index:.2f} differs from output {index_name} {output_index:.2f} by {difference:.4f}, which is more than {self.INDEX_TOLERANCE:.4f}.")

    def verify_hers_index(self):
        self.check_index_mismatch("HERS Index", self.calculate_hers_index(), self.data['hers_index'])

    def verify_carbon_index(self):
        self.check_index_mismatch("Carbon Index", self.calculate_carbon_index(), self.data['carbon_index'])

    def verify(self):
        self.verify_hers_index()
        self.verify_carbon_index()


# REUL calculation is repeated. This could be simplified by caching data in a dictionary.
