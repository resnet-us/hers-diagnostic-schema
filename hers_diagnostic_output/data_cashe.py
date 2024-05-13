import lattice
import numpy as np
import yaml

class DataCashe:

    home_types = ['rated_home','hers_reference_home','co2_reference_home']
    system_types = ['space_heating','space_cooling','water_heating']
    other_end_uses = ['lighting_and_appliance','ventilation','dehumidification']

    def __init__(self, file):
        # load data
        # determine number of sub-systems for each system type (ex. determine number of heating systems)
        self.data = lattice.load(file)

    def convert_tuple_to_str(self,data):
        if isinstance(data, dict):
            return {str(k): self.convert_tuple_to_str(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_tuple_to_str(item) for item in data]
        elif isinstance(data, tuple):
            return str(data)
        else:
            return data
    
    def cashe_data(self):

        energy_system_data = {}

        for home_type in self.home_types:
            energy_system_data[home_type] = {}
            for system_type_output in self.data[f"{home_type}_output"]:
                system_type = system_type_output.replace("_system_output","",1)
                if system_type in self.system_types:
                    energy_system_data[home_type][system_type] = {}
                    energy_system_data[home_type][system_type]['annual_system_energy_use'] = 0
                    # energy_system_data[home_type][system_type]['hourly_system_energy_use'] = [0] * 8760
                    for system_index in range(len(self.data[f"{home_type}_output"][system_type_output])):
                        energy_system_data[home_type][system_type]['primary_fuel_type'] = self.data[f"{home_type}_output"][system_type_output][system_index]['primary_fuel_type']
                        energy_system_data[home_type][system_type]['equipment_efficiency_coefficient'] = self.data[f"{home_type}_output"][system_type_output][system_index]['equipment_efficiency_coefficient']
                        for sub_system_number, sub_system  in enumerate(self.data[f"{home_type}_output"][system_type_output][system_index]["energy_use"]):
                            
                            tuple = (f"system_index: {system_index}",f"sub_system_index: {sub_system_number}")

                            energy_system_data[home_type][system_type][tuple] = {}

                            energy_system_data[home_type][system_type][tuple]["fuel_type"] = sub_system["fuel_type"]

                            energy_system_data[home_type][system_type][tuple]["annual_energy_use"] = sum(sub_system["energy"])
                            energy_system_data[home_type][system_type]['annual_system_energy_use'] += energy_system_data[home_type][system_type][tuple]["annual_energy_use"]
                
                            # energy_system_data[home_type][system_type][tuple]["hourly_energy_use"] = sub_system["energy"]
                            # energy_system_data[home_type][system_type]['hourly_system_energy_use'] += sub_system["energy"]                 

                elif system_type.strip("_energy") in self.other_end_uses:
                    pass
        print(energy_system_data)


        # Convert tuple keys to strings
        # converted_data = self.convert_tuple_to_str(energy_system_data)

        # Save dictionary as a YAML file
        with open('energy_system_data.yaml', 'w') as file:
            yaml.dump(energy_system_data, file)
        
