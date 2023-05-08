import lattice

class HERSDiagnosticData:

    fuel_coefficients = {("space_heating","ELECTRICITY"):{"a":2.2561,"b":0},
                         ("space_heating","FOSSIL_FUEL"):{"a":1.0943,"b":0.403},
                         ("space_heating","BIOMASS"):{"a":0.885,"b":0.4047},
                         ("space_cooling","ELECTRICITY"):{"a":3.809,"b":0},
                         ("water_heating","ELECTRICITY"):{"a":0.92,"b":0},
                         ("water_heating","FOSSIL_FUEL"):{"a":1.1877,"b":1.013}}

    def __init__(self, file):
        self.data = lattice.load(file)
        system_types = ['space_heating','space_cooling','water_heating']
        self.number_of_systems = {}
        for system_type in system_types:
            self.number_of_systems[f"{system_type}"] = len(self.data["rated_home_output"][f"{system_type}_system_output"])


    def get_system_energy_efficiency_coefficient(self,home_type,system_type,system_index):
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['equipment_efficiency_coefficient']

    def get_system_fuel_type(self,home_type,system_type,system_index):
        return self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['primary_fuel_type']

    def get_system_energy_consumption(self,home_type,system_type,system_index):
        energy_consumption = 0
        for energy_use in self.data[f"{home_type}_output"][f"{system_type}_system_output"][system_index]['energy_use']:
            energy_comsumption += energy_use['energy']
        
        return energy_consumption
    
    def calculate_normalized_energy_consumption(self,system_type,system_index):
        # equation
        # EC_x * (a * EEC_x - b) * (EEC_r/EEC_x)
        EC_x = self.get_system_energy_consumption('rated_home',system_type,system_index)
        EEC_x = self.get_system_energy_efficiency_coefficient('rated_home',system_type,system_index)
        EEC_r = self.get_system_energy_efficiency_coefficient('hers_reference_home',system_type,system_index)
        fuel_type = self.get_system_fuel_type('rated_home',system_type,system_index)
        a = fuel_coefficients[(system_type,fuel_type)]

        return 


    

    def calculate_eri(self):
        # rated home outputs

     

       