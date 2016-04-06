# -*- coding: utf-8 -*-


def isNotNone(x):
    return x is not None


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
