
'''

Format validation.


'''

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

def gazelib_common_v1(raw):
    raise ValidationException()
