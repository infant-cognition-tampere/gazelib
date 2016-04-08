# -*- coding: utf-8 -*-


def isNotNone(x):
    return x is not None


def isNotNone2d(x, y):
    return x is not None and y is not None


def get_valid_sublists(l, validator=isNotNone):
    '''
    Return list of lists, where each sublist contains only valid values.
    In other words, the given list is splitted by its invalid values.

    Parameters:
        l:
            A list
        validator:
            A boolean function that returns true if element is valid.
            Defaults to testing if value is not None.

    Example:
        >>> get_valid_sublists([1, 2, None, 3])
        [[1, 2], [3]]
    '''
    sublists = []
    cur_sublist = []

    for x in l:
        if validator(x):
            cur_sublist.append(x)
        else:
            if len(cur_sublist) > 0:
                # End current sublist and start a new one.
                sublists.append(cur_sublist)
                cur_sublist = []

    # If last value was valid, one sublist remains to be added.
    if len(cur_sublist) > 0:
        sublists.append(cur_sublist)

    return sublists


def get_valid_sublists_2d(xs, ys, validator=isNotNone2d):
    '''
    Return list of lists where

    Example result:
      [
        ([1,2,3,...], [0,3,5,...]),
        ([4,6,2,...], [3,0,3,...]),
        ...
      ]
    '''
    sublists = []
    cur_sublist_x = []
    cur_sublist_y = []

    for x, y in zip(xs, ys):
        if validator(x, y):
            cur_sublist_x.append(x)
            cur_sublist_y.append(y)
        else:
            if len(cur_sublist_x) > 0:
                # End current sublist and start a new one
                sublists.append((cur_sublist_x, cur_sublist_y))
                cur_sublist_x = []
                cur_sublist_y = []

    # If last value was valid, one sublist remains to be added.
    if len(cur_sublist_x) > 0:
        sublists.append((cur_sublist_x, cur_sublist_y))

    return sublists
