# -*- coding: utf-8 -*-


class ConversionException(Exception):
    pass


def estimate_sampling_interval(times):
    '''
    Return mean interval in the given list of times.
    Return None if times is empty or contains only one element.
    '''

    n = 0
    dt_sum = 0.0
    prev_t = 0.0
    first = True
    for t in times:
        if first:
            first = False
        else:
            dt_sum += t - prev_t
        prev_t = t
        n += 1

    if n < 2:
        return None

    return dt_sum / (n - 1)


def split_to_ranges_at_change_in_value(gd, value_converter, time_converter):
    '''
    Similar to gazelib.legacy.igazelib.split_at_change_in_value but
    returns also starting and ending times. The start time is equal to
    the end time of the previous range.

    Parameters:
        gd
            gazedata as list of dicts
        value_converter
            A function that converts from raw row to the value
            used for comparison and also in yielded dicts.
            Must raise ValueError if value cannot be converted.
            On ValueError the row will be skipped.
        time_converter
            A function that converts from raw row to times used
            in ranges.
            Must return integer.
            Must raise ValueError if time cannot be converted.
            On ValueError the row will be skipped.

    Yields dicts:
        {
          'start': <integer, start time of range, inclusive>,
          'end': <integer, end time of range, exclusive>,
          'value': <the value of the range>
          'first': <first point in range>
        }
    '''

    # Estimate sample interval (i.e. 1 / sampling rate)
    times = map(time_converter, gd)
    sample_interval = int(round(estimate_sampling_interval(times)))

    num_yields = 0
    cur_time = None
    previous_value = None
    event_to_yield = None
    for index, gazepoint in enumerate(gd):
        try:
            cur_value = value_converter(gazepoint)
            cur_time = time_converter(gazepoint)
            # cur_time must be last because otherwise it would not always
            # point to the time of last valid row. If last rows are
            # invalid, the last event should still have correct time.
        except ValueError:
            # Skip invalid but remember the previous value
            continue

        # Iterate until value differs from the previous
        if cur_value == previous_value:
            continue

        # Assert: different valid value observed

        # If first row, do not store dict but start the first dict.
        if num_yields == 0:
            event_to_yield = {
                'start': cur_time,
                'value': cur_value,
                'first': gazepoint
            }
        else:
            # Range dict finished
            event_to_yield['end'] = cur_time
            yield event_to_yield
            num_yields += 1

            # Start new one
            event_to_yield = {
                'start': cur_time,
                'value': cur_value,
                'first': gazepoint
            }

        previous_value = cur_value

    # Handle the last event
    if event_to_yield is not None:
        event_to_yield['end'] = cur_time + sample_interval
        yield event_to_yield
        num_yields += 1


class ExperimentConfiguration(object):

    def __init__(self, raw_dict):
        self.raw = raw_dict

    def get_trial_configuration(self, trial_config_id):
        '''
        Available trial configuration ids are:
            'calibration_movie', 'calibration_stimuli',
            'SRT1', 'SRT2', 'SRT3', 'SRT4', 'SRT5'
        '''
        raw = next(cf for cf in self.raw if cf['name'] == trial_config_id)
        return TrialConfiguration(raw)


class TrialConfiguration(object):

    def __init__(self, raw_dict):
        self.raw = raw_dict

    def get_image_name(self, index):
        '''
        Retrieves an image name from 'images' list at given index.
        '''
        return self.raw['images'][index]

    def get_aoi_rectangle(self, aoi_index):
        '''
        Returns AoI in gazelib/geom/rectangle format.
        '''
        aoi = self.raw['aois'][aoi_index]
        # Convert to gazelib/geom/rectangle
        rect = [aoi[0], aoi[2], aoi[1], aoi[3]]
        return rect
