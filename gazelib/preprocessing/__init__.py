# -*- coding: utf-8 -*-


class ExtrapolationError(Exception):
    pass


def fill_gaps(l):
    '''
    Given a list of values, extrapolate None values by the last
    known non-None value. If no preceding non-None values were found, copy
    the first known value to those.

    Paremeters:
        l: list of values

    Throw
        ExtrapolationError
            if list does not contains any non-null values

    Return
        list without gaps
    '''
    nl = []  # new, filled list

    if len(l) < 1:
        raise ExtrapolationError('Empty list cannot be extrapolated')

    first_nonnull = None

    # Find first non-nulls
    for p in l:
        if p is not None:
            first_nonnull = p
            break

    if first_nonnull is None:
        # No good values found
        msg = 'No non-null values to fill with: ' + str(first_nonnull)
        raise ExtrapolationError(msg)

    prev_nonnull = first_nonnull

    for p in l:
        if p is None:
            nl.append(prev_nonnull)
        else:
            prev_nonnull = p
            nl.append(p)

    return nl
