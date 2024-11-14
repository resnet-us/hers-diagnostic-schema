"""Example HERS Index calculations of example HERS diagnostic input files."""

from pathlib import Path
from hers_diagnostic_output.hers_diagnostic_output import HERSDiagnosticData

directory_path = Path("examples")
file_paths = [file for file in directory_path.glob("*.json")]

for file_path in file_paths:
    data = HERSDiagnosticData(file_path)
    data.verify()
    eri = data.hers_index
    co2 = data.co2_index
    data.save_hers_index_intermediaries()
