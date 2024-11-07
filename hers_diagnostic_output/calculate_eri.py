from .hers_diagnostic_output import HERSDiagnosticData
from pathlib import Path

directory_path = Path("examples")
file_paths = [file for file in directory_path.iterdir()]  # add if statement

energy_systems = ["space_heating", "space_cooling", "water_heating"]
other_end_uses = ["lighting_and_appliance", "ventilation", "dehumidification"]


for file_path in file_paths:
    print(f"""\n{file_path.name.replace(".json", "")}""")
    data = HERSDiagnosticData(file_path)
    rated_home_data = data.data["rated_home_output"]
    systems = [
        system
        for system in list(rated_home_data.keys())
        if system != "conditioned_space_temperature"
    ]

    data.verify()
    eri = data.calculate_hers_index()
    co2 = data.calculate_carbon_index()
