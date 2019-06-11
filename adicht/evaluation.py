# coding: utf-8

import re

import numpy
from scipy.integrate import simps


MARKER_PATTERNS = [
        re.compile(entry)
        for entry in ['el. stim.*', '(.*?)ser(.*)', '(.*?)ser(.*)']
        ]

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
        
        from_timed_pos = numpy.where(channel.timed_data[1] == from_marker.timed_position)[0][0]
        to_timed_pos = numpy.where(channel.timed_data[1] == to_marker.timed_position)[0][0]
        
        data = channel.timed_data[..., from_timed_pos:to_timed_pos]
        data = numpy.stack((data[0], data[1] - data[1][0]))
        
        result.append({
                'from_marker': from_marker,
                'to_marker': to_marker,
                'data': data
                })
    
    return result

def get_evaluated_stimulations(channel):
    stimulations = extract_stimulations(channel)
    
    for entry in stimulations:
        max_val_index = numpy.argmax(entry['data'][0])
        entry['max_value'] = entry['data'][..., max_val_index]
        entry['duration'] = entry['to_marker'].timed_position \
            - entry['from_marker'].timed_position
        entry['full_answer_integrated'] = simps(
                entry['data'][0], entry['data'][1])
    
    return stimulations