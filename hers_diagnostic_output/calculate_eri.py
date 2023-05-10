from hers_diagnostic_output import HERSDiagnosticData

# file_path = "examples/baltimore-multiclimate-base-case.json"
file_path = "examples/HERS_Diagnostic.json"
data = HERSDiagnosticData(file_path)
eri = data.calculate_eri()
print(eri)