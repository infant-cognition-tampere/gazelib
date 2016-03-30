# -*- coding: utf-8 -*-
'''
Classes that store the gaze data and can be fed to analysis functions.
'''
from .validation import is_list_of_strings, is_real
from .settings import min_event_slice_overlap_seconds as min_overlap
from .statistics import arithmetic_mean, deltas
from .io import load_json, write_json, write_fancy_json, write_dictlist_as_csv
from time import time as get_current_posix_time
from deepdiff import DeepDiff
from bisect import bisect_left  # binary tree search tool
from jsonschema import validate as validate_jsonschema


class CommonV1(object):

    class InvalidRangeException(Exception):
        '''
        Raised if invalid range index pair were given. E.g. start > end
        '''
        pass

    class MissingEnvironmentException(Exception):
        '''Raised if a environment cannot be found.'''
        pass

    class MissingTimelineException(Exception):
        '''Raised if a timeline cannot be found.'''
        pass

    class MissingStreamException(Exception):
        '''Raised if a stream cannot be found.'''
        pass

    class InvalidTimelineException(Exception):
        '''Raised if a timeline does not fit the CommonV1 specification.'''
        pass

    class InvalidStreamException(Exception):
        '''Raised if a stream does not fit the CommonV1 specification.'''
        pass

    class InvalidEventException(Exception):
        '''Raised if an event does not fit the CommonV1 specification.'''
        pass

    class InsufficientDataException(Exception):
        '''Raised if a timeline does not fit the CommonV1 specification.'''
        pass

    class InvalidGlobalTimeException(Exception):
        '''Raised if the global time is not an integer.'''
        pass

    # JSON Schema to validate raw input
    # For grammar,
    # see http://json-schema.org/latest/json-schema-validation.html
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
                'type': 'integer'
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

    def __init__(self, raw_common_or_filepath=None):
        '''
        Parameters:
            raw_common_or_filepath:
                Optional. A dict formatted in gazelib/common/v1
                or a string path to a source file.
                Supported source file types:
                - JSON

        Raises:
            ValidationError
        '''

        r = raw_common_or_filepath  # alias

        if r is None:
            # Construct with empty.
            now = int(get_current_posix_time())
            r = {
                'schema': 'gazelib/common/v1',
                'global_posix_time': now,
                'environment': {},
                'timelines': {},
                'streams': {},
                'events': []
            }
        elif isinstance(r, str):
            # Load file
            r = load_json(r)
            CommonV1.validate(r)
        else:
            CommonV1.validate(r)

        self.raw = r

    def __eq__(self, other):
        '''Override '==' operator with deep difference check.'''
        return DeepDiff(self.raw, other.raw) == {}

    # Assertions

    def assert_has_environments(self, env_names):
        '''
        Raises CommonV1.InsufficientDataException if the any of the
        given environments is missing from the container. This is used
        in analysis scripts that require certain environments.
        '''
        if not self.has_environments(env_names):
            required = ', '.join(env_names)
            available = ', '.join(self.get_environment_names())
            msg = 'Environments ' + required + ' are needed but only ' + \
                available + ' are available.'
            raise CommonV1.InsufficientDataException(msg)

    def assert_has_streams(self, stream_names):
        '''
        Raises CommonV1.InsufficientDataException if the any of the
        given streams is missing from the container. This is used
        in analysis scripts that require certain streams.
        '''
        if not self.has_streams(stream_names):
            required = ', '.join(stream_names)
            available = ', '.join(self.get_stream_names())
            msg = 'Streams ' + required + ' are needed but only ' + \
                available + ' are available.'
            raise CommonV1.InsufficientDataException(msg)

    def assert_range_order(self, start, end, start_name, end_name):
        '''
        Raise InvalidRangeException if start larger or equal than end.
        '''
        # Ensure correct order
        if start is not None and end is not None:
            if start >= end:
                msg = (start_name + ' (' + str(start) + ') must be ' +
                       'smaller than ' + end_name + ' (' + str(end) + ')')
                raise CommonV1.InvalidRangeException(msg)

    # Accessors

    def convert_to_global_time(self, relative_time_seconds):
        '''Return global time in seconds (float)'''
        if relative_time_seconds is None:
            return None
        gt = self.raw['global_posix_time']
        return gt + relative_time_seconds

    def convert_to_relative_time(self, global_time_seconds):
        '''Return relative time in seconds (float)'''
        if global_time_seconds is None:
            return None
        gt = self.raw['global_posix_time']
        return global_time_seconds - gt

    def get_environment(self, env_name):
        '''
        Return value of the environment.
        '''
        try:
            return self.raw['environment'][env_name]
        except KeyError:
            str_e = str(env_name)
            msg = 'Environment ' + str_e + ' not found.'
            raise CommonV1.MissingEnvironmentException(msg)

    def get_timeline(self, timeline_name):
        '''
        Return:
            timeline i.e. a list of relative times.

        Raise:
            CommonV1.MissingTimelineException: if name not found.
        '''
        try:
            return self.raw['timelines'][timeline_name]
        except KeyError:
            str_tl = str(timeline_name)
            raise CommonV1.MissingTimelineException('Timeline ' + str_tl +
                                                    ' not found.')

    def get_timeline_mean_interval(self, timeline_name):
        '''
        Return unbiased mean interval in seconds, measured over the timeline.
        '''
        try:
            tl = self.raw['timelines'][timeline_name]
            return arithmetic_mean(deltas(tl))
        except KeyError:
            str_tl = str(timeline_name)
            raise CommonV1.MissingTimelineException('Timeline ' + str_tl +
                                                    ' not found.')

    def get_global_time(self):
        '''
        Return the global reference time as seconds from unix epoch.
        '''
        return self.raw['global_posix_time']

    def get_relative_start_time(self):
        '''
        Find he smallest time in the container as relative time.
        Can be negative.
        '''
        # Min of first elements in timelines
        tl_1st = [timeline[0] for timeline in self.raw['timelines'].values()]
        tl_min = min(tl_1st)

        # Min in range of events
        ev_1st = [ev['range'][0] for ev in self.raw['events']]
        ev_min = min(ev_1st)

        return min(tl_min, ev_min)

    def get_relative_end_time(self):
        '''
        Find the largest time in the container as relative time.
        Can be negative.
        '''
        # Max of last elements in timelines
        tl_last = [timeline[-1] for timeline in self.raw['timelines'].values()]
        tl_max = max(tl_last)

        # Max in range of events
        ev_last = [ev['range'][1] for ev in self.raw['events']]
        ev_max = max(ev_last)

        return max(tl_max, ev_max)

    def get_relative_time_by_index(self, timeline_name, index):
        '''
        Return relative time on the timeline at index.
        '''
        tl = self.get_timeline(timeline_name)
        return tl[index]

    def get_duration(self):
        '''
        Difference in seconds between the smallest and largest time point.
        '''
        return self.get_relative_end_time() - self.get_relative_start_time()

    def get_environment_names(self):
        '''
        Return list of names of provided environments.
        '''
        return list(self.raw['environment'].keys())

    def get_stream_names(self):
        '''
        Return list of names of provided streams.
        '''
        return list(self.raw['streams'].keys())

    def get_stream(self, stream_name):
        '''
        Return: CommonV1 stream dict.
        Raise: CommonV1.MissingStreamException: if name not found.
        '''
        try:
            return self.raw['streams'][stream_name]
        except KeyError:
            str_name = str(stream_name)
            raise CommonV1.MissingStreamException('Stream ' + str_name +
                                                  ' not found.')

    def get_stream_values(self, stream_name):
        '''
        Return: the full list of values of the stream.
        Raise: CommonV1.MissingStreamException: if name not found.
        '''
        return self.get_stream(stream_name)['values']

    def get_stream_timeline_name(self, stream_name):
        '''
        Return: the timeline name associated with the stream.
        Raise: CommonV1.MissingStreamException: if name not found.
        '''
        return self.get_stream(stream_name)['timeline']

    def iter_events_by_tag(self, tag):
        '''
        Yields those events which have the given tag.
        '''
        for event in self.raw['events']:
            if tag in event['tags']:
                yield event

    def has_environments(self, env_names):
        '''
        Test if environments are available.

        Parameter:
            env_names, list of strings

        Return:
            True, if all the given environments are available.
            False, otherwise
        '''
        available_envs = self.get_environment_names()
        return all(env in available_envs for env in env_names)

    def has_streams(self, stream_names):
        '''
        Test if streams are available.

        Parameter:
            stream_names, list of strings

        Return:
            True, if all the given streams are available.
            False, otherwise
        '''
        available_streams = self.get_stream_names()
        return all(st in available_streams for st in stream_names)

    def slice_by_relative_time(self, rel_start_time, rel_end_time=None):
        '''
        Return new CommonV1 object with data only in the time range.
        Does not update global_posix_time because easier implementation.
        '''

        # Ensure correct order
        self.assert_range_order(rel_start_time, rel_end_time,
                                'rel_start_time', 'rel_end_time')

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
            tl = self.get_timeline(tl_name)  # Raises if not found
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

        # Ensure correct order
        self.assert_range_order(start_time, end_time,
                                'start_time', 'end_time')

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

        # Ensure correct order
        self.assert_range_order(start_index, end_index,
                                'start_index', 'end_index')

        timeline = self.get_timeline(timeline_name)

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
        '''DEPRECATED. Use iter_by_tag instead.'''
        return self.iter_by_tag(tag, limit_to)

    def iter_by_tag(self, tag, limit_to=None):
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
        '''
        Add new environment.

        Parameters:
            env_name
                A string, the name of the environment. Use of semantic names
                is recommended.
            env_value
                Any type of JSON-compatible object.
        '''
        # TODO raise error if invalid
        self.raw['environment'][env_name] = env_value

    def add_stream(self, stream_name, timeline_name, values, confidence=None):
        '''
        Add a new sequence of sampled data.

        Parameters:
            stream_name
                A string. It is advisable to use semantic names.
            timeline_name
                The name of the timeline that contains the sampling times of
                the values.
            values
                An iterable of values. The length cannot be larger than
                the length of the timeline.
            confidence
                An optional iterable of confidence values. The confidencies
                must be inclusively within 0.0 and 1.0.
        '''
        if timeline_name not in self.raw['timelines']:
            msg = 'Timeline ' + timeline_name + ' not found.'
            raise CommonV1.MissingTimelineException(msg)

        if type(stream_name) is not str:
            raise CommonV1.InvalidStreamException()

        if not hasattr(values, '__iter__'):
            msg = 'Values must be an iterable.'
            raise CommonV1.InvalidStreamException(msg)
        # Convert to list so length can be checked.
        # The specification also requires the internal representation
        # to be a list.
        values = list(values)

        if len(values) != len(self.raw['timelines'][timeline_name]):
            msg = 'Stream and timeline must have equal length.'
            raise CommonV1.InvalidStreamException(msg)

        if confidence is not None:
            if not hasattr(confidence, '__iter__'):
                msg = 'Confidence must be an iterable or None'
                raise CommonV1.InvalidStreamException(msg)
            # Convert to list so length can be checked.
            # The specification also requires the internal representation
            # to be a list.
            confidence = list(confidence)
            if len(confidence) != len(values):
                msg = 'Confidence length must equal to values'
                raise CommonV1.InvalidStreamException(msg)
            # Ensure values inclusively between 0.0 and 1.0
            if any(map(lambda c: c < 0.0 or c > 1.0, confidence)):
                msg = 'Confidence values must be within [0.0, 1.0]'
                raise CommonV1.InvalidStreamException(msg)

        new_stream = {
            'timeline': timeline_name,
            'values': values,
        }
        if confidence is not None:
            new_stream['confidence'] = confidence

        self.raw['streams'][stream_name] = new_stream

    def add_timeline(self, timeline_name, timeline_values):
        '''
        Add a new timeline.

        Parameters:
            timeline_name
                A string that will be referenced from the streams.
            timeline_values
                An iterable, will be converted to list.
        '''
        if type(timeline_name) is str and hasattr(timeline_values, '__iter__'):
            self.raw['timelines'][timeline_name] = list(timeline_values)
        else:
            raise CommonV1.InvalidTimelineException()

    def add_event(self, tags, start_time, end_time, extra=None):
        '''
        Add new event.

        Parameters:
            tags
                A list of tag strings.
            start_time
                A relative time in seconds. The starting time of the event.
            end_time
                A relative time in seconds. The ending time of the event.
            extra
                An optional place for extra info. Typically a dict.
        '''
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

        Parameter:
            seconds_from_epoch, integer.

        Raise:
            InvalidGlobalTimeException if not integer.
        '''
        if isinstance(seconds_from_epoch, int):
            # Note: what if
            self.raw['global_posix_time'] = seconds_from_epoch
        else:
            raise CommonV1.InvalidGlobalTimeException('Must be integer.')

    # IO

    def save_timeline_as_csv(self, timeline_name, target_file_path,
                             delimiter='\t'):
        '''
        Store timeline and its associated streams in a comma separated values
        format. Note that neither events nor environments are included.
        '''
        # Find timeline
        tl = self.get_timeline(timeline_name)

        # Build the headers in practical order.
        headers = ['gazelib/time/seconds']

        # Find streams on the timeline
        streams = {}
        for stream_name, stream in self.raw['streams'].items():
            if stream['timeline'] == timeline_name:
                streams[stream_name] = stream['values']
                headers.append(stream_name)
                if 'confidence' in stream:
                    conf_name = stream_name + '/confidence'
                    streams[conf_name] = stream['confidence']
                    headers.append(conf_name)

        # Define how to iterate over streams to get rows
        def iterstreams():
            for index in range(len(tl)):
                d = {}
                d['gazelib/time/seconds'] = tl[index]
                for stream_name, stream in streams.items():
                    d[stream_name] = stream[index]
                yield d

        write_dictlist_as_csv(target_file_path, iterstreams(),
                              headers=headers, delimiter=delimiter)

    def save_as_json(self, target_file_path, human_readable=False):
        '''
        Store the content in gazelib/common/v1 in a JSON file.

        Parameters:
            target_file_path
                Absolut or relative file path as string.
            human_readable
                Set True for new lines and indentation. Default to False.
        '''
        if human_readable:
            write_fancy_json(target_file_path, self.raw)
        else:
            write_json(target_file_path, self.raw)
