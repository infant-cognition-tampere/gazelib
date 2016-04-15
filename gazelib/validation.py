# -*- coding: utf-8 -*-
'''

Format validation.


'''
import numbers
import six  # Python version invariant string types.


class ValidationException(Exception):
    pass


def has_only_keys(dict, keys):
    '''
    Return true if obj has all and only the given keys.
    '''
    dk = dict.keys()
    if len(dk) != len(keys):
        return False
    return all(map(lambda k: k in keys, dk))


def has_keys(dict, keys):
    '''
    Parameter
        dict, dict to examine
        keys, a list of strings
    Return
        true, if all given keys are found from the dict.
        false, otherwise
    '''
    dk = dict.keys()
    return all(map(lambda k: k in dk, keys))


def is_string(s):
    '''Return true if s is string or similar.'''
    return isinstance(s, six.string_types)


def is_list_of_strings(l):
    return (type(l) is list and all(map(lambda x: type(x) is str, l)))


def is_real(r):
    '''Return true if r is real number'''
    return isinstance(r, numbers.Real)


def is_integer(n):
    '''See also http://stackoverflow.com/a/3501408/638546'''
    return isinstance(n, numbers.Integral)
