# coding: utf-8

from adicht.data import ADichtMatlabFile
from adicht.display import display_table, display_markdown, display_html


def generate_report(data_file_path):
    data_file = ADichtMatlabFile(data_file_path)

    display_markdown('# Raw Data Report\nData file: %s' % data_file_path)
    display_html('<span style="font-weight:bold; color:red;">ATTENTION: Adicht/Matlab indices start at 1!</span>')

    report_block_information(data_file)
    report_unit_information(data_file)
    report_channel_information(data_file)
    report_marker_information(data_file)
    report_marker_text_information(data_file)
    #report_raw_data_stream(data_file)


def report_block_information(data_file):
    display_markdown('## Block information')
    display_table(
        [['Index', 'Time', 'Tick rate']]
        + [
            [index, time[0], tickrate[0]]
            for index, (time, tickrate) in enumerate(zip(
                data_file.raw_content['blocktimes'],
                data_file.raw_content['tickrate'],
            ))
        ]
    )


def report_unit_information(data_file):
    display_markdown('## Unit information')
    display_table(
        [['Index', 'Unit']]
        + [
            [index, unit]
            for index, unit in enumerate(
                data_file.raw_content['unittext']
            )
        ]
    )


def report_channel_information(data_file):
    display_markdown('## Channel information')
    display_table(
        [['Index', 'Title', 'Data Start', 'Data End', 'Range Min', 'Range max', 'Unit', 'Sample rate',
          'Offset Of First Sample']]
        + [
            [index, title, data_start[0], data_end[0], range_min[0], range_max[0], unit[0], samplerate[0],
             firstsampleoffset[0]]
            for index, (title, data_start, data_end, range_min, range_max, unit, samplerate, firstsampleoffset) in
            enumerate(zip(
                data_file.raw_content['titles'],
                data_file.raw_content['datastart'],
                data_file.raw_content['dataend'],
                data_file.raw_content['rangemin'],
                data_file.raw_content['rangemax'],
                data_file.raw_content['unittextmap'],
                data_file.raw_content['samplerate'],
                data_file.raw_content['firstsampleoffset']
            ))
        ]
    )


def report_marker_information(data_file):
    display_markdown('## Marker information')
    display_table(
        [['Index', 'Channel', 'Block', 'Tick Position', 'Type', 'Text']]
        + [
            ([index] + list(marker_spec))
            for index, marker_spec in enumerate(
                data_file.raw_content['com']
            )
        ]
    )


def report_marker_text_information(data_file):
    display_markdown('## Marker text information')
    display_table(
        [['Index', 'Text']]
        + [
            [index, text]
            for index, text in enumerate(
                data_file.raw_content['comtext']
            )
        ]
    )


def report_raw_data_stream(data_file):
    display_markdown('## Raw data stream')
    display_table([['Index', 'Value']] + [[index, value] for index, value in enumerate(data_file.raw_content['data'][0])])