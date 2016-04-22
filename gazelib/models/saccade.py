# -*- coding: utf-8 -*-
'''
Find a linear saccade from the data.
'''
from gazelib.statistics import arithmetic_mean, maximum, minimum
from gazelib.containers import CommonV1
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

    Return:
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

    lx = g.raw['streams']['gazelib/gaze/left_eye_x_relative']['values']
    ly = g.raw['streams']['gazelib/gaze/left_eye_y_relative']['values']
    rx = g.raw['streams']['gazelib/gaze/right_eye_x_relative']['values']
    ry = g.raw['streams']['gazelib/gaze/right_eye_y_relative']['values']

    # Pointlists for saccademodel
    lpl = [[x, y] for x, y in zip(lx, ly)]
    rpl = [[x, y] for x, y in zip(rx, ry)]

    # Results
    try:
        lresults = saccademodel.fit(lpl)
        rresults = saccademodel.fit(rpl)
    except saccademodel.interpolate.InterpolationError:
        raise CommonV1.InsufficientDataException('Cannot find saccade from' +
                                                 'empty data.')

    # Get timelines to get times from
    l_tl_name = g.get_stream_timeline_name('gazelib/gaze/left_eye_x_relative')
    r_tl_name = g.get_stream_timeline_name('gazelib/gaze/right_eye_x_relative')

    # Convert to times
    llensource = len(lresults['source_points'])
    rlensource = len(rresults['source_points'])
    llensaccade = len(lresults['saccade_points'])
    rlensaccade = len(rresults['saccade_points'])
    lstart = g.get_relative_time_by_index(l_tl_name, llensource - 1)
    rstart = g.get_relative_time_by_index(r_tl_name, rlensource - 1)
    lend = g.get_relative_time_by_index(l_tl_name,
                                        llensource + llensaccade - 1)
    rend = g.get_relative_time_by_index(r_tl_name,
                                        rlensource + rlensaccade - 1)
    # mean_start = arithmetic_mean([lstart, rstart])
    # mean_end = arithmetic_mean([lend, rend])
    mean_start = minimum([lstart, rstart])
    mean_end = maximum([lend, rend, mean_start])  # TODO hacky

    # MSE
    lmse = lresults['mean_squared_error']
    rmse = rresults['mean_squared_error']
    mean_mse = arithmetic_mean([lmse, rmse])

    return {
        'type': 'gazelib/gaze/saccade',
        'start_time_relative': int(mean_start),  # microseconds
        'end_time_relative': int(mean_end),
        'mean_squared_error': mean_mse
    }
