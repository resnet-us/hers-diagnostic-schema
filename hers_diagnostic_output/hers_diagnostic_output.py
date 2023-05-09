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
    
    # define FOSSIL_FUEL types to allocate proper 'a' and 'b' coefficients in table fuel_coefficients
    fossil_fuel_types = ['NATURAL_GAS','FUEL_OIL_2','LIQUID_PETROLEUM_GAS']
    system_types = ['space_heating','space_cooling','water_heating']
    other_end_uses = ['lighting_and_appliance','ventilation','dehumidification']

    def __init__(self, file):
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
        
         
    
    ## REUL_space_heating = sum(data['hers_reference_home_output']['space_heating_system_output'][0]['load'])

    def calculate_normalized_modified_load(self,system_type,system_index):
        # nMEUL  = REUL * nEC_x / EC_r
        REUL = self.calculate_system_loads('hers_reference_home',system_type,system_index)
        nEC_x = self.calculate_normalized_energy_consumption(system_type,system_index)
        EC_r = self.get_system_energy_consumption('hers_reference_home',system_type,system_index)

        return REUL * nEC_x / EC_r
    
    def calculate_other_end_use_energy_consumtpion(self,home_type,electricity_system):
        # EC for lighting and appliances, ventilation, and dehumidification
        # REC for lighting and appliances, ventilation, and dehumidification
        return self.data[f"{home_type}_output"][f"{electricity_system}_energy"][0]["energy"]

    
    def calculate_total_normalized_modified_load(self):
        # TnML = nMEUL_HEAT + nMEUL_COOL + nMEUL_HW + EC_LA + EC_VENT + EC_DH

        nMEUL_total = 0

        for system_type in self.system_types:
            for system_index in range(self.number_of_systems[system_type]):
                nMEUL_total += self.calculate_normalized_modified_load(system_type,system_index)
        
        EC_end_use_total = 0

        for other_end_use in self.other_end_uses:
            EC_end_use_total += sum(self.calculate_other_end_use_energy_consumtpion('rated_home',other_end_use))
    
        return nMEUL_total + EC_end_use_total
    
    def calculate_total_reference_home_load(self):

        REUL_total = 0

        for system_type in self.system_types:
            for system_index in range(self.number_of_systems[system_type]):
                REUL_total += self.calculate_system_loads('hers_reference_home',system_type,system_index)

        REC_system_total = 0

        for other_end_use in self.other_end_uses:
            REC_system_total += sum(self.calculate_other_end_use_energy_consumtpion('hers_reference_home',other_end_use))
        
        return REUL_total + REC_system_total


    def calculate_eri(self):
        # rated home outputs
        # ERI = TnML / TRL
        TnML = self.calculate_total_normalized_modified_load()

        TRL = self.calculate_total_reference_home_load()

        return TnML / TRL * 100