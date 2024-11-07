"""
doit task/build automation
"""

import os

from lattice import Lattice
from hers_diagnostic_output.hers_diagnostic_output import HERSDiagnosticData

data_model = Lattice(build_validation=False)


def task_generate_web_docs():
    """Generates Markdown Documentation"""
    return {
        "file_dep": [schema.path for schema in data_model.schemas]
        + [template.path for template in data_model.doc_templates],
        "targets": [os.path.join(data_model.web_docs_directory_path, "public")],
        "actions": [(data_model.generate_web_documentation, [])],
    }


def task_calculate_hers_index():
    """Calculates HERS Index"""
    for example_file in data_model.examples:
        print(HERSDiagnosticData(example_file).calculate_hers_index())
