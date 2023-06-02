from hers_diagnostic_output import HERSDiagnosticData

file_path = "examples/baltimore-multiclimate-base-case.json"
data = HERSDiagnosticData(file_path)
data.verify()
eri = data.calculate_hers_index()
co2 = data.calculate_carbon_index()
print(f"HERS Index: {eri:.2f}")
print(f"CO2 Index:  {co2:.2f}")
