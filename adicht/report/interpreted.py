# coding: utf-8

from adicht.data import ADichtMatlabFile
from adicht.display import display_markdown, display_channels, display_markers


def generate_report(data_file_path):
    data_file = ADichtMatlabFile(data_file_path)

    display_markdown('# Interpreted Data Report\nData file: %s' % data_file_path)

    report_channel_data(data_file)
    report_markers(data_file)


def report_channel_data(data_file):
    display_markdown('## Channel data')
    display_channels(data_file)


def report_markers(data_file):
    display_markdown('## Markers')
    display_markers(data_file)
