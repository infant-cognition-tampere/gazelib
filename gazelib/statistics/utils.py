# -*- coding: utf-8 -*-
'''
Common statistical tools that do not depend on CommonV1.
'''


def maximum(l):
    '''Maximum of a list. Allows None values. Return None if no valid value.'''
    m = None
    for item in l:
        if item is not None:
            if m is not None:
                if item > m:
                    m = item
            else:
                m = item
    return m


def minimum(l):
    '''Minimum of a list. Allows None values. Return None if no valid value.'''
    m = None
    for item in l:
        if item is not None:
            if m is not None:
                if item < m:
                    m = item
            else:
                m = item
    return m


def arithmetic_mean(l):
    '''Return arithmetic mean of list. Return None if empty list.
    Allows None values and does not take them into consideration.'''
    # Based loosely on http://stackoverflow.com/a/7716358/638546
    summ = 0.0
    count = 0
    for item in l:
        if item is not None:
            summ += item
            count += 1
    return summ / count if count > 0 else None


def weighted_arithmetic_mean(l, w):
    '''
    Parameters:
        l: a list of numerical values. Nones are allowed.
        w: a list of numerical weights. Nones are regarded as zeros.

    Return
        float. None if no non-none weights or values were given.
    '''
    suml = 0.0
    sumw = 0.0
    for item, weight in zip(l, w):
        if item is not None:
            if weight is not None:
                suml += item * weight
                sumw += weight
    return suml / sumw if sumw > 0.0 else None


def deltas(l):
    '''
    Return list of differences between consecutive list items.
    The length of the returned list is one smaller than the given list.
    For an increasing sequence, the deltas are positive.
    For a decreasing sequence, the deltas are negative.
    '''
    if len(l) == 0 or len(l) == 1:
        return []
    diffs = []
    for i in range(len(l) - 1):
        diffs.append(l[i + 1] - l[i])
    return diffs
