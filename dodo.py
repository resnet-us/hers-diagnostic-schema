"""
doit task/build automation
"""

import os
from pathlib import Path
from shutil import rmtree
from typing import Dict

from lattice import Lattice  # type: ignore
import pandas as pd

from hers_diagnostic_output import HERSDiagnosticData

data_model = Lattice()

DIRECTORY_PATH = Path("build")


def task_generate_web_docs():
    """Generates Markdown Documentation"""
    return {
        "file_dep": [schema.path for schema in data_model.schemas]
        + [template.path for template in data_model.doc_templates],
        "targets": [os.path.join(data_model.web_docs_directory_path, "public")],
        "actions": [(data_model.generate_web_documentation, [])],
    }


def task_run_hers_diagnostics():
    """Initialize HERSDiagnosticData objects using all files in example directory and append to list."""

    def task_create_directory(directory_path: Path):
        if directory_path.exists():
            rmtree(directory_path)
        directory_path.mkdir(exist_ok=True)

    def task_calculate_hers_index(hers_diagnostic_data: HERSDiagnosticData):
        """Calculates HERS Index"""
        hers_diagnostic_data.verify()

    def task_get_hers_index_intermediaries(
        hers_diagnostic_data: HERSDiagnosticData,
    ) -> Dict[str, float]:
        return hers_diagnostic_data.get_hers_index_intermediaries()

    def task_save_dataframe(intermediaries: Dict[str, float], file_name: str):
        file_path = Path(DIRECTORY_PATH, f"{file_name}.csv")
        pd.DataFrame(intermediaries).to_csv(file_path)

    def task_get_file_stem(example_file: Path):
        return example_file.stem

    task_create_directory(DIRECTORY_PATH)

    for example_file in data_model.examples:
        hers_diagnostic_data = HERSDiagnosticData(example_file)
        task_calculate_hers_index(hers_diagnostic_data)
        task_save_dataframe(
            task_get_hers_index_intermediaries(hers_diagnostic_data),
            task_get_file_stem(example_file),
        )
