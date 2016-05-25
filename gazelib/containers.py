# -*- coding: utf-8 -*-
'''
Classes that store the gaze data and can be fed to analysis functions.
'''
from .validation import is_list_of_strings, is_integer, is_string
# from .settings import min_event_slice_overlap_seconds as min_overlap
from .statistics import arithmetic_mean, deltas
from .io import load_json, write_json, write_fancy_json, write_dictlist_as_csv
from time import time as get_current_posix_time
from deepdiff import DeepDiff
from bisect import bisect_left  # binary tree search tool
from jsonschema import validate as validate_jsonschema


def get_current_time_reference():
    '''Get current POSIX time in microseconds'''
    return int(get_current_posix_time() * 10**6)


class CommonV1(object):

    class InvalidRangeException(Exception):
        '''
        Raised if invalid range index pair were given. E.g. start > end
        '''
        pass

    class MissingEnvironmentException(Exception):
        '''Raised if a given environment name cannot be found.'''
        pass

    class MissingTimelineException(Exception):
        '''Raised if a given timeline name cannot be found.'''
        pass

    class MissingStreamException(Exception):
        '''Raised if a given stream name cannot be found.'''
        pass

    class MissingTagException(Exception):
        '''Raised if a given event tag cannot be found'''

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
        '''Raised if container does not provide required data.
        For example if some streams are missing.'''
        pass

    class InvalidTimeException(Exception):
        '''Raised if a time is not an integer.'''
        pass

    class EmptyContainerException(Exception):
        '''
        Raised if there is not enough content for a CommonV1 method.
        For example get_relative_start_time cannot return anything
        if there is no timelines or they are empty.
        '''
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
            'time_reference': {
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
                            'type': 'integer'
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
                            'derived': {
                                'type': 'string'
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
                        'derived': {
                            'type': 'string'
                        },
                        'extra': {}
                    },
                    'required': ['tags', 'range']
                }
            }
        },
        'required': ['schema', 'time_reference', 'environment',
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
            now = get_current_time_reference()
            r = {
                'schema': 'gazelib/common/v1',
                'time_reference': now,
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

    def convert_to_unix_time(self, relative_time_micros):
        '''Return unix time in microseconds (int)'''
        if relative_time_micros is None:
            return None
        tr = self.raw['time_reference']
        return tr + relative_time_micros

    def convert_to_relative_time(self, unix_time_micros):
        '''Return relative time in microseconds (int)'''
        if unix_time_micros is None:
            return None
        gt = self.raw['time_reference']
        return unix_time_micros - gt

    def count_events(self, tag=None):
        '''
        Return integer, number of stored events.
        If the optional tag is given, count only events with the tag.
        '''
        if tag is None:
            return len(self.raw['events'])
        else:
            total = 0
            for ev in self.raw['events']:
                if tag in ev['tags']:
                    total += 1
            return total

    def get_duration(self):
        '''
        Difference in microseconds between the smallest and largest time point.
        '''
        return self.get_relative_end_time() - self.get_relative_start_time()

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

    def get_environment_names(self):
        '''
        DEPRECATED: Use list_environment_names instead
        '''
        return self.list_environment_names()

    def get_event_by_tag(self, tag, index=0):
        '''
        Return event that has the given tag. By default the first occurence
        is returned.

        Raise MissingTagException if no events are found.
        Raise IndexError if tags found but index out of range.
        '''

        # Select event of the index:th tag
        tag_found = False
        i = 0
        for event in self.raw['events']:
            if tag in event['tags']:
                tag_found = True
                if index == i:
                    return event
                i += 1

        # Tag was found but index was too high.
        if tag_found:
            raise IndexError('Index ' + str(index) + ' out of range(' +
                             str(i) + ').')
        else:
            raise CommonV1.MissingTagException('Events with tag ' + str(tag) +
                                               ' not found.')

    def get_relative_start_time(self):
        '''
        Find he smallest time in the container as relative time.
        Can be negative.
        '''

        tls = self.raw['timelines']
        evs = self.raw['events']

        has_timelines = len(tls.keys()) > 0
        has_events = len(evs) > 0
        # Timelines cannot be empty

        if has_timelines:
            # Min of first elements in timelines
            tl_1st = [tl[0] for tl in tls.values()]
            tl_min = min(tl_1st)

        if has_events:
            # Min in range of events
            ev_1st = [ev['range'][0] for ev in evs]
            ev_min = min(ev_1st)

        if has_timelines:
            if has_events:
                return min(tl_min, ev_min)
            else:
                return tl_min
        else:
            if has_events:
                return ev_min
            else:
                raise CommonV1.EmptyContainerException('No time content.')

    def get_relative_end_time(self):
        '''
        Find the largest time in the container as relative time.
        Can be negative.
        '''

        tls = self.raw['timelines']
        evs = self.raw['events']

        has_timelines = len(tls.keys()) > 0
        has_events = len(evs) > 0

        if has_timelines:
            # Max of last elements in timelines
            tl_last = [tl[-1] for tl in tls.values()]
            tl_max = max(tl_last)

        if has_events:
            # Max in range of events
            ev_last = [ev['range'][1] for ev in evs]
            ev_max = max(ev_last)

        if has_timelines:
            if has_events:
                return max(tl_max, ev_max)
            else:
                return tl_max
        else:
            if has_events:
                return ev_max
            else:
                raise CommonV1.EmptyContainerException('No time content.')

    def get_relative_time_by_index(self, timeline_name, index):
        '''
        Return relative time on the timeline at index.
        '''
        tl = self.get_timeline(timeline_name)
        return tl[index]

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

    def get_stream_names(self):
        '''
        DEPRECATED: Use list_stream_names instead
        '''
        return self.list_stream_names()

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
        Return mean interval in microseconds, measured over the timeline.
        '''
        try:
            tl = self.raw['timelines'][timeline_name]
            return arithmetic_mean(deltas(tl))
        except KeyError:
            str_tl = str(timeline_name)
            raise CommonV1.MissingTimelineException('Timeline ' + str_tl +
                                                    ' not found.')

    def get_time_reference(self):
        '''
        Return the time reference as microseconds from unix epoch.
        '''
        return self.raw['time_reference']

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

    def iter_events(self):
        '''
        Iterate over each event. See list_events to get list directly.
        '''
        return iter(self.raw['events'])

    def iter_events_by_tag(self, tag):
        '''
        Yield events that have the tag.
        Raise MissingTagException if no events found.
        '''
        for ev in self.iter_events_by_tags([tag]):
            yield ev

    def iter_events_by_tags(self, tags):
        '''
        Yield events that have at least one of the tags.
        For example, used internally by save_events_as_csv(tags)

        Parameters:
            tags: a list of tags

        If no such events found, iter []
        '''
        num_yields = 0
        stags = set(tags)
        for ev in self.iter_events():
            # Intersection
            sev = set(ev['tags'])
            if len(stags.intersection(sev)) > 0:
                yield ev
                num_yields += 1
        if num_yields == 0:
            return  # Generators allow single return

    def iter_by_tag(self, tag, limit_to=None):
        '''DEPRECATED as too vague. Use iter_slices_by_tag instead.'''
        return self.iter_slices_by_tag(tag, limit_to)

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

        If no such slices found, iter []
        '''
        for index, event in enumerate(self.iter_events_by_tag(tag)):
            range_start = event['range'][0]
            range_end = event['range'][1]
            yield self.slice_by_relative_time(range_start, range_end)
            if limit_to is not None:
                if index + 2 > limit_to:
                    break

    def list_environment_names(self):
        '''Return list of names of provided environments.'''
        return list(self.raw['environment'].keys())

    def list_events(self):
        '''Return full list of events'''
        return self.raw['events']

    def list_stream_names(self):
        '''Return list of names of provided streams.'''
        return list(self.raw['streams'].keys())

    def list_tags(self):
        '''Return list of unique tags in the events. Order is not defined.'''

        tags = {}  # Looping lists is O(n). Searching a key is O(log(n))

        for ev in self.iter_events():
            for tag in ev['tags']:
                if tag not in tags:
                    tags[tag] = True

        return list(tags.keys())

    def slice_by_relative_time(self, rel_start_time, rel_end_time=None):
        '''
        Return new CommonV1 object with data only in the time range.
        Will slice events that are partially outside.
        Will remove empty streams and events that are completely outside.
        Will remove empty timelines
        Does not update time_reference because easier implementation
        and more efficient execution.
        '''

        # Ensure given range is in correct order
        self.assert_range_order(rel_start_time, rel_end_time,
                                'rel_start_time', 'rel_end_time')

        # The new copy of content. Insert sliced values to it.
        # time reference, schema, and environment stay the same.
        slice_raw = {
            'schema': self.raw['schema'],
            'time_reference': self.raw['time_reference'],
            'environment': self.raw['environment'],  # shallow copy!
            'timelines': {},
            'streams': {},
            'events': []
        }

        # Streams first, then events.
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

            # Slice timeline and streams
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

        def copy_event(event):
            '''Return copy. Extra is shallow copied.'''
            ev = {
                'tags': list(event['tags']),
                'range': list(event['range'])
            }
            if 'extra' in event:
                ev['extra'] = event['extra']
            return ev

        # Then events.
        # Slice events that overlap with the time range.
        # Keep events that are inside.
        # Remove events that are outside.
        for event in self.raw['events']:
            ev_start = event['range'][0]
            ev_end = event['range'][1]

            # # A false approach:
            # # Force into the range
            # upper_limit = rel_end_time
            # lower_limit = rel_start_time
            # f_ev_start = max(min(ev_start, upper_limit), lower_limit)
            # f_ev_end = max(min(ev_end, upper_limit), lower_limit)
            # # If event duration 0, it is outside.
            # # This would accidentally remove purposely 0 duration events.
            # # Testing if 0 duration event would be at begin or end
            # # accidentally removes events that needs to be there.

            if rel_end_time is None:
                if rel_start_time < ev_end:
                    # Event overlaps with the slice
                    if ev_start < rel_start_time:
                        # Event only partially overlaps. Copy & modify.
                        nev = copy_event(event)
                        nev['range'][0] = rel_start_time
                    else:
                        # Event inside the slice. Add it.
                        nev = event
                    slice_raw['events'].append(nev)
            else:
                if ev_start < rel_end_time and rel_start_time < ev_end:
                    # Event overlaps with the slice
                    upper_limit = rel_end_time
                    lower_limit = rel_start_time
                    # Limit event range
                    nev_start = max(min(ev_start, upper_limit), lower_limit)
                    nev_end = max(min(ev_end, upper_limit), lower_limit)
                    nev = copy_event(event)
                    nev['range'] = [nev_start, nev_end]
                    # Add the event.
                    slice_raw['events'].append(nev)

        return CommonV1(slice_raw)

    def slice_by_unix_time(self, start_time, end_time=None):
        '''
        Parameters:
            start_time: unix time in microseconds
            end_time: unix time in microseconds

        Return new CommonV1 object with data only from the time range.
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

        Parameters:
            timeline_name: string
            start_index: inclusive
            end_index:

                Optional, exclusive, first element to not be included.
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
        Parameters:
            tag
            index

        Return:
            CommonV1 instance
                that has data only during the tagged event.

        Raise MissingTagException if no events with given tag found.
        Raise IndexError if tag found but index out of range.
        '''
        ev = self.get_event_by_tag(tag, index)
        range_start = ev['range'][0]
        range_end = ev['range'][1]
        return self.slice_by_relative_time(range_start, range_end)

    def slice_first_microseconds(self, n):
        '''
        Parameters:
            n: <integer> microseconds

        Return:
            CommonV1 instance
                that has data only from the first n microseconds, counted
                from the beginning of the slice.
        '''
        range_start = self.get_relative_start_time()
        range_end = range_start + n
        return self.slice_by_relative_time(range_start, range_end)

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

    def add_event(self, tags, start_time, end_time, derived=None, extra=None):
        '''
        Add new event.

        Parameters:
            tags
                A list of tag strings.
            start_time
                A relative time in microseconds. The starting time of event.
            end_time
                A relative time in microseconds. The ending time of event.
            derived
                Optional name of function that was used to derive the event.
            extra
                An optional place for extra info. Typically a dict.
        '''
        if not is_list_of_strings(tags):
            raise CommonV1.InvalidEventException('Invalid tag list')
        if (not is_integer(start_time)) or (not is_integer(end_time)):
            rang = '[' + str(start_time) + ', ' + str(end_time) + ']'
            raise CommonV1.InvalidEventException('Invalid range: ' + rang)
        if start_time > end_time:
            rang = '[' + str(start_time) + ', ' + str(end_time) + ']'
            msg = 'Invalid range order: ' + rang
            raise CommonV1.InvalidEventException(msg)
        new_event = {
            'tags': tags,
            'range': [start_time, end_time],
        }
        if derived is not None:
            if not is_string(derived):
                msg = 'Derived must be a string: ' + str(derived)
                raise CommonV1.InvalidEventException(msg)
            new_event['derived'] = derived
        if extra is not None:
            new_event['extra'] = extra

        self.raw['events'].append(new_event)

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
                An iterable of integer microseconds. Will be converted to list.
        '''
        if type(timeline_name) is str and hasattr(timeline_values, '__iter__'):
            self.raw['timelines'][timeline_name] = list(timeline_values)
        else:
            raise CommonV1.InvalidTimelineException()

    def set_time_reference(self, microseconds_from_epoch):
        '''
        Can be used to anonymize data.

        Parameter:
            microseconds_from_epoch, integer.

        Raise:
            InvalidTimeException if not integer.
        '''
        if isinstance(microseconds_from_epoch, int):
            # Note: what if long
            self.raw['time_reference'] = microseconds_from_epoch
        else:
            raise CommonV1.InvalidTimeException('Must be integer.')

    # IO

    def save_events_as_csv(self, tags, target_file_path, delimiter='\t'):
        '''
        Save CSV file with each event as row and with columns:
            start_time: event start time in unix time
            end_time: event end time in unix time
            <1st tag>: 1 = event has tag, 0 = event does not have this tag
            <2nd tag>:
            ...

        The file includes header row.
        '''
        def iterevents():
            for ev in self.iter_events_by_tags(tags):
                row = {
                    'start_time': ev['range'][0],
                    'end_time': ev['range'][1]
                }
                for tag in tags:
                    if tag in ev['tags']:
                        row[tag] = 1
                    else:
                        row[tag] = 0
                yield row

        # Define order of columns
        headers = ['start_time', 'end_time'] + tags
        write_dictlist_as_csv(target_file_path, iterevents(),
                              headers=headers, delimiter=delimiter)

    def save_timeline_as_csv(self, timeline_name, target_file_path,
                             delimiter='\t'):
        '''
        Store timeline and its associated streams in a comma separated values
        format. Note that neither events nor environments are included.
        '''
        # Find timeline
        tl = self.get_timeline(timeline_name)

        # Build the headers in practical order.
        headers = ['gazelib/time/microseconds']

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
                d['gazelib/time/microseconds'] = tl[index]
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
