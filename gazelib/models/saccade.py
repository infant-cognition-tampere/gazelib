# -*- coding: utf-8 -*-
'''
Find a linear saccade from the data.
'''
from gazelib.containers import CommonV1
from gazelib.preprocessing import fill_gaps, ExtrapolationError
import scipy.signal
import saccademodel


def fit(g):
    '''
    Parameter:
        g: Gaze data as CommonV1 object

    Require streams:
        gazelib/gaze/left_eye_x_relative
        gazelib/gaze/left_eye_y_relative
        gazelib/gaze/right_eye_x_relative
        gazelib/gaze/right_eye_y_relative

    Raise:
        InsufficientDataException: if streams are missing or they are empty.

    Return::

        {
            'type': 'gazelib/gaze/saccade',
            'start_time_relative': <int microseconds>
            'end_time_relative': <int microseconds>
            'mean_squared_error': <float>
        }

    '''
    g.assert_has_streams([
        'gazelib/gaze/left_eye_x_relative',
        'gazelib/gaze/left_eye_y_relative',
        'gazelib/gaze/right_eye_x_relative',
        'gazelib/gaze/right_eye_y_relative'
    ])
    # Timeline names
    l_tl_name = g.get_stream_timeline_name('gazelib/gaze/left_eye_x_relative')
    r_tl_name = g.get_stream_timeline_name('gazelib/gaze/right_eye_x_relative')

    lx = g.raw['streams']['gazelib/gaze/left_eye_x_relative']['values']
    ly = g.raw['streams']['gazelib/gaze/left_eye_y_relative']['values']
    rx = g.raw['streams']['gazelib/gaze/right_eye_x_relative']['values']
    ry = g.raw['streams']['gazelib/gaze/right_eye_y_relative']['values']

    # Forward fill
    try:
        lx_fill = fill_gaps(lx)
        ly_fill = fill_gaps(ly)
        rx_fill = fill_gaps(rx)
        ry_fill = fill_gaps(ry)
    except ExtrapolationError:
        # Only nones or empty
        msg = 'Cannot find saccade from empty data.'
        raise CommonV1.InsufficientDataException(msg)

    # Median filter
    # Required to remove non-Gaussian noise i.e. random outliers
    # Saccademodel handles Gaussian noise.
    lx_filt = scipy.signal.medfilt(lx_fill, 5)
    ly_filt = scipy.signal.medfilt(ly_fill, 5)
    rx_filt = scipy.signal.medfilt(rx_fill, 5)
    ry_filt = scipy.signal.medfilt(ry_fill, 5)

    # Pointlists for saccademodel
    lpl = [[x, y] for x, y in zip(lx_filt, ly_filt)]
    rpl = [[x, y] for x, y in zip(rx_filt, ry_filt)]

    # Results
    try:
        lresults = saccademodel.fit(lpl)
        rresults = saccademodel.fit(rpl)
    except saccademodel.interpolate.InterpolationError:
        msg = 'Cannot find saccade from empty data.'
        raise CommonV1.InsufficientDataException(msg)

    # Pick one with smallest error
    lerr = lresults['mean_squared_error']
    rerr = rresults['mean_squared_error']
    if lerr < rerr:
        results = lresults
        tl_name = l_tl_name
    else:
        results = rresults
        tl_name = r_tl_name

    # Convert measured saccade end and start to times.
    lensource = len(results['source_points'])
    lensaccade = len(results['saccade_points'])

    start_index = max(0, lensource - 1)  # do not let below zero
    end_index = max(0, lensource + lensaccade - 1)  # do not let above length

    start = g.get_relative_time_by_index(tl_name, start_index)
    end = g.get_relative_time_by_index(tl_name, end_index)

    return {
        'type': 'gazelib/gaze/saccade',
        'start_time_relative': start,  # microseconds
        'end_time_relative': end,
        'mean_squared_error': results['mean_squared_error']
    }
