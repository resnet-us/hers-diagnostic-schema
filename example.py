from pathlib import Path

from hers_diagnostic_outputs import HERSDiagnosticOutput

file_path = Path("examples", "base-pv-battery.json")

hers_diagnostic_output = HERSDiagnosticOutput(file_path)
hers_diagnostic_output.calculate_hers_index()
