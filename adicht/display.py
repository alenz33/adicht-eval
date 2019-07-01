# coding: utf-8

from adicht.colors import COLORS, get_random_color
from adicht.evaluation import get_evaluated_stimulations, STIMULATION_END_MARKER, INTEGRAL_END_MARKER

from IPython.display import Markdown, HTML, display
from matplotlib import pyplot


def display_markdown(text):
    display(Markdown(text))


def display_html(text):
    display(HTML(text))


def display_table(table_data):
    def format_row(row_data):
        return ' | '.join(map(str, row_data))
    
    lines = [format_row(row) for row in table_data]
    lines.insert(1, format_row(['---'] * len(table_data[0])))
    
    display(Markdown('\n'.join(lines)))

    
def display_metadata(data_file):
    display(Markdown('''
| Tick rate | Block times |
| --- | --- |
| %(tickrate)f | %(blocktimes)f |
    ''' % data_file.metadata))

    
def display_channels(data_file):
    table_cols = [
        ('Range min', 'rangemin'),
        ('Range max', 'rangemax'),
        ('Unit', 'unit'),
        ('Sample rate (s)', 'samplerate'),
    ]
    
    for channel in data_file.channels:
        display(Markdown('#### %s' % channel.title))
        
        table = [[col[0] for col in table_cols]]             + [[getattr(channel, col[1]) for col in table_cols]]
        display_table(table)
        
        plot = pyplot.figure(figsize=(15, 5))
        
        pyplot.plot(channel.timed_data[1], channel.timed_data[0], label=channel.title, color='#66cc00')
        pyplot.xlabel('s')
        pyplot.ylabel(channel.unit)
        
        for index, entry in enumerate(channel.markers):
            pyplot.axvline(x=entry.timed_position, label=entry.text,
                           color=COLORS[index])
        
        legend = pyplot.legend(loc='upper right', shadow=True,
                               bbox_to_anchor=(1.3, 1.1))
        pyplot.show()

def display_markers(data_file):
    table_cols = [
        ('Channel', 'channel'),
        ('Block', 'block'),
        ('Position', 'position'),
        ('Marker type', 'type'),
        ('Text', 'text'),
    ]
    
    table = [[col[0] for col in table_cols]]         + [[getattr(marker, col[1]) for col in table_cols] for marker in data_file.markers]
    display_table(table)


def display_stimulations(data_file):
    for channel_number, channel in enumerate(data_file.channels): 
        display(Markdown('#### %s' % channel.title))
        
        for stimulation in get_evaluated_stimulations(channel):
            display(Markdown('##### %r - %r' % (stimulation['from_marker'].text, stimulation['to_marker'].text)))
            
            plot = pyplot.figure(figsize=(15, 5))
            pyplot.plot(stimulation['data'][1], stimulation['data'][0])
            
            pyplot.xlabel('s')
            pyplot.ylabel(channel.unit)
            
            pyplot.axvline(x=stimulation['max_value'][1], label='[calc] Maximum', color='red')

            used_colors = []
            for index, entry in enumerate(stimulation['markers']):
                if entry.text.lower().strip() not in (
                    stimulation['from_marker'].text.lower().strip(),
                    stimulation['to_marker'].text.lower().strip(),
                    STIMULATION_END_MARKER,
                    INTEGRAL_END_MARKER,
                ):
                    continue

                color = get_random_color(used_colors)
                pyplot.axvline(x=entry.timed_position, label=entry.text,
                               color=color)
                used_colors.append(color)
            
            legend = pyplot.legend(loc='upper right', shadow=True,
                           bbox_to_anchor=(1.3, 1.1))
                 
            pyplot.show()
            
            table = [
                [
                    'Total Duration (s)',
                    'Maximum Value (%s)' % channel.unit,
                    'Time of Maximum (s)',
                    'Time of Integral End (s)',
                    'Stimulation Answer (Integrated)',
                    'Full Answer (Integrated)',
                ],
                [
                    stimulation['duration'],
                    stimulation['max_value'][0],
                    stimulation['max_value'][1],
                    stimulation['integral_end_time'],
                    stimulation['stimulation_answer_integrated'],
                    stimulation['full_answer_integrated'],
                ]
            ]
            
            display_table(table)