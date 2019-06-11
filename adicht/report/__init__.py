# -*- coding: utf-8 -*-

import os

from jinja2 import Template
import nbformat
from nbconvert import HTMLExporter, PDFExporter

def generate_reports(data_file, output_dir):
    pass

class Reporter(object):
    OUTPUT_DIRS = ['raw', 'interpreted', 'evaluated']
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

    def __init__(self, output_dir):
        self._output_dir = output_dir
        self._templates = self._get_templates()

    def generate_report(self, data_file):
        self._generate_notebooks(data_file)

    def _generate_notebooks(self, data_file):
        target_dir = self._get_target_directory(data_file)

        for template, template_sub_dir in self._templates:
            template_target_dir = os.path.join(target_dir , template_sub_dir)
            os.makedirs(template_target_dir, exist_ok=True)

            output_file = os.path.join(template_target_dir, os.path.basename(template))
            with open(output_file, 'w') as f:
                f.write(Template(template).render(data_file_path=data_file))

    def _get_target_directory(self, data_file):
        return os.path.join(self._output_dir, os.path.splitext(os.path.basename(data_file))[0])

    def _get_templates(self):
        return [
            (os.path.join(self.TEMPLATE_DIR, entry), os.path.splitext(entry)[0])
            for entry in os.listdir(self.TEMPLATE_DIR) if entry.endswith('ipynb')
        ]


class Notebook(object):
    def __init__(self, notebook_path):
        self._path = notebook_path
        self._content = self._load()

    def to_html(self):
        return HTMLExporter().from_notebook_node(self._content)[0]

    def to_pdf(self):
        return PDFExporter().from_notebook_node(self._content)[0]

    def _load(self):
        with open(self._path, 'r') as f:
            return nbformat.reads(f.read())