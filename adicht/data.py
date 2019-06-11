# coding: utf-8

from enum import Enum
from collections import defaultdict

from scipy.io import loadmat
from numpy import array, stack


class MarkerType(Enum):
    USER = 1
    EVENT = 2


class Marker(object):
    """This class represents a marker (or comment in the the adicht wording)."""

    def __init__(self, channel, block, position, marker_type, text, tickrate=1):
        self._channel = channel
        self._block = block
        self._position = position
        self._type = MarkerType(marker_type)
        self._text = text
        self._tickrate = tickrate
        
        self._timed_position = None
        
        self._generate_time_information()
    
    @property
    def channel(self):
        """Read only access to the channel the marker was set to."""
        return self._channel
    
    @property
    def block(self):
        """Read only access to the block the marker was set to."""
        return self._block
    
    @property
    def position(self):
        """Read only access to the position the marker was set to."""
        return self._position
    
    @property
    def type(self):
        """Read only access to the marker type."""
        return self._type
    
    @property
    def text(self):
        """Read only access to the marker's text."""
        return self._text
    
    @property
    def timed_position(self):
        """Read only access to the marker time defined by position and tick rate."""
        return self._timed_position
    
    def _generate_time_information(self):
        self._timed_position = self.position / self._tickrate

    
class Channel(object):
    """This class represents a single channel."""
    
    def __init__(self, data, rangemin, rangemax, samplerate, title, unit, offset, markers=None):
        self._data = data
        self._rangemin = rangemin
        self._rangemax = rangemax
        self._samplerate = samplerate
        self._title = title
        self._unit = unit
        self._offset = offset
        self._markers = markers or []
        
        self._times = None
        self._timed_data = None
        
        self._generate_time_information()
    
    @property
    def data(self):
        """Read only access to the channel data."""
        return self._data
    
    @property
    def rangemin(self):
        """Read only access to the channel's range minimum."""
        return self._rangemin
    
    @property
    def rangemax(self):
        """Read only access to the channel's range maximum."""
        return self._rangemax
    
    @property
    def samplerate(self):
        """Read only access to the channel's sampling rate."""
        return self._samplerate
    
    @property
    def title(self):
        """Read only access to the channel's title/name."""
        return self._title
    
    @property
    def unit(self):
        """Read only access to the channel data's unit."""
        return self._unit
    
    @property
    def offset(self):
        """Read only access to the offset of the first sample (for timing calculations)."""
        return self._offset
    
    @property
    def times(self):
        """Read only access to the calculated times of the data points."""
        return self._times
    
    @property
    def timed_data(self):
        """Read only access to a 2D array representing the data with a time axis."""
        return self._timed_data
    
    @property
    def markers(self):
        """Read only access to the markers that were set on the channel."""
        return self._markers
    
    def get_marker_value(self, marker):
        return self.data[marker.position]
    
    def _generate_time_information(self):
        time_offset = self.offset / self.samplerate
        
        # generate the time for every data point
        self._times =  array([
            time_offset + i / self.samplerate
            for i in range(len(self.data))
        ])
        
        # combine times with data points
        self._timed_data = stack((self.data, self.times))


class ADichtMatlabFile(object):
    def __init__(self, filename):
        self._content = loadmat(filename)
        self._metadata = self._extract_metadata()
        self._markers = self._extract_markers()
        self._channels = self._extract_channels()

    @property
    def raw_content(self):
        return self._content

    @property
    def metadata(self):
        return self._metadata
    
    @property
    def channels(self):
        return self._channels
    
    @property
    def markers(self):
        return self._markers
    
    def get_marker_value(self, marker_spec):
        return self.channels[marker_spec['channel']]['data'][marker_spec['offset']]

    def _extract_metadata(self):
        return {
            'tickrate': self._content['tickrate'][0][0],
            'blocktimes': self._content['blocktimes'][0][0],
        }
    
    def _extract_channels(self):
        result = []
        
        markers = defaultdict(list)
        
        for entry in self.markers:
            markers[entry.channel].append(entry)
        
        for channel_number, title in enumerate(self._content['titles']):
            data_start = int(self._content['datastart'][channel_number][0]) - 1
            data_end = int(self._content['dataend'][channel_number][0]) - 1
            
            result.append(Channel(
                data=self._content['data'][0][data_start:data_end],
                rangemin=float(self._content['rangemin'][channel_number][0]),
                rangemax=float(self._content['rangemax'][channel_number][0]),
                samplerate=float(self._content['samplerate'][channel_number][0]),
                title=title.strip(),
                unit=self._content['unittext'][int(
                    self._content['unittextmap'][channel_number][0]) - 1].strip(),
                offset=float(self._content['firstsampleoffset'][channel_number][0]),
                markers=markers[channel_number]
            ))
        
        return result
    
    def _extract_markers(self):
        # -1 for all indices as adicht uses 1 based arrays
        return [Marker(
            channel=int(spec[0]) - 1,
            block=int(spec[1]) - 1,
            position=int(spec[2]) - 1,
            marker_type=int(spec[3]),
            text=self._content['comtext'][int(spec[4]) - 1].strip(),
            tickrate=self.metadata['tickrate']
        ) for spec in self._content['com']]
    