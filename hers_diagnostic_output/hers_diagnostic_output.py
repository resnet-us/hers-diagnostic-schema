import lattice

class HERSDiagnosticData:

    # Define coefficients 'a' and 'b based on Table 4.1.1(1) in Standard 301 for 
    # space heating, space cooling, and water heating
    fuel_coefficients = {("space_heating","ELECTRICITY"):{"a":2.2561,"b":0},
                         ("space_heating","FOSSIL_FUEL"):{"a":1.0943,"b":0.403},
                         ("space_heating","BIOMASS"):{"a":0.885,"b":0.4047},
                         ("space_cooling","ELECTRICITY"):{"a":3.809,"b":0},
                         ("water_heating","ELECTRICITY"):{"a":0.92,"b":0},
                         ("water_heating","FOSSIL_FUEL"):{"a":1.1877,"b":1.013}}
    
    # define FOSSIL_FUEL types to allocate proper 'a' and 'b' coefficients in fuel_coefficients dictionary
    fossil_fuel_types = ['NATURAL_GAS','FUEL_OIL_2','LIQUID_PETROLEUM_GAS']
    system_types = ['space_heating','space_cooling','water_heating']
    other_end_uses = ['lighting_and_appliance','ventilation','dehumidification']

    def __init__(self, file):
        # load data
        # determine number of sub-systems for each system type (ex. determine number of heating systems)
        self.data = lattice.load(file)
        self.number_of_systems = {}
        for system_type in self.system_types:
            self.number_of_systems[f"{system_type}"] = len(self.data["rated_home_output"][f"{system_type}_system_output"])


    def get_system_energy_efficiency_coefficient(self,home_type,system_type,system_index):
        # EEC_x for rated home
        # EEC_r for reference home
        # Retrieve energy efficiency coefficient for each system type and sub-system type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['equipment_efficiency_coefficient']

    def get_system_fuel_type(self,home_type,system_type,system_index):
        # Retrieve fuel type
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['primary_fuel_type']

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
        # REUL
        return sum(self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['load'])

    def calculate_normalized_modified_load(self,system_type,system_index):
        # nMEUL  = REUL * nEC_x / EC_r
        REUL = self.calculate_system_loads('hers_reference_home',system_type,system_index)
        nEC_x = self.calculate_normalized_energy_consumption(system_type,system_index)
        EC_r = self.get_system_energy_consumption('hers_reference_home',system_type,system_index)

        return REUL * nEC_x / EC_r
    
    def calculate_other_end_use_energy_consumtpion(self,home_type):
        # EC for lighting and appliances, ventilation, and dehumidification
        # REC for lighting and appliances, ventilation, and dehumidification

        end_use_total = 0

        for other_end_use in self.other_end_uses:
            if other_end_use == 'dehumidification':
                if other_end_use in self.data:
                    end_use_total += sum(self.data[f"{home_type}_output"][f"{other_end_use}_energy"][0]["energy"])
                else:
                    pass
            else:
                end_use_total += sum(self.data[f"{home_type}_output"][f"{other_end_use}_energy"][0]["energy"])
    
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
        EC_end_use_total = self.calculate_other_end_use_energy_consumtpion('rated_home')
    
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
        REC_system_total = self.calculate_other_end_use_energy_consumtpion('hers_reference_home')
        
        return REUL_total + REC_system_total


    def calculate_eri(self):
        # rated home outputs
        # ERI = TnML / TRL
        TnML = self.calculate_total_normalized_modified_load()

        TRL = self.calculate_total_reference_home_load()

        return TnML / TRL * 100

# REUL calculation is repeated. This could be simplified by caching data in a dictionary.