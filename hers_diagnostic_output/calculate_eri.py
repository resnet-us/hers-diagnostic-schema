from hers_diagnostic_output import HERSDiagnosticData

file_path = "examples/baltimore-multiclimate-base-case.json"
data = HERSDiagnosticData(file_path)
eri = data.calculate_eri()
co2 = data.calculate_co2()
print(f"HERS Index: {eri:.2f}")
print(f"CO2 Index:  {co2:.2f}")
