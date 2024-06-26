"""
doit task/build automation
"""

import os

from lattice import Lattice

data_model = Lattice()


def task_generate_web_docs():
    """Generates Markdown Documentation"""
    return {
        "file_dep": [schema.path for schema in data_model.schemas]
        + [template.path for template in data_model.doc_templates],
        "targets": [os.path.join(data_model.web_docs_directory_path, "public")],
        "actions": [(data_model.generate_web_documentation, [])],
    }
