# -*- coding: utf-8 -*-
'''
Classes that store the gaze data and can be fed to analysis functions.
'''
from .validation import has_keys, is_list_of_strings, is_real
from .settings import min_event_slice_overlap_seconds as min_overlap
from deepdiff import DeepDiff
from bisect import bisect_left  # binary tree search tool
from jsonschema import validate as validate_jsonschema


class CommonV1(object):

    class MissingTimelineException(Exception):
        pass

    class InvalidTimelineException(Exception):
        pass

    class InvalidStreamException(Exception):
        pass

    class InvalidEventException(Exception):
        pass

    # JSON Schema to validate raw input
    SCHEMA = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'title': 'gazelib/common/v1',
        'type': 'object',
        'properties': {
            'schema': {
                'type': 'string',
                'pattern': 'gazelib/common/v1'
            },
            'global_posix_time': {
                'type': 'number'
            },
            'environment': {
                'type': 'object',
                'patternProperties': {
                    '.+': {}
                }
            },
            'timelines': {
                'type': 'object',
                'patternProperties': {
                    '.+': {
                        'type': 'array',
                        'items': {
                            'type': 'number'
                        }
                    }
                }
            },
            'streams': {
                'type': 'object',
                'patternProperties': {
                    '.+': {
                        'type': 'object',
                        'properties': {
                            'timeline': {
                                'type': 'string'
                            },
                            'values': {
                                'type': 'array'
                            },
                            'confidence': {
                                'type': 'array',
                                'items': {
                                    'type': 'number',
                                    'maximum': 1.0,
                                    'minimum': 0.0
                                }
                            }
                        },
                        'required': ['timeline', 'values']
                    }
                }
            },
            'events': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'tags': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        },
                        'range': {
                            'type': 'array',
                            'items': {
                                'type': 'number'
                            }
                        },
                        'extra': {}
                    },
                    'required': ['tags', 'range']
                }
            }
        },
        'required': ['schema', 'global_posix_time', 'environment',
                     'timelines', 'streams', 'events']
    }

    @staticmethod
    def validate(raw_common):
        '''
        Raises ValidationError if raw_common is not valid gazelib/common/v1
        '''
        validate_jsonschema(raw_common, CommonV1.SCHEMA)


    def __init__(self, raw_common):

        CommonV1.validate(raw_common)
        self.raw = raw_common

    def __eq__(self, other):
        '''
        Override '==' operator
        '''
        return DeepDiff(self.raw, other.raw) == {}

    # Accessors

    def convert_to_global_time(self, relative_time_seconds):
        if relative_time_seconds is None:
            return None
        gt = self.raw['global_posix_time']
        return gt + relative_time_seconds

    def convert_to_relative_time(self, global_time_seconds):
        if global_time_seconds is None:
            return None
        gt = self.raw['global_posix_time']
        return global_time_seconds - gt

    def get_environment(self, env_name):
        return self.raw['environment'][env_name]

    def get_global_time(self):
        return self.raw['global_posix_time']

    def iter_environment_names(self):
        return self.raw['environment'].keys()

    def iter_stream_names(self):
        return self.raw['streams'].keys()

    def iter_events_by_tag(self, tag):
        '''
        Yields events with the tag.
        '''
        for event in self.raw['events']:
            if tag in event['tags']:
                yield event

    def slice_by_relative_time(self, rel_start_time, rel_end_time=None):
        '''
        Return new CommonV1 object with data only in the time range.
        Does not update global_posix_time because easier implementation.
        '''

        # The new copy
        slice_raw = {
            'schema': self.raw['schema'],
            'global_posix_time': self.raw['global_posix_time'],
            'environment': self.raw['environment'],  # shallow copy!
            'timelines': {},
            'streams': {},
            'events': []
        }

        for stream_name, stream in self.raw['streams'].items():

            # Find indices from the original timeline
            tl_name = stream['timeline']
            tl = self.raw['timelines'][tl_name]
            first_i = bisect_left(tl, rel_start_time)  # first in range
            if rel_end_time is None:
                end_i = None
            else:
                end_i = bisect_left(tl, rel_end_time)  # first after range
            # https://docs.python.org/3/library/bisect.html

            # Slice timeline and substreams
            # (TODO ensure that timeline slice is done only once)
            if end_i is None:
                sub_timeline = tl[first_i:]
                sub_values = stream['values'][first_i:]
                if 'confidence' in stream:
                    sub_confidence = stream['confidence'][first_i:]
            else:
                sub_timeline = tl[first_i:end_i]
                sub_values = stream['values'][first_i:end_i]  # incl-excl
                if 'confidence' in stream:
                    sub_confidence = stream['confidence'][first_i:end_i]

            # Include stream to the slice if not empty.
            if len(sub_values) > 0:
                slice_raw['timelines'][tl_name] = sub_timeline

                substream = {}
                substream['timeline'] = tl_name
                substream['values'] = sub_values
                # Include confidencies only if they exist beforehand
                if 'confidence' in stream:
                    substream['confidence'] = sub_confidence
                slice_raw['streams'][stream_name] = substream

        # Result:
        #   only needed timelines are included
        #   timelines, values, and confidencies are cut
        #   empty timelines are not included

        # Keep events that overlap with the time range.
        for event in self.raw['events']:
            ev_start = event['range'][0]
            ev_end = event['range'][1]

            # Due to rounding errors, let us not include events that only
            # slightly overlap with the range.
            if rel_end_time is None:
                limit_start = rel_start_time + min_overlap
                if limit_start < ev_end:
                    slice_raw['events'].append(event)
            else:
                limit_end = rel_end_time - min_overlap
                limit_start = rel_start_time + min_overlap
                if ev_start < limit_end and limit_start < ev_end:
                    slice_raw['events'].append(event)

        return CommonV1(slice_raw)

    def slice_by_global_time(self, start_time, end_time=None):
        '''
        Return new CommonV1 object with data only in the time range.
            Updates the global_posix_time to start_time
                to minimize representation size.
        '''
        r_start = self.convert_to_relative_time(start_time)
        r_end = self.convert_to_relative_time(end_time)

        return self.slice_by_relative_time(r_start, r_end)

    def slice_by_timeline(self, timeline_name, start_index, end_index=None):
        '''
        Return new CommonV1 object with data only in the time range specified
        by the indices of the timeline.

        Parameters
            timeline_name
            start_index: inclusive
            end_index: optional, exclusive, first element to not be included.
                If None given, slice to the end.

        '''
        timelines = self.raw['timelines']

        # Ensure timeline exists
        if timeline_name not in timelines:
            str_tl = str(timeline_name)
            raise CommonV1.MissingTimelineException('Timeline ' + str_tl +
                                                    ' not found.')
        timeline = timelines[timeline_name]

        # Limit indices
        last_index = len(timeline) - 1
        start_index = min(last_index, max(0, start_index))
        if end_index is not None:
            if end_index > last_index:
                end_index = None
            else:
                # Limit to zero or positive
                end_index = max(0, end_index)

        rel_start_time = timeline[start_index]
        if end_index is None:
            rel_end_time = None
        else:
            rel_end_time = timeline[end_index]

        return self.slice_by_relative_time(rel_start_time, rel_end_time)

    def slice_by_tag(self, tag, index=0):
        '''
        Parameters
            tag
            index

        Return
            CommonV1 instance
                that has data only during the tagged event.
            None
                if no such tag found
        '''
        # Select event of the index:th tag
        target_event = None
        i = 0
        for event in self.raw['events']:
            if tag in event['tags']:
                if index == i:
                    target_event = event
                    break
                i += 1

        if target_event is None:
            return None

        range_start = target_event['range'][0]
        range_end = target_event['range'][1]

        return self.slice_by_relative_time(range_start, range_end)

    def iter_slices_by_tag(self, tag, limit_to=None):
        '''
        Slice to multiple portions. E.g. if there is ten events with "trial"
        tag, returns iterable over ten slices, one for each tag.

        Parameters
            tag
                string
            limit_to
                max number of slices to return. By default returns all.

        Return
            iterable of CommonV1 objects
        '''

        for index, event in enumerate(self.iter_events_by_tag(tag)):
            range_start = event['range'][0]
            range_end = event['range'][1]
            yield self.slice_by_relative_time(range_start, range_end)
            if limit_to is not None:
                if index + 2 > limit_to:
                    break

    # Mutators

    def add_environment(self, env_name, env_value):
        # TODO raise error if invalid
        self.raw['environment'][env_name] = env_value

    def add_stream(self, stream_name, timeline_name, values, confidence=None):
        if timeline_name not in self.raw['timelines']:
            raise CommonV1.MissingTimelineException(
                'Timeline ' + timeline_name + ' not found.')
        if type(stream_name) is not str:
            raise CommonV1.InvalidStreamException()
        if type(values) is not list:
            raise CommonV1.InvalidStreamException('Values must be a list.')
        if len(values) != len(self.raw['timelines'][timeline_name]):
            raise CommonV1.InvalidStreamException(
                'Stream and timeline must have equal length.')
        if confidence is not None and type(confidence) is not list:
            raise CommonV1.InvalidStreamException(
                'Confidence must be a list or None')

        new_stream = {
            'timeline': timeline_name,
            'values': values,
        }
        if confidence is not None:
            new_stream['confidence'] = confidence

        self.raw['streams'][stream_name] = new_stream

    def add_timeline(self, timeline_name, timeline_values):
        if type(timeline_name) is str and type(timeline_values) is list:
            self.raw['timelines'][timeline_name] = timeline_values
        else:
            raise CommonV1.InvalidTimelineException()

    def add_event(self, tags, start_time, end_time, extra=None):
        if not is_list_of_strings(tags):
            raise CommonV1.InvalidEventException('Invalid tag list')
        if (not is_real(start_time)) or (not is_real(end_time)):
            raise CommonV1.InvalidEventException('Invalid range')
        new_event = {
            'tags': tags,
            'range': [start_time, end_time],
        }
        if extra is not None:
            new_event['extra'] = extra

        self.raw['events'].append(new_event)

    def set_global_time(self, seconds_from_epoch):
        '''
        Can be used to anonymize data.
        '''
        # TODO validate
        self.raw['global_posix_time'] = seconds_from_epoch
