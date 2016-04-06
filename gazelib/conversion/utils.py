# -*- coding: utf-8 -*-


def estimate_sampling_interval(times):
    '''
    Return mean interval in the given list of times.
    '''

    n = 0
    dt_sum = 0
    prev_t = 0
    first = True
    for t in times:
        if first:
            first = False
        else:
            dt_sum += t - prev_t
        prev_t = t
        n += 1

    assert n > 0, 'List of times must not be empty'
    return dt_sum / n


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
            Must raise ValueError if time cannot be converted.
            On ValueError the row will be skipped.

    Yields dicts:
        {
          'start': 123.456,
          'end': 234.567,
          'value': anything
        }
    '''
    # Estimate sample interval (i.e. 1 / sampling rate)
    times = map(time_converter, gd)
    sample_interval = estimate_sampling_interval(times)

    previous_value = None
    current_event = {}
    for index, gazepoint in enumerate(gd):
        try:
            value = value_converter(gazepoint)
        except ValueError:
            # Skip invalid
            continue

        # Iterate until value differs from the previous
        is_last = index == len(gd) - 1
        if value == previous_value:
            if not is_last:
                continue

        # Assert: new value observed or last index
        # Anyway, compute start and end time and store dict.
        prev_range_end_time = time_converter(gazepoint)
        next_range_start_time = prev_range_end_time

        # If first row, do not store dict but start the first dict.
        is_first = index == 0
        if not is_first:
            # Range dict finished
            current_event['end'] = prev_range_end_time
            yield current_event
        # Start building a new range dict
        current_event = {
            'start': next_range_start_time,
            'value': value,
            'first_gazepoint': gazepoint
        }
        # Special handling for the last range dict
        if is_last:
            # Last range dict finished
            current_event['end'] = prev_range_end_time + sample_interval

        previous_value = value


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
