# -*- coding: utf-8 -*-

import os

from jinja2 import Template
import nbformat

from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter, PDFExporter, NotebookExporter

import adicht

SRC_DIR = os.path.join(os.path.dirname(adicht.__file__), '..')

def generate_reports(data_file, output_dir):
    pass

class Reporter(object):
    OUTPUT_DIRS = ['raw', 'interpreted', 'evaluated']
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

    def __init__(self, output_dir, log_callback=None):
        self._output_dir = output_dir
        self._templates = self._get_templates()

        self._log_callback = log_callback

    def _log(self, message):
        if self._log_callback:
            self._log_callback(message)

    def generate_report(self, data_file):
        self._log('Generate report for %s' % data_file)
        self._generate_notebooks(data_file)
        self._log('Report for %s finished!' % data_file)

    def _generate_notebooks(self, data_file):
        target_dir = self._get_target_directory(data_file)

        for template, template_sub_dir in self._templates:
            template_target_dir = os.path.join(target_dir , template_sub_dir)
            os.makedirs(template_target_dir, exist_ok=True)

            with open(template, 'r') as f:
                template_content = f.read()

            output_file = os.path.join(template_target_dir, os.path.basename(template))
            with open(output_file, 'w') as f:
                self._log('Generate notebook %s' % output_file)
                f.write(Template(template_content).render(data_file_path=data_file))

            noteook = Notebook(output_file, self._log)
            self._log('Execute notebook %s' % output_file)
            noteook.execute()
            self._log('Export notebook %s' % output_file)
            noteook.export()

    def _get_target_directory(self, data_file):
        return os.path.join(self._output_dir, os.path.splitext(os.path.basename(data_file))[0])

    def _get_templates(self):
        return [
            (os.path.join(self.TEMPLATE_DIR, entry), os.path.splitext(entry)[0])
            for entry in os.listdir(self.TEMPLATE_DIR) if entry.endswith('ipynb')
        ]


class Notebook(object):
    def __init__(self, notebook_path, log_callback):
        self._path = notebook_path
        self._content = self._load()
        self._log_callback = log_callback

    def execute(self):
        proc = ExecutePreprocessor()
        proc.preprocess(self._content, {'metadata': {'path': SRC_DIR}})

    def export(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.dirname(self._path)

        file_base = os.path.join(output_dir, os.path.basename(self._path.rpartition('.')[0]))

        for ext, func in self.exports.items():
            self._log('Export %s' % ext)
            with open('%s%s' % (file_base, ext), 'w') as f:
                f.write(str(func(self)))

    def to_notebook(self):
        return NotebookExporter().from_notebook_node(self._content)[0]

    def to_html(self):
        return HTMLExporter().from_notebook_node(self._content)[0]

    def to_pdf(self):
        return PDFExporter().from_notebook_node(self._content)[0]

    def _load(self):
        with open(self._path, 'r') as f:
            return nbformat.read(f, as_version=4)

    def _log(self, message):
        if self._log_callback:
            self._log_callback(message)

    exports = {
        '.ipynb': to_notebook,
        '.html': to_html,
        #'.pdf': to_pdf,
    }