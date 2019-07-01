# coding: utf-8

import random

COLORS = [
    '#0000cc',
    '#0033cc',
    '#0066cc',
    '#0099cc',
    '#00cccc',
    '#00ffcc',
    '#3300cc',
    '#3333cc',
    '#3366cc',
    '#3399cc',
    '#33cccc',
    '#33ffcc',
    '#6600cc',
    '#6633cc',
    '#6666cc',
    '#6699cc',
    '#66cccc',
    '#66ffcc',
    '#9900cc',
    '#9933cc',
    '#9966cc',
    '#9999cc',
    '#99cccc',
    '#99ffcc',
    '#cc00cc',
    '#cc33cc',
    '#cc66cc',
    '#cc99cc',
    '#cccccc',
    '#ccffcc',
]

def get_random_color(already_used_ones=None):
    if already_used_ones is None:
        already_used_ones = []

    return random.choice(COLORS)