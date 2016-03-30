# -*- coding: utf-8 -*-
'''
Find a linear saccade from the data.
'''
from gazelib.statistics import arithmetic_mean
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
            'start_time_relative':
            'end_time_relative':
            'mean_squared_error':
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

    # Convert to times
    llensource = len(lresults['source_points'])
    rlensource = len(rresults['source_points'])
    llensaccade = len(lresults['saccade_points'])
    rlensaccade = len(rresults['saccade_points'])
    lstart = g.get_relative_time_by_index(llensource - 1)
    rstart = g.get_relative_time_by_index(rlensource - 1)
    lend = g.get_relative_time_by_index(llensource + llensaccade - 1)
    rend = g.get_relative_time_by_index(rlensource + rlensaccade - 1)
    mean_start = arithmetic_mean([lstart, rstart])
    mean_end = arithmetic_mean([lend, rend])

    # MSE
    lmse = lresults['mean_squared_error']
    rmse = rresults['mean_squared_error']
    mean_mse = arithmetic_mean([lmse, rmse])

    return {
        'type': 'gazelib/gaze/saccade',
        'start_time_relative': mean_start,
        'end_time_relative': mean_end,
        'mean_squared_error': mean_mse
    }
