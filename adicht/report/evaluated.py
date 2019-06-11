# coding: utf-8

from adicht.data import ADichtMatlabFile
from adicht.display import display_stimulations, display_markdown


def generate_report(data_file_path):
    data_file = ADichtMatlabFile(data_file_path)

    display_markdown('# Evaluated Data Report\nData file: %s' % data_file_path)

    report_stimulations(data_file)


def report_stimulations(data_file):
    display_markdown('## Stimulations')
    display_stimulations(data_file)
