# coding: utf-8

import re
import copy
from enum import Enum

import numpy
from scipy.interpolate import interp1d
from scipy.integrate import simps, cumtrapz


STIMULATION_END_MARKER = 'stim ende'
INTEGRAL_END_MARKER = 'int ende'

MARKER_PATTERNS = [
        re.compile(entry)
        for entry in ['el. stim.*', '(.*?)ser(.*)', '(.*?)ser(.*)']
        ]

class IntegralReference:
    TO_START = 0
    TO_BASELINE = 1


def extract_stimulations(channel):
    delimiter_markers = [
            entry 
            for entry in channel.markers 
            if any([pattern.match(entry.text.lower())
            for pattern in MARKER_PATTERNS])
    ]
    
    result = []
    
    for i in range(len(delimiter_markers) - 1):
        from_marker = delimiter_markers[i]
        to_marker = delimiter_markers[i+1]

        contained_markers = copy.deepcopy(channel.markers[channel.markers.index(from_marker):channel.markers.index(to_marker)+1])
        for entry in contained_markers:
            entry.apply_time_offest(from_marker.timed_position)
        
        from_timed_pos = numpy.where(channel.timed_data[1] == from_marker.timed_position)[0][0]
        to_timed_pos = numpy.where(channel.timed_data[1] == to_marker.timed_position)[0][0] + 1
        
        data = channel.timed_data[..., from_timed_pos:(to_timed_pos)]
        #data[...,:] -= from_timed_pos
        data = numpy.stack((data[0], data[1] - data[1][0]))
        
        result.append({
                'from_marker': contained_markers[0],
                'to_marker': contained_markers[-1],
                'markers': contained_markers,
                'data': data
                })
    
    return result


def get_integral_end_marker(stimulation):
    return list(
        filter(lambda marker: marker.text.lower().strip() == INTEGRAL_END_MARKER, stimulation['markers'])
    ) or None


def get_stimulation_integral(stimulation, from_marker_text, to_marker_text, reference=IntegralReference.TO_START):
    from_marker = list(
        filter(lambda marker: marker.text.lower().strip() == from_marker_text.lower().strip(), stimulation['markers'])
    )
    to_marker = list(
        filter(lambda marker: marker.text.lower().strip() == to_marker_text.lower().strip(), stimulation['markers'])
    )

    if not to_marker or not from_marker:
        return None, numpy.nan

    from_pos = numpy.where(stimulation['data'][1] == from_marker[0].timed_position)[0][0]
    to_pos = numpy.where(stimulation['data'][1] == to_marker[0].timed_position)[0][0]

    integration_data = stimulation['data'][..., from_pos:to_pos]

    full_integral = simps(integration_data[0], integration_data[1])

    start = integration_data[..., from_pos]
    end = integration_data[..., to_pos - 1]

    if reference == IntegralReference.TO_BASELINE:
        x = integration_data[1]
        slope = (end[0] - start[0]) / (end[1] - start[1])
        y = slope * (x - start[1]) + start[0]

        substraction = simps(y, x)
    else:
        substraction = simps(numpy.full((1, len(integration_data[0])), start[0])[0], integration_data[1])

    return integration_data, (full_integral - substraction)


def get_evaluated_stimulations(channel):
    stimulations = extract_stimulations(channel)
    
    for entry in stimulations:
        max_val_index = numpy.argmax(entry['data'][0])
        entry['integral_end_time'] = numpy.nan
        entry['duration'] = entry['to_marker'].timed_position - entry['from_marker'].timed_position

        full_answer_data, full_answer_integrated = get_stimulation_integral(entry,
                                                                          entry['from_marker'].text,
                                                                          INTEGRAL_END_MARKER, reference=IntegralReference.TO_BASELINE)
        stimulation_answer_data, stimulation_answer_integrated = get_stimulation_integral(entry,
                                                                                        entry['from_marker'].text,
                                                                                        STIMULATION_END_MARKER)

        entry['full_answer_integrated'] = full_answer_integrated
        entry['stimulation_answer_integrated'] = stimulation_answer_integrated

        if full_answer_data is not None:
            max_val_index = numpy.argmax(full_answer_data[0])
            entry['integral_end_time'] = get_integral_end_marker(entry)[0].timed_position

        entry['max_value'] = entry['data'][..., max_val_index]

    
    return stimulations